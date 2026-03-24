# Installing Doramagic

## Option 1: OpenClaw Skill (recommended)

Install from ClawHub:
```bash
openclaw skills install dora
```

Or manually:
```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cp -r Doramagic/skills/doramagic ~/.openclaw/skills/dora
```

### Usage in OpenClaw

In any OpenClaw conversation, type:
```
/dora 帮我做一个记账 app
```

Or point directly at a GitHub repo:
```
/dora https://github.com/TandoorRecipes/recipes
```

Doramagic will search GitHub for relevant projects, extract their design wisdom, and compile an AI advisor pack.

## Option 2: Claude Code Skill

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
mkdir -p ~/.claude/skills
cp -r Doramagic/skills/doramagic ~/.claude/skills/dora
```

### Usage in Claude Code

In any Claude Code session, type:
```
/dora https://github.com/user/project
```

The skill works identically to the OpenClaw version. Output is shown directly in the conversation.

## Option 3: Standalone Python (for developers)

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cd Doramagic
pip install pydantic
```

### Single-project extraction

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

python3 packages/orchestration/doramagic_orchestration/phase_runner.py \
  --repo-path /path/to/cloned/repo \
  --output-dir ./output
```

### Full pipeline (search + extract + compile)

```bash
python3 skills/doramagic/scripts/doramagic_main.py \
  --cli \
  --input "帮我做记账 app" \
  --run-dir ./runs
```

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- At least one LLM API key:
  - `ANTHROPIC_API_KEY` (Claude) — recommended
  - `GOOGLE_API_KEY` (Gemini)
  - `OPENAI_API_KEY` (GPT)

## Configuration

### Model selection

Copy the example config and edit:
```bash
cp models.json.example models.json
```

The `models.json` file declares which LLMs are available. The capability router automatically selects the cheapest model that satisfies each stage's requirements. You only need to configure models you have API keys for.

### Environment variables

```bash
# Required: at least one
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: additional providers
export GOOGLE_API_KEY="..."
export OPENAI_API_KEY="sk-proj-..."
```

## Output

All options produce the same output:
- **`CLAUDE.md`** — Injectable AI context file (design philosophy, mental models, decision rules)
- **`.cursorrules`** — Cursor IDE integration
- **`advisor-brief.md`** — Executive summary with evidence trail
- **`PROVENANCE.md`** — Evidence chain for every extracted claim
- **`LIMITATIONS.md`** — Known gaps and extraction confidence
