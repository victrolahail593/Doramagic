#!/usr/bin/env python3
"""Community Signals — 从 GitHub 采集社区信号，用于 UNSAID 提取。

用法：
    python3 community_signals.py "owner/repo" --output /tmp/community.json

输出：
    - 高频问题类型
    - 高评论 issues
    - "won't fix"/"by design" 回复
    - bug 标签分布
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def fetch_issues(owner: str, repo: str, per_page: int = 30) -> list[dict]:
    """获取 GitHub issues。"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&sort=comments&per_page={per_page}"
    req = Request(url, headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Doramagic/1.0"
    })

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        print(f"GitHub API error: {e.code}", file=sys.stderr)
        return []

    # 过滤掉 PR
    return [i for i in data if "pull_request" not in i]


def analyze_issues(issues: list[dict]) -> dict:
    """分析 issues 提取社区信号。"""

    # 高评论 issues（社区强烈感受）
    high_comment_issues = [
        {
            "number": i["number"],
            "title": i["title"],
            "comments": i["comments"],
            "state": i["state"],
            "labels": [l["name"] for l in i.get("labels", [])],
            "url": i["html_url"]
        }
        for i in issues if i["comments"] >= 10
    ]

    # 高频问题类型
    problem_keywords = ["error", "fail", "bug", "crash", "broken", "doesn't work", "can't", "unable"]
    problem_issues = []
    for i in issues:
        title_lower = i["title"].lower()
        if any(kw in title_lower for kw in problem_keywords):
            problem_issues.append({
                "number": i["number"],
                "title": i["title"],
                "type": "problem"
            })

    # 标签分布
    all_labels = []
    for i in issues:
        all_labels.extend([l["name"] for l in i.get("labels", [])])

    label_counts = Counter(all_labels)
    bug_labels = [l for l, c in label_counts.most_common(10)
                  if any(kw in l.lower() for kw in ["bug", "error", "fix", "issue"])]

    # "won't fix"/"by design" 回复（隐含 WHY）
    boundary_issues = []
    boundary_keywords = ["won't fix", "wontfix", "by design", "as expected", "working as intended",
                         "not a bug", "declined", "invalid"]
    for i in issues:
        labels_lower = [l["name"].lower() for l in i.get("labels", [])]
        if any(kw in " ".join(labels_lower) for kw in boundary_keywords):
            boundary_issues.append({
                "number": i["number"],
                "title": i["title"],
                "labels": [l["name"] for l in i.get("labels", [])],
                "why_hint": "Maintenance boundary declaration"
            })

    # 计算支持请求比例
    support_keywords = ["how to", "how do i", "help", "question", "usage"]
    support_count = sum(1 for i in issues
                       if any(kw in i["title"].lower() for kw in support_keywords))
    support_ratio = support_count / len(issues) if issues else 0

    # 异常场景占比
    exception_keywords = ["edge case", "rare", "unusual", "specific", "corner case"]
    exception_count = sum(1 for i in high_comment_issues
                         if any(kw in i["title"].lower() for kw in exception_keywords))
    exception_ratio = exception_count / len(high_comment_issues) if high_comment_issues else 0

    return {
        "total_issues": len(issues),
        "high_comment_issues": high_comment_issues[:10],
        "problem_issues": problem_issues[:15],
        "bug_labels": bug_labels,
        "boundary_issues": boundary_issues[:10],
        "metrics": {
            "support_ratio": round(support_ratio, 2),
            "exception_ratio": round(exception_ratio, 2),
            "high_comment_count": len(high_comment_issues)
        }
    }


def detect_dark_trap_signals(analysis: dict) -> list[dict]:
    """检测暗雷信号。"""
    signals = []

    metrics = analysis.get("metrics", {})

    # Exception Dominance Ratio
    if metrics.get("exception_ratio", 0) > 0.6:
        signals.append({
            "indicator": "Exception Dominance Ratio",
            "value": metrics["exception_ratio"],
            "risk": "HIGH",
            "description": "高互动线程集中在异常场景，可能不适合普通用户"
        })

    # Support-Desk Share
    if metrics.get("support_ratio", 0) > 0.7:
        signals.append({
            "indicator": "Support-Desk Share",
            "value": metrics["support_ratio"],
            "risk": "MEDIUM",
            "description": "大量求助帖子，项目使用门槛高"
        })

    return signals


def main():
    parser = argparse.ArgumentParser(description="Collect community signals from GitHub")
    parser.add_argument("repo", help="Repository in format owner/repo")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file")
    parser.add_argument("--per-page", type=int, default=30, help="Issues to fetch")

    args = parser.parse_args()

    # 解析 owner/repo
    parts = args.repo.split("/")
    if len(parts) != 2:
        print(f"Error: Invalid repo format. Use 'owner/repo'", file=sys.stderr)
        sys.exit(1)

    owner, repo = parts

    print(f"Fetching issues for {owner}/{repo}...")

    # 获取 issues
    issues = fetch_issues(owner, repo, args.per_page)
    if not issues:
        print("No issues found or API error", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(issues)} issues")

    # 分析
    analysis = analyze_issues(issues)

    # 暗雷检测
    dark_signals = detect_dark_trap_signals(analysis)
    analysis["dark_trap_signals"] = dark_signals

    # 写入输出
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nCommunity signals saved to {args.output}")
    print(f"  High comment issues: {len(analysis['high_comment_issues'])}")
    print(f"  Problem issues: {len(analysis['problem_issues'])}")
    print(f"  Boundary issues: {len(analysis['boundary_issues'])}")
    print(f"  Dark trap signals: {len(dark_signals)}")

    if dark_signals:
        print("\nDark trap warnings:")
        for s in dark_signals:
            print(f"  ⚠️ [{s['risk']}] {s['indicator']}: {s['description']}")


if __name__ == "__main__":
    main()