# Contributing to Doramagic

## Getting Started

```bash
git clone https://github.com/tangweigang-jpg/Doramagic.git
cd Doramagic
pip install pydantic
```

## Running Tests

```bash
python -m pytest tests/
```

## Project Structure

- `packages/` — Core Python extraction engine
- `bricks/` — Knowledge bricks (JSONL format)
- `skills/doramagic/` — OpenClaw / Claude Code skill definition
- `tests/` — Test suite
- `scripts/` — Utility scripts

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a PR with a clear description

## Adding Knowledge Bricks

Bricks are JSONL files in `bricks/`. Each line is a JSON object with fields:
- `brick_id` — unique identifier
- `level` — L1 (framework) or L2 (pattern)
- `domain` — framework or domain name
- `knowledge_type` — capability, rationale, constraint, interface, failure, assembly_pattern
- `content` — the knowledge text
- `evidence_url` — documentation reference

## License

MIT
