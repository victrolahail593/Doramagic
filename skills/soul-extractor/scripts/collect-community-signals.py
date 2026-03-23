#!/usr/bin/env python3
"""
Soul Extractor: Collect community signals from GitHub + local sources.
Usage: python3 collect-community-signals.py --repo-url <url> --repo-path <path> --output <file>

Synthesizes three research inputs:
- Codex: sort=comments + local scoring, security advisories, git log, PR filtering, ≤20KB
- Gemini: CHANGELOG P0, severity by reactions, structured format for weak models
- Superpowers: context is a public good, fail gracefully, never block main pipeline
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from math import log1p
from datetime import datetime, timezone


# --- Configuration ---
MAX_ISSUES = 50
TOP_SIGNALS = 12
MAX_OUTPUT_BYTES = 20_000
CONNECT_TIMEOUT = 10
REQUEST_TIMEOUT = 15


def detect_provider(repo_url):
    if not repo_url:
        return "local"
    if "github.com" in repo_url:
        return "github"
    if "gitlab.com" in repo_url:
        return "gitlab"
    if "gitee.com" in repo_url:
        return "gitee"
    return "other"


def extract_github_slug(repo_url):
    """Extract owner/repo from GitHub URL."""
    match = re.search(r'github\.com[:/]([^/]+/[^/.]+)', repo_url)
    return match.group(1) if match else None


# --- GitHub API ---

def github_api_get(endpoint, token=None):
    """Call GitHub REST API with optional auth. Returns parsed JSON or None."""
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SoulExtractor/0.6",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"  [warn] GitHub API failed: {endpoint} -> {e}", file=sys.stderr)
        return None


def fetch_github_issues(slug, token=None):
    """Fetch issues sorted by comments (official sort field), filter out PRs."""
    data = github_api_get(
        f"/repos/{slug}/issues?state=all&sort=comments&direction=desc&per_page={MAX_ISSUES}",
        token=token
    )
    if not data or not isinstance(data, list):
        return []
    # Filter out pull requests (GitHub issues API mixes them in)
    return [i for i in data if "pull_request" not in i]


def fetch_security_advisories(slug, token=None):
    """Fetch published security advisories."""
    data = github_api_get(
        f"/repos/{slug}/security-advisories?state=published&per_page=10",
        token=token
    )
    if not data or not isinstance(data, list):
        return []
    return data


# --- Local signals ---

def collect_changelog_signals(repo_path):
    """Extract breaking changes from CHANGELOG, grouped by version blocks."""
    signals = []
    changelog_file = None
    for name in ["CHANGELOG.md", "CHANGELOG", "CHANGELOG.rst", "CHANGES.md",
                  "CHANGES", "HISTORY.md", "HISTORY.rst", "RELEASES.md"]:
        path = os.path.join(repo_path, name)
        if os.path.isfile(path):
            changelog_file = path
            break

    if not changelog_file:
        return signals

    try:
        with open(changelog_file, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return signals

    # Split by version headers
    version_re = re.compile(r'^(#{1,3}\s*)?(\[?v?\d+\.\d+(?:\.\d+)?[^\]]*\]?)(?:\s*[-–]\s*\d{4}-\d{2}-\d{2})?',
                            re.MULTILINE)
    blocks = []
    positions = [(m.start(), m.group()) for m in version_re.finditer(content)]

    for idx, (pos, header) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(content)
        block_text = content[pos:end]

        # Check for breaking/migration/deprecation signals
        keywords = re.findall(
            r'(?i)(break|deprecat|remov|renam|drop|migration|upgrade|incompatible|security)',
            block_text
        )
        if keywords:
            # Extract version number
            ver_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', header)
            version = ver_match.group(1) if ver_match else header.strip()

            # Extract relevant lines (not the entire block)
            relevant = []
            for line in block_text.split('\n'):
                if re.search(r'(?i)(break|deprecat|remov|renam|drop|migration|incompatible|security)', line):
                    relevant.append(line.strip())

            if relevant:
                signals.append({
                    "source": "changelog",
                    "kind": "breaking_change",
                    "version": version,
                    "title": f"Breaking changes in v{version}",
                    "evidence": relevant[:5],  # Max 5 lines per version
                    "keyword_count": len(keywords),
                })

    return signals[:10]  # Max 10 version blocks


def collect_readme_faq(repo_path):
    """Extract FAQ/Troubleshooting/Migration sections from README."""
    signals = []
    readme_file = None
    for name in ["README.md", "README.rst", "README"]:
        path = os.path.join(repo_path, name)
        if os.path.isfile(path):
            readme_file = path
            break

    if not readme_file:
        return signals

    try:
        with open(readme_file, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return signals

    # Find relevant sections
    section_re = re.compile(
        r'^(#{1,3})\s+.*?(FAQ|Troubleshoot|Common|Gotcha|Caveat|Warning|Known.Issue|Pitfall|Migration|Upgrade)',
        re.MULTILINE | re.IGNORECASE
    )
    for m in section_re.finditer(content):
        level = len(m.group(1))
        start = m.start()
        # Find end: next heading of same or higher level
        end_re = re.compile(r'^#{1,' + str(level) + r'}\s', re.MULTILINE)
        end_match = end_re.search(content, m.end())
        end = end_match.start() if end_match else min(start + 2000, len(content))

        section_text = content[start:end].strip()
        if len(section_text) > 50:
            signals.append({
                "source": "readme",
                "kind": "faq",
                "title": m.group().strip().lstrip('#').strip(),
                "content": section_text[:800],
            })

    return signals[:5]


def collect_gitlog_signals(repo_path):
    """Extract fix/bug/regression commits from git log."""
    signals = []
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--no-merges", "--date=short",
             "--pretty=format:%h\t%ad\t%s", "-n", "200"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return signals
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return signals

    fix_re = re.compile(r'(?i)(fix|bug|regress|workaround|breaking|deprecat|security)')
    fixes = []
    for line in result.stdout.strip().split('\n'):
        if fix_re.search(line):
            parts = line.split('\t', 2)
            if len(parts) == 3:
                fixes.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "message": parts[2],
                })

    if fixes:
        signals.append({
            "source": "git_log",
            "kind": "fix_commits",
            "title": f"Recent fix/bug commits ({len(fixes)} found)",
            "evidence": [f"{f['date']} {f['hash']} {f['message']}" for f in fixes[:15]],
        })

    return signals


# --- Issue classification and scoring ---

def classify_issue(issue):
    """Classify issue as bug/question/feature/unknown."""
    labels = {label['name'].lower() for label in issue.get('labels', [])}
    title = (issue.get('title') or '').lower()

    bug_labels = {'bug', 'type:bug', 'kind/bug', 'type: bug', 'defect'}
    question_labels = {'question', 'support', 'help wanted', 'help-wanted'}
    feature_labels = {'enhancement', 'feature', 'proposal', 'feature-request', 'feature request'}

    if bug_labels & labels:
        return 'bug'
    if question_labels & labels:
        return 'question'
    if feature_labels & labels:
        return 'feature'
    if any(kw in title for kw in ['how do i', 'why does', 'how to', 'unable to']):
        return 'question'
    if any(kw in title for kw in ['error', 'fail', 'broken', 'crash', 'wrong', 'not work']):
        return 'bug'
    return 'unknown'


def score_issue(issue):
    """Score an issue for community signal value. Higher = more valuable."""
    kind = classify_issue(issue)
    reactions = issue.get('reactions', {})
    thumbs_up = reactions.get('+1', 0)
    comments = issue.get('comments', 0)

    # Base score by type (Codex recommendation)
    base = {'bug': 0.85, 'question': 0.75, 'feature': 0.30, 'unknown': 0.50}.get(kind, 0.50)

    # Engagement bonus (log scale, capped)
    engagement = min(0.15, log1p(thumbs_up + comments) / 20)

    # Recency bonus
    recency = 0.0
    updated = issue.get('updated_at', '')
    if updated:
        try:
            updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            months_ago = (datetime.now(timezone.utc) - updated_dt).days / 30
            if months_ago <= 18:
                recency = 0.05
        except (ValueError, TypeError):
            pass

    # Resolution bonus (closed issues are confirmed problems)
    resolved = 0.05 if issue.get('state') == 'closed' else 0.0

    # Feature request penalty
    penalty = 0.15 if kind == 'feature' else 0.0

    return round(max(0, min(1, base + engagement + recency + resolved - penalty)), 2)


def severity_from_reactions(reactions_count):
    """Gemini recommendation: severity from reactions."""
    if reactions_count >= 50:
        return "CRITICAL"
    if reactions_count >= 20:
        return "HIGH"
    if reactions_count >= 5:
        return "MEDIUM"
    return "LOW"


# --- Signal merging and dedup ---

def normalize_title(title):
    """Normalize title for dedup comparison."""
    t = title.lower()
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\d+', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def dedupe_signals(signals):
    """Simple dedup by normalized title similarity."""
    seen = {}
    result = []
    for sig in signals:
        key = normalize_title(sig.get('title', ''))
        if key and key in seen:
            # Merge: keep higher-scored one, note duplicate
            existing = seen[key]
            existing.setdefault('also_seen_in', [])
            ref = sig.get('url', sig.get('source', ''))
            if ref:
                existing['also_seen_in'].append(ref)
            continue
        seen[key] = sig
        result.append(sig)
    return result


# --- Render output ---

def render_markdown(signals, meta, output_path):
    """Render community_signals.md in structured Markdown format."""
    lines = []
    lines.append("# Community Signals\n")
    lines.append("## Collection Meta\n")
    lines.append("```yaml")
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("```\n")

    # Group by source type
    changelog_sigs = [s for s in signals if s.get('source') == 'changelog']
    issue_sigs = [s for s in signals if s.get('source') == 'github_issue']
    advisory_sigs = [s for s in signals if s.get('source') == 'security_advisory']
    gitlog_sigs = [s for s in signals if s.get('source') == 'git_log']
    readme_sigs = [s for s in signals if s.get('source') == 'readme']

    sig_id = 0

    # Tier 1: Breaking Changes (Gemini: P0, highest certainty)
    if changelog_sigs:
        lines.append("## Tier 1: Breaking Changes (CHANGELOG)\n")
        for sig in changelog_sigs:
            sig_id += 1
            lines.append(f"### SIG-{sig_id:03d} — {sig['title']}")
            lines.append(f"- **Version**: {sig.get('version', 'unknown')}")
            lines.append(f"- **Source**: changelog")
            if sig.get('evidence'):
                for ev in sig['evidence']:
                    lines.append(f"  - {ev}")
            lines.append("")

    # Tier 1.5: Security Advisories (Codex: high signal, structured)
    if advisory_sigs:
        lines.append("## Tier 1.5: Security Advisories\n")
        for sig in advisory_sigs:
            sig_id += 1
            lines.append(f"### SIG-{sig_id:03d} — {sig['title']}")
            lines.append(f"- **Severity**: {sig.get('severity', 'unknown')}")
            lines.append(f"- **Source**: security_advisory")
            if sig.get('affected_versions'):
                lines.append(f"- **Affected**: {sig['affected_versions']}")
            if sig.get('patched_version'):
                lines.append(f"- **Patched**: {sig['patched_version']}")
            if sig.get('summary'):
                lines.append(f"- **Summary**: {sig['summary']}")
            lines.append("")

    # Tier 2: High-Frequency Pitfalls (Issues)
    if issue_sigs:
        lines.append("## Tier 2: Community Pitfalls (GitHub Issues)\n")
        for sig in issue_sigs:
            sig_id += 1
            lines.append(f"### SIG-{sig_id:03d} — {sig['title']}")
            lines.append(f"- **Source**: github_issue #{sig.get('number', '?')}")
            lines.append(f"- **Type**: {sig.get('kind', 'unknown')}")
            lines.append(f"- **Score**: {sig.get('score', 0)}")
            lines.append(f"- **Reactions**: {sig.get('reactions', 0)} 👍")
            lines.append(f"- **Comments**: {sig.get('comments', 0)}")
            lines.append(f"- **State**: {sig.get('state', 'unknown')}")
            if sig.get('labels'):
                lines.append(f"- **Labels**: {sig['labels']}")
            if sig.get('body_summary'):
                lines.append(f"- **Summary**: {sig['body_summary']}")
            if sig.get('also_seen_in'):
                lines.append(f"- **Also reported in**: {', '.join(sig['also_seen_in'])}")
            lines.append("")

    # Tier 3: README FAQ
    if readme_sigs:
        lines.append("## Tier 3: FAQ & Troubleshooting (README)\n")
        for sig in readme_sigs:
            sig_id += 1
            lines.append(f"### SIG-{sig_id:03d} — {sig['title']}")
            if sig.get('content'):
                # Truncate for context budget
                lines.append(sig['content'][:500])
            lines.append("")

    # Tier 4: Fix commit patterns
    if gitlog_sigs:
        lines.append("## Tier 4: Recent Fix Patterns (git log)\n")
        for sig in gitlog_sigs:
            sig_id += 1
            lines.append(f"### SIG-{sig_id:03d} — {sig['title']}")
            if sig.get('evidence'):
                for ev in sig['evidence']:
                    lines.append(f"- {ev}")
            lines.append("")

    lines.append("---")
    lines.append(f"*Collected by Soul Extractor {datetime.now().strftime('%Y-%m-%d')}*\n")

    content = '\n'.join(lines)

    # Budget control: trim if over limit
    if len(content.encode('utf-8')) > MAX_OUTPUT_BYTES:
        # Progressively remove lower-tier items
        while len(content.encode('utf-8')) > MAX_OUTPUT_BYTES and signals:
            signals.pop()
            content = '\n'.join(lines[:len(lines) - 3])  # crude trim

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(content.encode('utf-8'))


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Collect community signals for Soul Extractor")
    parser.add_argument("--repo-url", default="", help="Repository URL (for GitHub API)")
    parser.add_argument("--repo-path", required=True, help="Local repository path")
    parser.add_argument("--output", required=True, help="Output file path")
    args = parser.parse_args()

    provider = detect_provider(args.repo_url)
    token = os.environ.get("GITHUB_TOKEN", "")
    slug = extract_github_slug(args.repo_url) if provider == "github" else None

    print(f"=== Collecting community signals ===")
    print(f"  Provider: {provider}")
    print(f"  Authenticated: {'yes' if token else 'no'}")

    all_signals = []
    meta = {
        "repo": slug or os.path.basename(args.repo_path),
        "provider": provider,
        "collected_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "authenticated": "yes" if token else "no",
    }

    # --- Local signals (always available, no network) ---

    # 1. CHANGELOG (Gemini: P0, highest certainty)
    changelog_sigs = collect_changelog_signals(args.repo_path)
    print(f"  CHANGELOG signals: {len(changelog_sigs)}")
    all_signals.extend(changelog_sigs)

    # 2. README FAQ
    readme_sigs = collect_readme_faq(args.repo_path)
    print(f"  README FAQ signals: {len(readme_sigs)}")
    all_signals.extend(readme_sigs)

    # 3. git log fix commits (Codex: high ROI, local)
    gitlog_sigs = collect_gitlog_signals(args.repo_path)
    print(f"  Git log fix signals: {len(gitlog_sigs)}")
    all_signals.extend(gitlog_sigs)

    meta["local_signals"] = len(changelog_sigs) + len(readme_sigs) + len(gitlog_sigs)

    # --- Remote signals (GitHub only, graceful degradation) ---

    if provider == "github" and slug:
        # 4. GitHub Issues (Codex: sort=comments, filter PRs, local scoring)
        print(f"  Fetching GitHub issues for: {slug}")
        issues = fetch_github_issues(slug, token=token)
        print(f"  Raw issues fetched: {len(issues)}")

        # Score and rank
        scored_issues = []
        for issue in issues:
            kind = classify_issue(issue)
            score = score_issue(issue)
            reactions = issue.get('reactions', {}).get('+1', 0)

            body = (issue.get('body') or '')
            body_summary = body[:300].replace('\n', ' ').strip()
            if len(body) > 300:
                body_summary += "..."

            scored_issues.append({
                "source": "github_issue",
                "kind": kind,
                "score": score,
                "number": issue.get('number'),
                "title": issue.get('title', ''),
                "reactions": reactions,
                "comments": issue.get('comments', 0),
                "state": issue.get('state', ''),
                "labels": ', '.join(l['name'] for l in issue.get('labels', [])),
                "body_summary": body_summary,
                "severity": severity_from_reactions(reactions),
            })

        # Sort by score descending, take top N
        scored_issues.sort(key=lambda x: x['score'], reverse=True)
        top_issues = scored_issues[:TOP_SIGNALS]
        print(f"  Top issues after scoring: {len(top_issues)}")
        all_signals.extend(top_issues)

        meta["issues_fetched"] = len(issues)
        meta["issues_scored"] = len(top_issues)

        # 5. Security Advisories (Codex: high signal, structured)
        print(f"  Fetching security advisories...")
        advisories = fetch_security_advisories(slug, token=token)
        for adv in advisories:
            vulns = adv.get('vulnerabilities', [])
            affected = ', '.join(
                v.get('vulnerable_version_range', '?') for v in vulns
            )
            patched = ', '.join(
                v.get('first_patched_version', {}).get('identifier', '?') for v in vulns
                if v.get('first_patched_version')
            )
            all_signals.append({
                "source": "security_advisory",
                "kind": "security",
                "title": adv.get('summary', 'Security Advisory'),
                "severity": adv.get('severity', 'unknown'),
                "summary": adv.get('description', '')[:500],
                "affected_versions": affected,
                "patched_version": patched,
                "score": 1.0,  # Security always top priority
            })

        print(f"  Security advisories: {len(advisories)}")
        meta["advisories_fetched"] = len(advisories)

    elif provider != "github":
        print(f"  Skipping remote signals (provider: {provider}, local-only mode)")
        meta["remote_community_support"] = "false"
        meta["reason"] = "non-github provider"

    # --- Dedupe and render ---
    all_signals = dedupe_signals(all_signals)
    print(f"  Total signals after dedup: {len(all_signals)}")

    output_size = render_markdown(all_signals, meta, args.output)
    print(f"  -> {args.output} ({output_size} bytes)")

    meta["total_signals"] = len(all_signals)
    meta["output_bytes"] = output_size


if __name__ == "__main__":
    main()
