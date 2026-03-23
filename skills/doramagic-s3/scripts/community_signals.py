#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
import argparse
from pathlib import Path

def fetch_issues(repo_full_name, state="all", max_results=30):
    url = f"https://api.github.com/repos/{repo_full_name}/issues?state={state}&per_page={max_results}&sort=comments&direction=desc"
    req = urllib.request.Request(url, headers={"User-Agent": "Doramagic-Agent", "Accept": "application/vnd.github.v3+json"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"Failed to fetch issues for {repo_full_name}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Full repository name (e.g., owner/repo)")
    parser.add_argument("--output", help="Output JSON file", required=True)
    args = parser.parse_args()

    issues = fetch_issues(args.repo)
    
    signals = []
    for issue in issues:
        signals.append({
            "number": issue.get("number"),
            "title": issue.get("title"),
            "state": issue.get("state"),
            "comments": issue.get("comments"),
            "labels": [lbl.get("name") for lbl in issue.get("labels", [])],
            "is_pull_request": "pull_request" in issue
        })
    
    with open(args.output, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"Community signals saved to {args.output}")

if __name__ == "__main__":
    main()
