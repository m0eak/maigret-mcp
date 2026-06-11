"""MCP server exposing safe Maigret search tools."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .runner import default_reports_dir, list_report_files, run_maigret, run_stats

mcp = FastMCP("maigret-mcp")

ReportFormat = Literal["txt", "html", "pdf", "csv", "json"]


@mcp.tool()
def search_username(
    username: str,
    report_formats: list[ReportFormat] | None = None,
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
) -> dict:
    """Search one username with Maigret and generate reports."""
    result = run_maigret(
        [username],
        report_formats=report_formats or ["txt", "html", "json"],
        top_sites=top_sites,
        all_sites=all_sites,
        timeout=timeout,
        retries=retries,
        tags=tags,
        exclude_tags=exclude_tags,
        sites=sites,
        with_domains=with_domains,
        no_recursion=no_recursion,
        no_extracting=no_extracting,
        print_errors=print_errors,
        proxy=proxy,
    )
    return {
        "usernames": result.usernames,
        "return_code": result.return_code,
        "reports": result.reports,
        "parsed_results": result.parsed_results,
        "stdout_tail": result.stdout,
        "stderr_tail": result.stderr,
    }


@mcp.tool()
def search_usernames(
    usernames: list[str],
    report_formats: list[ReportFormat] | None = None,
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
) -> dict:
    """Search multiple usernames with Maigret and generate reports."""
    result = run_maigret(
        usernames,
        report_formats=report_formats or ["txt", "html", "json"],
        top_sites=top_sites,
        all_sites=all_sites,
        timeout=timeout,
        retries=retries,
        tags=tags,
        exclude_tags=exclude_tags,
        sites=sites,
        with_domains=with_domains,
        no_recursion=no_recursion,
        no_extracting=no_extracting,
        print_errors=print_errors,
        proxy=proxy,
    )
    return {
        "usernames": result.usernames,
        "return_code": result.return_code,
        "reports": result.reports,
        "parsed_results": result.parsed_results,
        "stdout_tail": result.stdout,
        "stderr_tail": result.stderr,
    }


@mcp.tool()
def maigret_stats() -> dict:
    """Return Maigret database statistics."""
    return run_stats()


@mcp.tool()
def list_reports() -> dict:
    """List generated report files in the configured reports directory."""
    reports_dir = default_reports_dir()
    reports_dir.mkdir(parents=True, exist_ok=True)
    return {
        "reports_dir": str(reports_dir),
        "reports": list_report_files(reports_dir),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
