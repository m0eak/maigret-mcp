"""Safe Maigret CLI runner for the MCP server."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

ReportFormat = Literal["txt", "html", "pdf", "csv", "json"]

REPORT_FORMAT_FLAGS: dict[str, list[str]] = {
    "txt": ["-T"],
    "html": ["-H"],
    "pdf": ["-P"],
    "csv": ["-C"],
    "json": ["-J", "simple"],
}

SAFE_USERNAME_RE = re.compile(r"^[^\x00\r\n]{1,128}$")
SAFE_SITE_RE = re.compile(r"^[A-Za-z0-9_.: @+\-]{1,80}$")
SAFE_TAGS_RE = re.compile(r"^[A-Za-z0-9_,+\-]{1,300}$")


@dataclass(slots=True)
class MaigretRunResult:
    usernames: list[str]
    return_code: int
    stdout: str
    stderr: str
    reports: list[str]
    parsed_results: dict[str, list[str]]


def default_reports_dir() -> Path:
    return Path(os.environ.get("MAIGRET_MCP_REPORTS_DIR", "/app/reports")).resolve()


def validate_username(username: str) -> str:
    username = username.strip()
    if not SAFE_USERNAME_RE.match(username):
        raise ValueError("username must be 1-128 chars and must not contain control characters")
    return username


def validate_usernames(usernames: Iterable[str]) -> list[str]:
    values = [validate_username(u) for u in usernames]
    if not values:
        raise ValueError("at least one username is required")
    if len(values) > 20:
        raise ValueError("at most 20 usernames are allowed per run")
    return values


def validate_reports_dir(path: Path | None) -> Path:
    base = default_reports_dir()
    target = (path or base).resolve()
    if target != base and base not in target.parents:
        raise ValueError("reports_dir must be inside the configured reports directory")
    target.mkdir(parents=True, exist_ok=True)
    return target


def build_maigret_command(
    usernames: list[str],
    *,
    report_formats: list[ReportFormat],
    reports_dir: Path,
    top_sites: int = 500,
    all_sites: bool = False,
    timeout: int = 30,
    retries: int = 1,
    tags: str | None = None,
    exclude_tags: str | None = None,
    sites: list[str] | None = None,
    with_domains: bool = False,
    no_recursion: bool = False,
    no_extracting: bool = False,
    print_errors: bool = False,
    proxy: str | None = None,
) -> list[str]:
    if not 1 <= top_sites <= 3155:
        raise ValueError("top_sites must be between 1 and 3155")
    if not 1 <= timeout <= 180:
        raise ValueError("timeout must be between 1 and 180 seconds")
    if not 0 <= retries <= 5:
        raise ValueError("retries must be between 0 and 5")

    formats = report_formats or ["txt", "html", "json"]
    for fmt in formats:
        if fmt not in REPORT_FORMAT_FLAGS:
            raise ValueError(f"unsupported report format: {fmt}")

    cmd = [sys.executable, "-m", "maigret", *usernames]

    if all_sites:
        cmd.append("--all-sites")
    else:
        cmd.extend(["--top-sites", str(top_sites)])

    cmd.extend(["--timeout", str(timeout), "--retries", str(retries)])
    cmd.extend(["--folderoutput", str(reports_dir)])
    cmd.extend(["--no-color", "--no-progressbar"])

    if tags:
        if not SAFE_TAGS_RE.match(tags):
            raise ValueError("tags contains unsupported characters")
        cmd.extend(["--tags", tags])

    if exclude_tags:
        if not SAFE_TAGS_RE.match(exclude_tags):
            raise ValueError("exclude_tags contains unsupported characters")
        cmd.extend(["--exclude-tags", exclude_tags])

    for site in sites or []:
        if not SAFE_SITE_RE.match(site):
            raise ValueError(f"site contains unsupported characters: {site!r}")
        cmd.extend(["--site", site])

    if with_domains:
        cmd.append("--with-domains")
    if no_recursion:
        cmd.append("--no-recursion")
    if no_extracting:
        cmd.append("--no-extracting")
    if print_errors:
        cmd.append("--print-errors")

    if proxy:
        if not proxy.startswith(("http://", "https://", "socks4://", "socks5://")):
            raise ValueError("proxy must start with http://, https://, socks4:// or socks5://")
        # Proxy credentials should be passed at runtime only. They are never written to repo files.
        cmd.extend(["--proxy", proxy])

    for fmt in formats:
        cmd.extend(REPORT_FORMAT_FLAGS[fmt])

    return cmd


def list_report_files(reports_dir: Path) -> list[str]:
    if not reports_dir.exists():
        return []
    return sorted(
        str(path)
        for path in reports_dir.iterdir()
        if path.is_file() and path.name != ".gitkeep"
    )


def parse_txt_reports(reports_dir: Path) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for path in reports_dir.glob("report_*.txt"):
        urls: list[str] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith(("http://", "https://")):
                urls.append(line)
        parsed[path.stem.removeprefix("report_")] = urls
    return parsed


def run_maigret(
    usernames: Iterable[str],
    *,
    report_formats: list[ReportFormat] | None = None,
    reports_dir: Path | None = None,
    process_timeout: int = 900,
    **kwargs,
) -> MaigretRunResult:
    safe_usernames = validate_usernames(usernames)
    safe_reports_dir = validate_reports_dir(reports_dir)
    before = set(list_report_files(safe_reports_dir))

    cmd = build_maigret_command(
        safe_usernames,
        report_formats=report_formats or ["txt", "html", "json"],
        reports_dir=safe_reports_dir,
        **kwargs,
    )

    completed = subprocess.run(
        cmd,
        cwd=str(safe_reports_dir),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=process_timeout,
        check=False,
    )

    after = set(list_report_files(safe_reports_dir))
    new_reports = sorted(after - before)

    return MaigretRunResult(
        usernames=safe_usernames,
        return_code=completed.returncode,
        stdout=completed.stdout[-12000:],
        stderr=completed.stderr[-12000:],
        reports=new_reports,
        parsed_results=parse_txt_reports(safe_reports_dir),
    )


def run_stats(process_timeout: int = 120) -> dict[str, str | int]:
    completed = subprocess.run(
        [sys.executable, "-m", "maigret", "--stats", "--no-color"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=process_timeout,
        check=False,
    )
    return {
        "return_code": completed.returncode,
        "stdout": completed.stdout[-12000:],
        "stderr": completed.stderr[-12000:],
    }
