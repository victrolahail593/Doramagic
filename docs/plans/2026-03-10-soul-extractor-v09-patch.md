# Soul Extractor v0.9 Patch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix three regressions in Soul Extractor v0.9: unreliable benchmark scoring, hallucinated content passing validation, and missing feature inventory in output.

**Architecture:** Three independent patches to existing scripts. No new stages, no breaking changes. (1) `run_judge.py` gets retry logic. (2) A new `extract_repo_facts.py` script produces `repo_facts.json` at Stage 0; `validate_extraction.py` gains a fact-check gate; `prepare-repo.sh` calls the new script. (3) `assemble-output.sh` renders a FEATURE INVENTORY block from `repo_facts.json`.

**Tech Stack:** Python 3.9+, bash, existing Soul Extractor script layout at `/Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/`

---

## Task 1: Fix benchmark retry in `run_judge.py`

**Files:**
- Modify: `experiments/exp07-v09-superpowers-usertest/benchmark/run_judge.py`

**Context:** Gemini CLI times out (~120s) on long prompts. Currently any failure records 0/3. We need per-question retry with increasing timeout.

**Step 1: Add retry logic to `run_gemini_judge()`**

Open `run_judge.py`. Replace the `run_gemini_judge` function (lines 68–103) with:

```python
def run_gemini_judge(question, key_points, anti_points, answer, max_retries=3):
    """Send evaluation prompt to Gemini CLI and parse JSON response. Retries on timeout."""
    eval_prompt = f"""你是一个严格的考试阅卷员。只根据标准答案评判，不要加入自己的知识。

### 题目
{question}

### 标准答案要点
{key_points}

### 反面要点（提到则扣分）
{anti_points}

### 被评判的回答
{answer[:2000]}

### 评分规则
- factual (0-1): 回答中是否有与标准答案矛盾的错误？1=无错误 0=有错误
- coverage (0-1): 标准答案要点覆盖了一半以上？1=是 0=否
- no_hallucination (0-1): 没有提到反面要点或编造不存在的东西？1=无幻觉 0=有幻觉

只输出JSON:
{{"factual": 0或1, "coverage": 0或1, "no_hallucination": 0或1, "total": 总分, "reasoning": "一句话"}}"""

    last_error = None
    for attempt in range(1, max_retries + 1):
        timeout = 180 + (attempt - 1) * 30  # 180, 210, 240
        try:
            result = subprocess.run(
                ["gemini", "-p", eval_prompt],
                capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            output = output.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(output)
            if attempt > 1:
                print(f"  (succeeded on attempt {attempt})")
            return parsed
        except subprocess.TimeoutExpired as e:
            last_error = f"TIMEOUT after {timeout}s"
            print(f"  WARNING: attempt {attempt}/{max_retries} timed out, retrying...")
        except json.JSONDecodeError as e:
            last_error = f"PARSE_ERROR: {e}"
            print(f"  WARNING: attempt {attempt}/{max_retries} parse error, retrying...")
        except Exception as e:
            last_error = f"CLI_ERROR: {e}"
            print(f"  WARNING: attempt {attempt}/{max_retries} failed: {e}, retrying...")

    print(f"  ERROR: all {max_retries} attempts failed: {last_error}")
    return {"factual": 0, "coverage": 0, "no_hallucination": 0, "total": 0,
            "reasoning": f"EVAL_FAILED: {last_error}"}
```

Key changes: answer truncated to 2000 chars to reduce prompt size, retry loop up to 3 times, timeout starts at 180s and grows by 30s per attempt.

**Step 2: Verify the function signature change propagates**

`run_gemini_judge` is called on line 144. The call signature `run_gemini_judge(QUESTIONS[q_id], KEY_POINTS[q_id], ANTI_POINTS[q_id], answer)` stays the same — `max_retries` has a default. No other changes needed.

**Step 3: Also copy the fix to the skill's benchmark template**

The canonical benchmark scripts live alongside the skill. Copy the updated file:

