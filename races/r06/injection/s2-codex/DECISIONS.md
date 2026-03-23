# Brick Injection Decisions

## Scope

This implementation is fully deterministic. It reads curated JSONL bricks, validates every row against `DomainBrick`, writes merged bricks to `artifacts/domain_bricks.jsonl`, and renders prompt-ready baseline knowledge text.

## Decisions

- Validate on read. Every JSONL row is parsed with `DomainBrick.model_validate_json()`. Corrupt JSON and schema-invalid rows are skipped instead of leaking malformed data downstream.
- Deduplicate by source file, not by framework name. `FastAPI` and `Flask` intentionally share `fastapi_flask.jsonl`; the file is loaded once while both frameworks are still reported as matched.
- Preserve input order. Framework matching and merged brick ordering follow the caller's framework list, while brick ordering inside each file stays as curated in the JSONL source.
- Write the artifact whenever `output_dir` is provided, even if zero bricks are selected. This keeps downstream orchestration idempotent and removes "file missing vs empty selection" ambiguity.
- Keep prompt text compact. The injection text includes one line per brick with a normalized domain label and whitespace-condensed statement, truncated deterministically to avoid runaway prompt size.
