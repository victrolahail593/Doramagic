# Doramagic

[![CI](https://github.com/tangweigang-jpg/Doramagic/actions/workflows/ci.yml/badge.svg)](https://github.com/tangweigang-jpg/Doramagic/actions/workflows/ci.yml)

> **"Don't teach the user what to do -- give them the tool."** -- Doramagic's design philosophy, inspired by Doraemon.

Doramagic extracts the **soul** of open-source projects -- not just what the code does, but *why* it was designed that way and the hard-won community wisdom that never appears in documentation. The extracted knowledge is compiled into injectable advisor packs that make AI assistants deeply understand a project's design philosophy, mental models, and community pitfalls.

**Doramagic is a tool that must be installed and run.** It executes a 7-phase extraction pipeline against real GitHub repositories. Reading this README does not enable its functionality -- you must install it as a skill and invoke `/dora`.

## Quick Start

### 1. Clone

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git ~/Doramagic
cd ~/Doramagic
```

### 2. Install as a skill

**OpenClaw:**
```bash
mkdir -p ~/.openclaw/skills
cp -r ~/Doramagic/skills/doramagic ~/.openclaw/skills/dora
```

**Claude Code:**
```bash
mkdir -p ~/.claude/skills
cp -r ~/Doramagic/skills/doramagic ~/.claude/skills/dora
```

### 3. Configure models

The installed skill includes `models.json.example`. Copy and edit it **inside the skill directory**:

```bash
# OpenClaw:
cp ~/.openclaw/skills/dora/models.json.example ~/.openclaw/skills/dora/models.json

# Claude Code:
cp ~/.claude/skills/dora/models.json.example ~/.claude/skills/dora/models.json
```

Edit `models.json` -- declare the models you have access to. One model is enough.

Export API keys for the providers you declared:

```bash
export ANTHROPIC_API_KEY="..."
# and/or
export GOOGLE_API_KEY="..."
export OPENAI_API_KEY="..."
```

### 4. Use `/dora`

Restart your host session, then invoke:

```text
/dora I want a Skill for managing family recipes and weekly menus.
     Please learn from https://github.com/TandoorRecipes/recipes
     and https://github.com/mealie-recipes/mealie
```

Doramagic runs its 7-phase pipeline and produces a Skill bundle you can install.

## What Doramagic Produces

Every successful run produces exactly these files:

| File | Purpose |
|------|---------|
| `SKILL.md` | Executable instructions that define expert behavior |
| `PROVENANCE.md` | Evidence trail -- every claim traced to source |
| `DSD_REPORT.md` | Deceptive Source Detection results (8 automated checks) |
| `CONFIDENCE_STATS.json` | Per-claim verdict distribution |

Here is what the beginning of a real `SKILL.md` looks like:

```markdown
# Fitness Tracker Advisor

You are an expert advisor on fitness tracking application design,
trained on the design philosophy and community wisdom of wger.

## Core Design Principles

- **Simplicity over features**: wger deliberately limits dashboard widgets
  to 3 per view. Community learned that >5 widgets caused 40% of users
  to stop logging workouts (GitHub Discussion #847).
  [SOURCE: CODE:dashboard/views.py:L42 + COMMUNITY:Discussion#847]
```

If your output does not look like this, Doramagic did not run -- the AI may have fabricated a response from reading this README.

## Usage Examples

Doramagic supports 4 input types, each routed deterministically:

| Route | Example | Behavior |
|-------|---------|----------|
| Direct URL | `/dora https://github.com/fastapi/fastapi` | Skips discovery, extracts directly |
| Named Project | `/dora Extract wisdom from Home Assistant` | Searches GitHub, then extracts |
| Domain Exploration | `/dora What design wisdom can I learn from PKM projects?` | Multi-project discovery + extraction |
| Clarification | `/dora I need something for my team` | Asks clarifying questions first |

## Key Features (v12.1.1)

- **Deterministic Routing DAG** -- 4 input paths with conditional edges
- **Fan-out Extraction** -- Up to 3 isolated RepoWorkers in parallel
- **5-Dimension Quality Gate** -- 60-point threshold with targeted revision
- **4-Tier Degraded Delivery** -- Users always receive output
- **EventBus + Structured Logging** -- `run_events.jsonl` for observability
- **Model-Agnostic** -- Works with any LLM (Claude, Gemini, GPT, Ollama)

## Architecture Overview

```
INIT → PHASE A (Input Router)
         |
    ┌────┴────┐
  CLARIFY   (route)
              |
         PHASE B (GitHub Discovery)
              |
         PHASE C (Fan-out Soul Extraction, up to 3 repos)
              |
         PHASE D (Cross-Project Synthesis)
              |
         PHASE E (Skill Compilation)
              |
         PHASE F (Quality Gate: 5-dim, 60pt threshold)
         /        \
      REVISE     PASS
      (→E)         |
              PHASE G (Package + Deliver)
                 |
               DONE
```

See [INSTALL.md](INSTALL.md) for detailed architecture, configuration, and advanced usage.

## Configuration

### `models.json`

Doramagic routes by **capability**, not by model name:

```json
{
  "available_models": [
    {
      "model_id": "claude-sonnet-4-6",
      "provider": "anthropic",
      "capabilities": ["deep_reasoning", "structured_extraction", "tool_calling"],
      "cost_tier": "medium",
      "api_key_env": "ANTHROPIC_API_KEY"
    }
  ],
  "routing_preference": "lowest_sufficient",
  "fallback_strategy": "degrade_and_warn"
}
```

One model is enough. Adding more improves routing flexibility and cost control.

## Development

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cd Doramagic
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
make test
```

## Project Structure

```
packages/           # Core modules (contracts, controller, executors, extraction, etc.)
bricks/             # 278 knowledge bricks across 34 frameworks/domains
skills/doramagic/   # Self-contained skill bundle (SKILL.md + packages + bricks)
tests/              # Unit + E2E smoke tests
scripts/            # Utility and release scripts
```

## FAQ

### Does Doramagic build an app for me?

No. Doramagic builds a **Skill bundle** that turns your AI assistant into a domain expert.

### Do I need multiple LLM providers?

No. One capable model is enough.

### Can I delete the cloned repo after installation?

Yes. The installed skill directory is self-contained. Your `models.json` is inside the skill directory, not in the cloned repo.

### Where do I find the generated skill bundle?

```text
~/.doramagic/runs/<run-id>/delivery/
```

Copy that directory into your host's skill directory.

## License

[MIT](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and PR guidelines.
