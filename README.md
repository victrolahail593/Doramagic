# Doramagic

[![CI](https://github.com/tangweigang-jpg/Doramagic/actions/workflows/ci.yml/badge.svg)](https://github.com/tangweigang-jpg/Doramagic/actions/workflows/ci.yml)

> **"Don't teach the user what to do -- give them the tool."** -- Doramagic's design philosophy, inspired by Doraemon.

Doramagic extracts the **soul** of open-source projects -- not just what the code does, but *why* it was designed that way and the hard-won community wisdom that never appears in documentation. The extracted knowledge is compiled into injectable advisor packs that make AI assistants deeply understand a project's design philosophy, mental models, and community pitfalls.

## Key Features (v12.1.1)

- **Deterministic Routing DAG** -- 4 input paths (direct URL, named project, domain exploration, low-confidence clarification) with lambda-driven conditional edges replacing the old linear pipeline
- **Fan-out Extraction** -- Up to 3 isolated RepoWorkers run in parallel with independent budgets and timeouts
- **5-Dimension Quality Gate** -- 60-point threshold (Coverage / Evidence / DSD / WHY / Substance) with targeted single-section revision
- **4-Tier Degraded Delivery** -- Users always receive output: FULL_SKILL > PARTIAL_SOULS > FAST_PATH > TEMPLATE
- **EventBus + Structured Logging** -- `run_events.jsonl` for observability and `/dora-status` queries
- **Model-Agnostic Architecture** -- Works with any LLM (Claude, Gemini, GPT, Ollama). Capability routing picks the cheapest model that satisfies each task's requirements

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git ~/Doramagic
cd ~/Doramagic
```

Copy the example model configuration and edit it with your available models:

```bash
cp models.json.example models.json
# Edit models.json -- declare the models you have access to
```

Export API keys for the providers you want to use:

```bash
export ANTHROPIC_API_KEY="..."
# and/or
export GOOGLE_API_KEY="..."
export OPENAI_API_KEY="..."
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

### 3. Use `/dora`

Restart your host session, then invoke:

```text
/dora I want a Skill for managing family recipes and weekly menus.
     Please learn from https://github.com/TandoorRecipes/recipes
     and https://github.com/mealie-recipes/mealie
```

Doramagic will run its 7-phase pipeline and produce a Skill bundle you can install.

## Usage Examples

Doramagic supports 4 input types, each routed deterministically:

### Direct URL (skips discovery)
```text
/dora https://github.com/fastapi/fastapi
```

### Named Project (searches GitHub)
```text
/dora Extract wisdom from Home Assistant
```

### Domain Exploration (multi-project)
```text
/dora I want to build a personal knowledge management tool.
     What design wisdom can I learn from the best open-source PKM projects?
```

### Clarification (low-confidence input)
```text
/dora I need something for my team
```
Doramagic will ask clarifying questions before proceeding.

## Architecture

```
         INIT
          |
       PHASE A ---- Need Profile + Input Router
       /    \
  CLARIFY  (route)
             |
          PHASE B ---- GitHub Discovery (skipped for DIRECT_URL)
             |
          PHASE C ---- Fan-out RepoWorkers (up to 3 parallel)
             |
          PHASE D ---- Cross-Project Synthesis
             |
          PHASE E ---- Skill Compilation
             |
          PHASE F ---- Quality Gate (5-dim, 60pt threshold)
          /     \
      REVISE   PASS
      (->E)      |
              PHASE G ---- Package + Deliver
                 |
               DONE

      Any phase can degrade --> DEGRADED (partial delivery)
```

### Conditional Edge FSM

State transitions are driven by lambda predicates over an `EdgeContext` snapshot:

```python
Phase.PHASE_A: [
    (lambda ctx: ctx.routing_route == "LOW_CONFIDENCE", Phase.PHASE_A_CLARIFY),
    (lambda ctx: ctx.routing_route == "DIRECT_URL",     Phase.PHASE_C),
    (lambda ctx: ctx.routing_route in ("NAMED_PROJECT", "DOMAIN_EXPLORE"), Phase.PHASE_B),
    (lambda ctx: True, Phase.PHASE_B),  # fallback
]
```

### Inside Phase C (Soul Extraction per Repo)

```
Stage 0:   Deterministic extraction (repo_facts.json)
Stage 0.5: Brick injection (framework baseline knowledge)
Stage 1:   Soul discovery (Q1-Q7 + WHY recoverability)
Stage 1.5: Agentic exploration (hypothesis-driven deep dive)
Stage 2:   Concept extraction (CC-* cards)
Stage 3:   Rule extraction (DR-* cards)
Stage 3.5: Confidence tagging + DSD (8 deceptive source checks)
Stage 4.5: Knowledge Compiler (type-routed formatting)
Stage 5:   Assembly
```

## Deliverables

Every successful run produces a Skill bundle:

| File | Purpose |
|------|---------|
| `SKILL.md` | Executable instructions that define expert behavior |
| `PROVENANCE.md` | Evidence trail -- every claim traced to source |
| `DSD_REPORT.md` | Deceptive Source Detection results (8 automated checks) |
| `CONFIDENCE_STATS.json` | Per-claim verdict distribution (SUPPORTED/CONTESTED/WEAK/REJECTED) |

### Confidence Verdicts

Every extracted knowledge claim carries an evidence-chain verdict:

- **SUPPORTED** (CODE + DOC) -- core truth, inject confidently
- **CONTESTED** (COMMUNITY only) -- unsaid knowledge, annotate source
- **WEAK** (INFERENCE + corroboration) -- speculative, mark as such
- **REJECTED** (INFERENCE only) -- quarantined, excluded from output

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
packages/
├── contracts/        # Pydantic schemas (the foundation)
├── controller/       # FlowController, InputRouter, EventBus, StateMachine
├── executors/        # Phase executors (NeedProfileBuilder, WorkerSupervisor, etc.)
├── extraction/       # Stage 0-5 extraction pipeline
├── orchestration/    # Phase Runner, assembly, validation
├── shared_utils/     # LLMAdapter + CapabilityRouter
├── cross_project/    # Compare + synthesis + discovery
├── skill_compiler/   # OpenClaw skill compilation
├── community/        # Community signal harvesting
├── domain_graph/     # Domain snapshot builder
└── platform_openclaw/ # Platform validation

bricks/               # 278 knowledge bricks across 34 frameworks/domains
skills/doramagic/     # Self-contained skill bundle (SKILL.md + packages + bricks)
tests/                # Unit + E2E smoke tests (26 tests)
scripts/              # Utility and release scripts
```

## License

[MIT](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and PR guidelines.