```bash
cp /Users/tang/Documents/vibecoding/allinone/experiments/exp07-v09-superpowers-usertest/benchmark/run_judge.py \
   /Users/tang/Documents/vibecoding/allinone/experiments/exp06-v09-superpowers/benchmark/run_judge.py
```

**Step 4: Smoke-test the retry path (no actual Gemini call)**

```bash
cd /Users/tang/Documents/vibecoding/allinone/experiments/exp07-v09-superpowers-usertest/benchmark
python3 -c "
import run_judge
# Verify function exists and has max_retries param
import inspect
sig = inspect.signature(run_judge.run_gemini_judge)
assert 'max_retries' in sig.parameters, 'max_retries param missing'
print('OK: run_gemini_judge has max_retries parameter')
"
```
Expected: `OK: run_gemini_judge has max_retries parameter`

---

## Task 2: Create `extract_repo_facts.py`

**Files:**
- Create: `skills/soul-extractor/scripts/extract_repo_facts.py`

**Context:** We need a deterministic (non-LLM) extractor that walks the repo and produces `repo_facts.json`. This whitelist is later used to fact-check CLAUDE.md claims. The script must work on any repo — it should look for patterns that indicate commands, skills, features, and file paths.

**Step 1: Create the script**

```python
#!/usr/bin/env python3
"""
Soul Extractor: Extract deterministic facts from a repository.
Produces repo_facts.json — a whitelist used for fact-checking extracted claims.

Usage:
    python3 extract_repo_facts.py --repo-path <path> --output <output_dir>

Output: <output_dir>/artifacts/repo_facts.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def extract_cli_commands(repo_path):
    """Find CLI commands defined in the repo (setup.py, pyproject.toml, package.json, etc.)."""
    commands = set()

    # Python: setup.py / pyproject.toml console_scripts
    for fname in ["setup.py", "setup.cfg", "pyproject.toml"]:
        fpath = os.path.join(repo_path, fname)
        if os.path.exists(fpath):
            text = open(fpath, encoding="utf-8", errors="ignore").read()
            # console_scripts = ["cmd = module:func"]
            for m in re.finditer(r'["\'](\w[\w-]*)(?:\s*=\s*[\w.:]+)?["\']', text):
                name = m.group(1)
                if len(name) > 1 and not name.startswith("_"):
                    commands.add(name)

    # Node: package.json bin / scripts
    pkg = os.path.join(repo_path, "package.json")
    if os.path.exists(pkg):
        try:
            data = json.load(open(pkg, encoding="utf-8"))
            for key in data.get("bin", {}).keys():
                commands.add(key)
            for key in data.get("scripts", {}).keys():
                commands.add(f"npm run {key}")
        except Exception:
            pass

    # Shell scripts in bin/ or scripts/
    for bindir in ["bin", "scripts"]:
        dirpath = os.path.join(repo_path, bindir)
        if os.path.isdir(dirpath):
            for f in os.listdir(dirpath):
                if not f.startswith("."):
                    commands.add(f)

    return sorted(commands)


def extract_skill_names(repo_path):
    """Find skill/plugin names from skills/, plugins/, .claude/skills/ directories."""
    skills = set()

    for skilldir in ["skills", "plugins", ".claude/skills", ".claude/plugins"]:
        dirpath = os.path.join(repo_path, skilldir)
        if not os.path.isdir(dirpath):
            continue
        for entry in os.listdir(dirpath):
            full = os.path.join(dirpath, entry)
            if os.path.isdir(full) and not entry.startswith("."):
                skills.add(entry)
            # Also check SKILL.md name field
            skill_md = os.path.join(full, "SKILL.md")
            if os.path.exists(skill_md):
                text = open(skill_md, encoding="utf-8", errors="ignore").read()
                m = re.search(r"^name:\s*(.+)", text, re.MULTILINE)
                if m:
                    skills.add(m.group(1).strip())

    return sorted(skills)


def extract_file_paths(repo_path):
    """List all non-hidden files relative to repo root (for source ref validation)."""
    paths = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in
                   ("node_modules", "__pycache__", ".git", "venv", ".venv", "dist", "build")]
        for f in files:
            if not f.startswith("."):
                rel = os.path.relpath(os.path.join(root, f), repo_path)
                paths.append(rel)
    return sorted(paths)


def extract_config_keys(repo_path):
    """Find configuration keys from .env.example, config files, README."""
    keys = set()

    for fname in [".env.example", ".env.sample", "config.example.yaml",
                  "config.example.yml", "config.example.json"]:
        fpath = os.path.join(repo_path, fname)
        if os.path.exists(fpath):
            text = open(fpath, encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r"^([A-Z][A-Z0-9_]{2,})\s*=", text, re.MULTILINE):
                keys.add(m.group(1))

    return sorted(keys)


def main():
    parser = argparse.ArgumentParser(description="Extract deterministic facts from a repo")
    parser.add_argument("--repo-path", required=True, help="Path to cloned repo")
    parser.add_argument("--output-dir", required=True, help="Output directory (artifacts/ will be used)")
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.isdir(repo_path):
        print(f"ERROR: repo path not found: {repo_path}", file=sys.stderr)
        sys.exit(1)

    artifacts_dir = os.path.join(output_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    facts = {
        "repo_path": repo_path,
        "commands": extract_cli_commands(repo_path),
        "skills": extract_skill_names(repo_path),
        "files": extract_file_paths(repo_path),
        "config_keys": extract_config_keys(repo_path),
    }

    out_path = os.path.join(artifacts_dir, "repo_facts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, ensure_ascii=False)

    print(f"repo_facts={out_path}")
    print(f"  commands: {len(facts['commands'])}")
    print(f"  skills:   {len(facts['skills'])}")
    print(f"  files:    {len(facts['files'])}")
    print(f"  config_keys: {len(facts['config_keys'])}")


if __name__ == "__main__":
    main()
```

