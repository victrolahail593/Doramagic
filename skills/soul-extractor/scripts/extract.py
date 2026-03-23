#!/usr/bin/env python3
"""
Soul Extractor — Extract structured knowledge from any open source project.
Usage: python3 extract.py <repo_url_or_path> [output_dir]

Environment variables:
  ANTHROPIC_API_KEY  — API key (required)
  ANTHROPIC_BASE_URL — API base URL (default: https://api.anthropic.com)
  SOUL_MODEL         — Model to use (default: claude-sonnet-4-6-20260217)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import urllib.request
import urllib.error


# --- Config ---

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
MODEL = os.environ.get("SOUL_MODEL", "claude-sonnet-4-6-20260217")
MAX_TOKENS = 8192


def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Call Anthropic Messages API using the SDK."""
    if not API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=API_KEY, base_url=BASE_URL if "anthropic.com" not in BASE_URL else None)
        
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(b.text for b in response.content if hasattr(b, "text"))
    except Exception as e:
        print(f"LLM Error: {e}")
        sys.exit(1)


def run_cmd(cmd: str, cwd: str = None) -> str:
    """Run a shell command and return stdout."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"CMD FAILED: {cmd}\n{result.stderr[:500]}")
    return result.stdout


def write_file(path: str, content: str):
    """Write content to file, creating directories as needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  -> {path}")


# --- Phase 0: Prepare ---

def phase0_prepare(repo_input: str, output_dir: str) -> dict:
    """Clone repo and run Repomix."""
    print("\n=== Phase 0: Prepare ===")
    artifacts = os.path.join(output_dir, "artifacts")
    os.makedirs(artifacts, exist_ok=True)

    # Clone or use local
    if repo_input.startswith("http") or repo_input.startswith("git@"):
        repo_name = os.path.basename(repo_input).replace(".git", "")
        clone_dir = os.path.join(artifacts, "_repo")
        if not os.path.isdir(clone_dir):
            print(f"  Cloning {repo_input}...")
            run_cmd(f"git clone --depth 1 '{repo_input}' '{clone_dir}'")
        repo_path = clone_dir
    else:
        repo_path = repo_input
        repo_name = os.path.basename(os.path.abspath(repo_path))

    # Run Repomix
    compressed_xml = os.path.join(artifacts, "packed_compressed.xml")
    full_xml = os.path.join(artifacts, "packed_full.xml")

    if not os.path.exists(compressed_xml):
        print("  Running Repomix (compressed)...")
        run_cmd(f"npx repomix --compress --style xml -o '{compressed_xml}'", cwd=repo_path)

    if not os.path.exists(full_xml):
        print("  Running Repomix (full)...")
        run_cmd(f"npx repomix --style xml -o '{full_xml}'", cwd=repo_path)

    # Read files
    with open(compressed_xml, "r") as f:
        compressed = f.read()
    with open(full_xml, "r") as f:
        full = f.read()

    # Truncate if too large (keep under 150K chars to fit in context)
    if len(compressed) > 150000:
        compressed = compressed[:150000] + "\n<!-- TRUNCATED -->"
    if len(full) > 150000:
        full = full[:150000] + "\n<!-- TRUNCATED -->"

    print(f"  Repo: {repo_name}")
    print(f"  Compressed: {len(compressed):,} chars")
    print(f"  Full: {len(full):,} chars")
    return {
        "repo_name": repo_name,
        "repo_path": repo_path,
        "compressed": compressed,
        "full": full,
        "artifacts_dir": artifacts,
    }


# --- Phase 1: Eagle Eye ---

def phase1_eagle_eye(ctx: dict, output_dir: str) -> str:
    """Run Eagle Eye analysis: identity, modules, soul locus scoring."""
    print("\n=== Phase 1: Eagle Eye ===")

    system = (
        "You are an expert code analyst. Analyze the provided codebase "
        "and produce structured knowledge extraction. Be evidence-based — "
        "cite file:line references. Use English for all output."
    )

    prompt = f"""Analyze this codebase and produce THREE sections in a single response.

<codebase>
{ctx['compressed']}
</codebase>

## Section 1: IDENTITY

Write a project identity analysis:
- What it is, what it does, who uses it (3-4 sentences)
- Design philosophy (1-2 sentences)
- 5-10 Core Concepts: each with 1-sentence definition and file:line reference

## Section 2: MODULE MAP

- List 4-8 logical modules (table: module, file, lines, responsibility)
- Show a Mermaid dependency diagram
- Trace the primary data flow from input to output

## Section 3: SOUL LOCUS SCORING

Score each important code area on 8 dimensions (0-100, weighted):
- Domain Centrality (20%), Execution Influence (15%), Orchestration Power (15%)
- Data/State Gravity (15%), Rule Density (10%), Boundary Importance (10%)
- Cross-Module Bridge (10%), Concept Density (5%)

CALIBRATION: At least 30% of scores MUST be below 70.

Output a ranked table with weighted scores. Select the TOP 3 as the Deep Dive queue.
End with: DEEP_DIVE_QUEUE: <locus1_name>|<file:lines>, <locus2_name>|<file:lines>, <locus3_name>|<file:lines>
"""

    print("  Calling LLM for Eagle Eye...")
    result = call_llm(system, prompt)

    write_file(os.path.join(output_dir, "artifacts", "eagle_eye_analysis.md"), result)

    # Extract deep dive queue from result
    queue_match = re.search(r"DEEP_DIVE_QUEUE:\s*(.+)", result)
    queue_str = queue_match.group(1).strip() if queue_match else ""
    print(f"  Deep Dive Queue: {queue_str}")

    return result


