#!/usr/bin/env python3
"""Collect community signals and quick DSD metrics for Doramagic S2."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

USER_AGENT = "Doramagic-S2/1.0"
MAX_ISSUES = 50
TOP_COMMENTED = 8

HIDDEN_CONTEXT_PATTERNS = [
    re.compile(r"\b(internal|offline|slack|discord|dm me|private chat|private discussion)\b", re.I),
]
BOUNDARY_PATTERNS = [
    re.compile(r"\b(won't fix|wont fix|by design|not planned|out of scope|won't implement)\b", re.I),
]
TEMPORAL_CONFLICT_PATTERNS = [
    re.compile(r"\b(rewrite|overhaul|migration|migrate|breaking change|deprecated|deprecation)\b", re.I),
]
SUPPORT_DESK_PATTERNS = [
    re.compile(r"\b(how do i|how to|unable to|help|support|question|usage)\b", re.I),
]
EXCEPTION_PATTERNS = [
    re.compile(r"\b(bug|fail|failing|error|wrong|broken|exception|crash|security|vulnerability)\b", re.I),
]

TOPIC_RULES = {
    "import-parser": ["import", "parser", "parse", "format", "step", "json"],
    "permissions-sharing": ["permission", "public", "private", "household", "group", "share"],
    "auth-login": ["login", "auth", "oidc", "token", "password", "proxy"],
    "migration-upgrade": ["migration", "upgrade", "rewrite", "deprecated", "version"],
    "sync-storage": ["sync", "storage", "db", "sqlite", "postgres", "backup", "seed"],
    "ui-ux": ["ui", "button", "redirect", "sort", "search", "locale"],
}


def _extract_github_slug(repo_url: str) -> str | None:
    match = re.search(r"github\.com[:/]([^/]+/[^/.]+)", repo_url)
    return match.group(1) if match else None


def _github_api_get(url: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_issues(slug: str) -> list[dict[str, Any]]:
    url = (
        "https://api.github.com/repos/{0}/issues?state=all&sort=comments"
        "&direction=desc&per_page={1}"
    ).format(slug, MAX_ISSUES)
    data = _github_api_get(url)
    if not isinstance(data, list):
        return []
    return [item for item in data if "pull_request" not in item]


def _classify_issue(issue: dict[str, Any]) -> str:
    labels = {label.get("name", "").lower() for label in issue.get("labels", [])}
    title = (issue.get("title") or "").lower()
    if "bug" in labels or any("bug" in label for label in labels):
        return "bug"
    if "question" in labels or "support" in labels:
        return "question"
    if "enhancement" in labels or "feature" in labels:
        return "feature"
    if any(pattern.search(title) for pattern in SUPPORT_DESK_PATTERNS):
        return "question"
    if any(pattern.search(title) for pattern in EXCEPTION_PATTERNS):
        return "bug"
    return "unknown"


def _reactions_total(issue: dict[str, Any]) -> int:
    reactions = issue.get("reactions", {}) or {}
    if "total_count" in reactions:
        return int(reactions["total_count"])
    total = 0
    for key, value in reactions.items():
        if isinstance(value, int):
            total += value
    return total


def _topic_hits(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    topic_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        haystack = "{0} {1}".format(issue.get("title", ""), issue.get("body", "") or "").lower()
        for topic, keywords in TOPIC_RULES.items():
            if any(keyword in haystack for keyword in keywords):
                topic_map[topic].append(issue)
    results = []
    for topic, matched in topic_map.items():
        if len(matched) >= 1:
            results.append(
                {
                    "topic": topic,
                    "count": len(matched),
                    "issue_numbers": [item["number"] for item in matched[:8]],
                }
            )
    results.sort(key=lambda item: (-item["count"], item["topic"]))
    return results


def _boundary_signals(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    for issue in issues:
        body = issue.get("body") or ""
        title = issue.get("title") or ""
        text = "{0}\n{1}".format(title, body)
        if any(pattern.search(text) for pattern in BOUNDARY_PATTERNS):
            matches.append(
                {
                    "number": issue["number"],
                    "title": title,
                    "url": issue.get("html_url", ""),
                    "kind": _classify_issue(issue),
                }
            )
    return matches[:10]


def _hidden_context_count(issues: list[dict[str, Any]]) -> int:
    count = 0
    for issue in issues:
        text = "{0}\n{1}".format(issue.get("title") or "", issue.get("body") or "")
        if any(pattern.search(text) for pattern in HIDDEN_CONTEXT_PATTERNS):
            count += 1
    return count


def _temporal_conflicts(repo_path: Path, issues: list[dict[str, Any]]) -> int:
    hits = 0
    for issue in issues:
        title = issue.get("title") or ""
        if any(pattern.search(title) for pattern in TEMPORAL_CONFLICT_PATTERNS):
            hits += 1

    for name in ["CHANGELOG.md", "CHANGELOG", "CHANGES.md", "HISTORY.md", "RELEASES.md"]:
        path = repo_path / name
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in TEMPORAL_CONFLICT_PATTERNS:
            hits += len(pattern.findall(text))
    return hits


def _dsd_metrics(issues: list[dict[str, Any]], repo_path: Path) -> dict[str, float]:
    total = max(len(issues), 1)
    support_like = sum(1 for issue in issues if _classify_issue(issue) == "question")

    top_issues = sorted(
        issues,
        key=lambda issue: (int(issue.get("comments", 0)), _reactions_total(issue)),
        reverse=True,
    )[:10]
    if top_issues:
        exception_like = sum(1 for issue in top_issues if _classify_issue(issue) == "bug")
        exception_ratio = round(exception_like / len(top_issues), 4)
    else:
        exception_ratio = 0.0

    hidden_context = _hidden_context_count(issues)
    public_context_completeness = round(1.0 - (hidden_context / total), 4)

    temporal_hits = _temporal_conflicts(repo_path, issues)
    temporal_conflict_score = round(min(1.0, temporal_hits / 6), 4)

    return {
        "support_desk_share": round(support_like / total, 4),
        "exception_dominance_ratio": exception_ratio,
        "public_context_completeness": public_context_completeness,
        "temporal_conflict_score": temporal_conflict_score,
    }


def _markdown_report(
    repo_slug: str,
    issues: list[dict[str, Any]],
    metrics: dict[str, float],
    topics: list[dict[str, Any]],
    boundaries: list[dict[str, Any]],
) -> str:
    counts = Counter(_classify_issue(issue) for issue in issues)
    lines = [
        "# Community Signals",
        "",
        "Repo: {0}".format(repo_slug),
        "",
        "## Counts",
        "- Total issues analyzed: {0}".format(len(issues)),
        "- Bug-like issues: {0}".format(counts.get("bug", 0)),
        "- Support/question issues: {0}".format(counts.get("question", 0)),
        "- Feature-like issues: {0}".format(counts.get("feature", 0)),
        "",
        "## DSD Metrics",
        "- support_desk_share: {0}".format(metrics["support_desk_share"]),
        "- exception_dominance_ratio: {0}".format(metrics["exception_dominance_ratio"]),
        "- public_context_completeness: {0}".format(metrics["public_context_completeness"]),
        "- temporal_conflict_score: {0}".format(metrics["temporal_conflict_score"]),
        "",
        "## High Frequency Topics",
    ]
    if topics:
        for item in topics[:8]:
            lines.append(
                "- {0}: {1} issue(s) -> {2}".format(
                    item["topic"],
                    item["count"],
                    ", ".join("#{0}".format(num) for num in item["issue_numbers"]),
                )
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Boundary Signals"])
    if boundaries:
        for item in boundaries:
            lines.append("- #{0} {1} ({2})".format(item["number"], item["title"], item["kind"]))
    else:
        lines.append("- none")

    lines.extend(["", "## Top Commented Issues"])
    top_issues = sorted(
        issues,
        key=lambda issue: (int(issue.get("comments", 0)), _reactions_total(issue)),
        reverse=True,
    )[:TOP_COMMENTED]
    if top_issues:
        for issue in top_issues:
            lines.append(
                "- #{0} {1} | comments={2} | reactions={3}".format(
                    issue["number"],
                    issue.get("title", ""),
                    issue.get("comments", 0),
                    _reactions_total(issue),
                )
            )
    else:
        lines.append("- none")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect GitHub community signals for Doramagic S2")
    parser.add_argument("--repo-url", required=True, help="GitHub repository URL")
    parser.add_argument("--repo-path", required=True, help="Local extracted repository path")
    parser.add_argument("--output-json", required=True, help="Structured JSON output path")
    parser.add_argument("--output-md", required=True, help="Markdown summary output path")
    args = parser.parse_args()

    repo_slug = _extract_github_slug(args.repo_url)
    if not repo_slug:
        print("unsupported repo url: {0}".format(args.repo_url), file=sys.stderr)
        return 1

    repo_path = Path(args.repo_path).expanduser().resolve()
    try:
        issues = _fetch_issues(repo_slug)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        print("GitHub API failed: {0}".format(exc), file=sys.stderr)
        return 1

    metrics = _dsd_metrics(issues, repo_path)
    topics = _topic_hits(issues)
    boundaries = _boundary_signals(issues)

    counts = Counter(_classify_issue(issue) for issue in issues)
    top_commented = []
    for issue in sorted(
        issues,
        key=lambda item: (int(item.get("comments", 0)), _reactions_total(item)),
        reverse=True,
    )[:TOP_COMMENTED]:
        top_commented.append(
            {
                "number": issue["number"],
                "title": issue.get("title", ""),
                "url": issue.get("html_url", ""),
                "comments": int(issue.get("comments", 0)),
                "reactions": _reactions_total(issue),
                "kind": _classify_issue(issue),
            }
        )

    payload = {
        "schema_version": "dm.s2.community-signals.v1",
        "repo_slug": repo_slug,
        "repo_url": args.repo_url,
        "total_issues": len(issues),
        "bug_label_distribution": dict(counts),
        "top_commented_issues": top_commented,
        "high_frequency_topics": topics,
        "boundary_signals": boundaries,
        "dsd_metrics": metrics,
    }

    output_json = Path(args.output_json).expanduser().resolve()
    output_md = Path(args.output_md).expanduser().resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_md.write_text(_markdown_report(repo_slug, issues, metrics, topics, boundaries), encoding="utf-8")

    print("community_json={0}".format(output_json))
    print("community_md={0}".format(output_md))
    print("issues={0}".format(len(issues)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