**Step 2: Make executable**

```bash
chmod +x /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/extract_repo_facts.py
```

**Step 3: Test against the cached superpowers repo**

```bash
python3 /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/extract_repo_facts.py \
  --repo-path ~/soul-output/superpowers/artifacts/_repo \
  --output-dir /tmp/facts-test
cat /tmp/facts-test/artifacts/repo_facts.json | python3 -m json.tool | head -40
```

Expected: JSON with `commands`, `skills` (should include skill names like `brainstorming`, `tdd`, etc.), `files`.

---

## Task 3: Wire `extract_repo_facts.py` into `prepare-repo.sh`

**Files:**
- Modify: `skills/soul-extractor/scripts/prepare-repo.sh`

**Step 1: Add the call after community signals collection**

After the community signals block (after line 71, before the Stats section), insert:

```bash
# --- Extract repo facts (for fact-checking in Stage 3.5) ---
REPO_FACTS="$OUTPUT_DIR/artifacts/repo_facts.json"
if [ ! -f "$REPO_FACTS" ]; then
    python3 "$SCRIPT_DIR/extract_repo_facts.py" \
        --repo-path "$REPO_PATH" \
        --output-dir "$OUTPUT_DIR" \
        2>&1 || echo "  [warn] Repo facts extraction failed, continuing without it"
fi
FACTS_SIZE=$(wc -c < "$REPO_FACTS" 2>/dev/null | tr -d ' ' || echo "0")
```

**Step 2: Add to Stats output** (in the echo block at the end):

```bash
echo "facts=$REPO_FACTS ($FACTS_SIZE bytes)"
```

**Step 3: Test end-to-end**

```bash
# Remove cached facts to force re-run
rm -f ~/soul-output/superpowers/artifacts/repo_facts.json
bash /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/prepare-repo.sh \
  https://github.com/obra/superpowers ~/soul-output/superpowers
```

Expected: output includes `facts=...repo_facts.json (NNN bytes)`

---

## Task 4: Add fact-checking gate to `validate_extraction.py`

**Files:**
- Modify: `skills/soul-extractor/scripts/validate_extraction.py`

**Context:** After CLAUDE.md is assembled (Stage 5), we need to check that any commands, install steps, or skill names mentioned in it actually appear in `repo_facts.json`. This runs as part of Stage 3.5 (pre-assembly) by checking the DR card bodies too.