# --- Phase 2: Deep Dive ---

def phase2_deep_dive(ctx: dict, eagle_eye: str, output_dir: str) -> str:
    """Deep dive on top 3 loci: concept cards, workflow cards, rule cards."""
    print("\n=== Phase 2: Deep Dive ===")

    system = (
        "You are an expert code analyst performing deep knowledge extraction. "
        "Produce structured knowledge cards with YAML frontmatter. "
        "Every claim must cite file:line. Every workflow card must have a Mermaid flowchart. "
        "Use English for all output."
    )

    prompt = f"""Based on the Eagle Eye analysis and FULL source code, extract knowledge cards for the top 3 loci.

<eagle_eye>
{eagle_eye[:20000]}
</eagle_eye>

<full_source>
{ctx['full']}
</full_source>

Produce ALL of the following in a single response, separated by "---CARD---" markers:

### For each of the top 3 loci, produce:

**1. Concept Card (CC-001, CC-002, CC-003)**

```yaml
---
card_type: concept_card
card_id: CC-NNN
repo: {ctx['repo_name']}
title: "..."
---
```
Sections: Identity, Is/IsNot table, Key Attributes, Boundaries, Evidence (file:line)

**2. Workflow Card (WF-001, WF-002, WF-003)**

```yaml
---
card_type: workflow_card
card_id: WF-NNN
repo: {ctx['repo_name']}
title: "..."
---
```
Sections: Steps (3-8 with file:line evidence), Mermaid flowchart (MANDATORY), Failure Modes (2+)

**3. Decision Rule Cards (DR-001 through DR-005+)**

Extract the most important conditional rules, edge cases, and design decisions from code:

```yaml
---
card_type: decision_rule_card
card_id: DR-NNN
repo: {ctx['repo_name']}
type: DESIGN_DECISION
title: "..."
rule: |
  IF condition THEN behavior
context: |
  Why this rule exists
do:
  - "recommendation"
dont:
  - "common mistake"
confidence: 0.95
sources:
  - "file.py:L42-L58"
---
```

Produce at least 3 concept cards, 3 workflow cards, and 3 decision rule cards.
"""

    print("  Calling LLM for Deep Dive...")
    result = call_llm(system, prompt)

    write_file(os.path.join(output_dir, "artifacts", "deep_dive_cards.md"), result)

    # Split cards into individual files
    cards = result.split("---CARD---")
    card_dir = os.path.join(output_dir, "soul", "cards")
    os.makedirs(os.path.join(card_dir, "concepts"), exist_ok=True)
    os.makedirs(os.path.join(card_dir, "workflows"), exist_ok=True)
    os.makedirs(os.path.join(card_dir, "rules"), exist_ok=True)

    cc_count = wf_count = dr_count = 0
    for card in cards:
        card = card.strip()
        if not card:
            continue
        if "card_type: concept_card" in card:
            cc_count += 1
            write_file(os.path.join(card_dir, "concepts", f"CC-{cc_count:03d}.md"), card)
        elif "card_type: workflow_card" in card:
            wf_count += 1
            write_file(os.path.join(card_dir, "workflows", f"WF-{wf_count:03d}.md"), card)
        elif "card_type: decision_rule_card" in card:
            dr_count += 1
            write_file(os.path.join(card_dir, "rules", f"DR-{dr_count:03d}.md"), card)

    # If no cards were split (model didn't use separator), save as single file
    if cc_count + wf_count + dr_count == 0:
        write_file(os.path.join(card_dir, "all_cards.md"), result)
        print("  Note: Cards saved as single file (model didn't use ---CARD--- separator)")

    print(f"  Cards: {cc_count} concept, {wf_count} workflow, {dr_count} rule")
    return result


# --- Phase 3: Community Soul ---