**Step 1: Add `load_repo_facts()` helper** (after `load_community_signals()` around line 263):

```python
def load_repo_facts(output_dir):
    """Load repo_facts.json for claim verification."""
    path = os.path.join(output_dir, "artifacts", "repo_facts.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
```

**Step 2: Add `check_commands_in_facts()` checker** (after `check_community_source_refs()` around line 229):

```python
def check_commands_in_facts(meta, body, repo_facts):
    """Check that commands/skill names mentioned in card body exist in repo_facts."""
    if repo_facts is None:
        return []  # No facts available, skip check

    known_commands = set(repo_facts.get("commands", []))
    known_skills = set(repo_facts.get("skills", []))
    all_known = known_commands | known_skills

    if not all_known:
        return []  # Empty whitelist, skip

    errors = []
    # Find backtick-quoted tokens that look like CLI commands or slash commands
    # e.g. `/plugin marketplace add` or `openclaw agent`
    for m in re.finditer(r'`(/[\w\s]+|[\w][\w-]+ [\w-]+)`', body):
        token = m.group(1).strip()
        first_word = token.split()[0].lstrip("/")
        # Only flag if it looks like a command (not a file path)
        if "/" not in token and "." not in token:
            if first_word not in all_known and len(first_word) > 2:
                errors.append(
                    f"Command/skill '{token}' not found in repo_facts.json whitelist"
                )
    return errors
```

**Step 3: Wire it into `validate_all()`** — inside the card validation loop, after the existing content quality checks (around line 364):

```python
        # Fact-checking gate (v0.9 patch)
        if card_type == "decision_rule_card" and repo_facts:
            errors.extend(check_commands_in_facts(meta, body, repo_facts))
```

**Step 4: Pass `repo_facts` into `validate_all()`** — add loading (after `repo_file_index` on line 287):

```python
    repo_facts = load_repo_facts(output_dir)
```

**Step 5: Fix `traceability_pass` missing from `overall_pass`** (Codex report finding, line 436):

Change:
```python
        "overall_pass": (
            total_errors == 0
            and len(quantity_errors) == 0
        ),
```
To:
```python
        "overall_pass": (
            total_errors == 0
            and len(quantity_errors) == 0
            and g["traceability_pass"]
        ),
```

**Step 6: Test on the exp07 extraction output**

```bash
python3 /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/validate_extraction.py \
  --output-dir ~/soul-output/superpowers
```

Expected: Any cards with unverified commands get flagged. Existing clean cards still pass.

---

## Task 5: Add FEATURE INVENTORY to `assemble-output.sh`

**Files:**
- Modify: `skills/soul-extractor/scripts/assemble-output.sh`

**Context:** CLAUDE.md currently has no list of what skills/features/commands the project has. This causes Q02-type failures where AI guesses wrong names. We render this deterministically from `repo_facts.json`.

**Step 1: Add inventory generation block** — insert after the `REFERENCE_SECTION` tempfile setup (after line 83, before "Assemble CLAUDE.md"):

```bash
# --- Build FEATURE INVENTORY section (from repo_facts.json) ---
INVENTORY_SECTION=$(mktemp)
REPO_FACTS="$OUTPUT_DIR/artifacts/repo_facts.json"
if [ -f "$REPO_FACTS" ]; then
    python3 - "$REPO_FACTS" << 'PYEOF' > "$INVENTORY_SECTION"
import json, sys
facts = json.load(open(sys.argv[1]))
skills = facts.get("skills", [])
commands = facts.get("commands", [])
config_keys = facts.get("config_keys", [])

lines = ["## FEATURE INVENTORY", ""]
if skills:
    lines.append("**Skills / Features:**")
    for s in skills:
        lines.append(f"- `{s}`")
    lines.append("")
if commands:
    lines.append("**Commands:**")
    for c in commands[:20]:  # cap at 20 to avoid bloat
        lines.append(f"- `{c}`")
    lines.append("")
if config_keys:
    lines.append("**Config Keys:**")
    for k in config_keys[:15]:
        lines.append(f"- `{k}`")
    lines.append("")
print("\n".join(lines))
PYEOF
else
    echo "" > "$INVENTORY_SECTION"
fi
```