def phase3_community(ctx: dict, output_dir: str) -> str:
    """Extract community UNSAID knowledge."""
    print("\n=== Phase 3: Community Soul ===")

    system = (
        "You are an expert developer with deep community knowledge. "
        "Extract UNSAID knowledge — gotchas, traps, best practices, and "
        "compatibility issues that official docs don't mention. "
        "Be honest about confidence levels. Use English."
    )

    prompt = f"""For the project "{ctx['repo_name']}", extract UNSAID community knowledge.

Step 1: List 15-25 known gotchas, traps, best practices, and compatibility issues.
For each, note: title, description, type (GOTCHA/BEST_PRACTICE/COMPATIBILITY/PERFORMANCE), confidence (0.0-1.0).

Step 2: For each item, write a decision_rule_card:

```yaml
---
card_type: decision_rule_card
card_id: DR-1NN
repo: {ctx['repo_name']}
type: UNSAID_GOTCHA
title: "..."
rule: |
  ...
context: |
  ...
do:
  - "..."
dont:
  - "..."
confidence: 0.85
sources:
  - "description of evidence"
---
```

Separate each card with "---CARD---".

Step 3: End with a summary section titled "## Community Soul Summary" containing:
- Total items found
- Category breakdown (GOTCHA/BEST_PRACTICE/COMPATIBILITY/PERFORMANCE counts)
- Top 5 most impactful findings
"""

    print("  Calling LLM for Community Soul...")
    result = call_llm(system, prompt)

    # Split and save community cards
    cards = result.split("---CARD---")
    rules_dir = os.path.join(output_dir, "soul", "cards", "rules")
    os.makedirs(rules_dir, exist_ok=True)

    dr_count = 0
    for card in cards:
        card = card.strip()
        if "card_type: decision_rule_card" in card:
            dr_count += 1
            write_file(os.path.join(rules_dir, f"DR-{100 + dr_count:03d}.md"), card)

    # Extract and save summary
    summary_match = re.search(r"(## Community Soul Summary.+)", result, re.DOTALL)
    summary = summary_match.group(1) if summary_match else result[-2000:]
    write_file(os.path.join(output_dir, "soul", "community_soul_summary.md"), summary)

    if dr_count == 0:
        write_file(os.path.join(rules_dir, "community_cards.md"), result)
        print("  Note: Community cards saved as single file")

    print(f"  Community rule cards: {dr_count}")
    return result


# --- Phase 4: Project Soul Summary ---

def phase4_summary(ctx: dict, eagle_eye: str, deep_dive: str, community: str, output_dir: str):
    """Generate project soul summary."""
    print("\n=== Phase 4: Project Soul Summary ===")

    system = "You are a technical writer creating a concise project knowledge summary."

    prompt = f"""Based on the extracted knowledge for "{ctx['repo_name']}", write a Project Soul Summary.

<eagle_eye_excerpt>
{eagle_eye[:5000]}
</eagle_eye_excerpt>

<deep_dive_excerpt>
{deep_dive[:5000]}
</deep_dive_excerpt>

<community_excerpt>
{community[:3000]}
</community_excerpt>

Write a "Project Soul" document with:

1. **What Makes It Tick** — 2-3 core design principles
2. **Architecture in One Sentence** — the primary data flow
3. **Card Index** — table of all extracted cards (ID, title, type)
4. **Key Insights** — 3-5 non-obvious discoveries
5. **Top Gotchas** — the 5 most important UNSAID things a developer must know

Keep it concise. This is the "start here" document.
"""

    print("  Calling LLM for summary...")
    result = call_llm(system, prompt)
    write_file(os.path.join(output_dir, "soul", "project_soul.md"), result)
    return result


# --- Main ---

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    repo_input = sys.argv[1]
    repo_name = os.path.basename(repo_input).replace(".git", "")
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(f"~/soul-output/{repo_name}")

    print(f"Soul Extractor v0.1.0")
    print(f"Repo: {repo_input}")
    print(f"Output: {output_dir}")
    print(f"Model: {MODEL}")
    print(f"API: {BASE_URL}")

    # Phase 0
    ctx = phase0_prepare(repo_input, output_dir)

    # Phase 1
    eagle_eye = phase1_eagle_eye(ctx, output_dir)

    # Phase 2
    deep_dive = phase2_deep_dive(ctx, eagle_eye, output_dir)

    # Phase 3
    community = phase3_community(ctx, output_dir)

    # Phase 4
    summary = phase4_summary(ctx, eagle_eye, deep_dive, community, output_dir)

    # Done
    print(f"\n{'='*50}")
    print(f"DONE! Soul extracted for {ctx['repo_name']}")
    print(f"Output: {output_dir}/soul/")
    print(f"Start here: {output_dir}/soul/project_soul.md")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