**Step 2: Insert INVENTORY into CLAUDE.md assembly** — in the `{ ... } > "$CLAUDE_MD"` block (around line 86), add inventory between CRITICAL RULES and EXPERT KNOWLEDGE:

```bash
{
    echo "# $REPO_NAME — AI Knowledge Pack"
    echo "# Auto-generated by Soul Extractor v0.9"
    echo "# Structure: CRITICAL RULES → FEATURE INVENTORY → EXPERT KNOWLEDGE → QUICK REFERENCE"
    echo ""
    cat "$RULES_SECTION"
    cat "$INVENTORY_SECTION"
    echo "## EXPERT KNOWLEDGE"
    echo ""
    cat "$NARRATIVE"
    echo ""
    cat "$REFERENCE_SECTION"
} > "$CLAUDE_MD"
```

**Step 3: Add cleanup of INVENTORY_SECTION temp file** — in the `rm -f` cleanup line:

```bash
rm -f "$RULES_SECTION" "$REFERENCE_SECTION" "$INVENTORY_SECTION"
```

**Step 4: Test against superpowers output**

```bash
bash /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/scripts/assemble-output.sh \
  ~/soul-output/superpowers
grep -A 30 "FEATURE INVENTORY" ~/soul-output/superpowers/inject/CLAUDE.md
```

Expected: FEATURE INVENTORY section with skill names listed.

---

## Task 6: Deploy to remote OpenClaw + run exp08

**Step 1: Sync skill to remote**

```bash
rsync -avz --delete \
  /Users/tang/Documents/vibecoding/allinone/skills/soul-extractor/ \
  tangsir@192.168.0.251:~/.openclaw/skills/soul-extractor/
```

**Step 2: Clear previous extraction cache on remote**

```bash
ssh tangsir@192.168.0.251 "rm -rf ~/soul-output/superpowers"
```

**Step 3: Trigger extraction via Telegram**

Send to `@tangsirminibot`:
```
提取灵魂 https://github.com/obra/superpowers
```

Monitor via session file on remote.

**Step 4: Pull output to local exp08**

```bash
mkdir -p /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/{benchmark,results}
cp -r /Users/tang/Documents/vibecoding/allinone/experiments/exp07-v09-superpowers-usertest/benchmark/* \
  /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/benchmark/
scp -r tangsir@192.168.0.251:~/soul-output/superpowers/inject/ \
  /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/
scp -r tangsir@192.168.0.251:~/soul-output/superpowers/soul/ \
  /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/
```

**Step 5: Run benchmark on remote**

```bash
# Upload benchmark scripts
ssh tangsir@192.168.0.251 "mkdir -p ~/soul-extract-exp08-benchmark"
scp -r /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/benchmark/ \
  tangsir@192.168.0.251:~/soul-extract-exp08-benchmark/

# Run A group (no injection) — may reuse exp07 results if identical
ssh tangsir@192.168.0.251 "source ~/.zshrc && cd ~/soul-extract-exp08-benchmark/benchmark && CLAUDECODE='' bash run_answers.sh A"

# Run C group (v0.9 patch injection)
ssh tangsir@192.168.0.251 "source ~/.zshrc && cd ~/soul-extract-exp08-benchmark/benchmark && CLAUDECODE='' bash run_answers.sh C ~/soul-output/superpowers/inject/CLAUDE.md"

# Judge both groups
ssh tangsir@192.168.0.251 "source ~/.zshrc && cd ~/soul-extract-exp08-benchmark/benchmark && python3 run_judge.py A && python3 run_judge.py C"
```

**Step 6: Pull results and compare**

```bash
scp -r tangsir@192.168.0.251:~/soul-extract-exp08-benchmark/results/ \
  /Users/tang/Documents/vibecoding/allinone/experiments/exp08-v09patch-superpowers/
```

Expected: C组 ≥ A组 (26/30). If Q07 scores 3/3 with no hallucinated commands, the patch worked.
