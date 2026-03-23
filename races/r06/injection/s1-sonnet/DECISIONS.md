# DECISIONS.md — S1-Sonnet Brick Injection (Race E)

## Summary

Implemented `brick_injection.py`: pure deterministic mechanism to load framework bricks from `bricks/*.jsonl` and generate injection text for Stage 1/2/3 prompts. No LLM calls.

---

## Decision 1: Matching Strategy — Two-Level Lookup

**Decision**: Use a two-level matching strategy: exact dict lookup first, then substring scan.

**Rationale**:
- `repo_facts.frameworks` produces names like `"Django"`, `"FastAPI"`, `"Go module"` — not always the same as filenames.
- A static dict (`_FRAMEWORK_TO_BRICK_FILE`) covers all known mappings explicitly. This is deterministic and fast.
- Substring scan (`_FRAMEWORK_SUBSTRING_MAP`) handles edge cases (e.g. `"Go module"` → `"go_general"`) without blowing up the dict.
- For unknown frameworks, we return a slug candidate (lowercased, underscored) and let the file-existence check fail gracefully — no crash.

**Alternative rejected**: Regex-based matching. Overkill for 12 files. The static dict is clearer and easier to audit.

---

## Decision 2: FastAPI + Flask Deduplication

**Decision**: Track loaded file paths in a `loaded_files: set[str]` to avoid loading `fastapi_flask.jsonl` twice when both `FastAPI` and `Flask` appear in `frameworks`.

**Rationale**:
- Both frameworks share one JSONL file by design (from Race B).
- Loading it twice would double-count bricks in `domain_bricks.jsonl` and inflate `bricks_loaded`.
- Set-based dedup is O(1) and zero complexity.

**Edge case handled**: Even when the file is skipped on second load, the framework name is still recorded in `frameworks_matched` (if the file exists) or `frameworks_not_matched`, so callers get accurate diagnostics.

---

## Decision 3: Graceful Degradation — No Crash on Missing Bricks

**Decision**: Missing files, empty files, corrupt JSON lines, and unknown frameworks all return 0 bricks and empty injection text. No exception raised.

**Rationale**:
- This is a pre-processing step. If bricks are missing, extraction continues — just without the baseline hint.
- Crashing Stage 1 because a brick file is absent would be disproportionate.
- Each failure mode is handled at the smallest scope: `_load_bricks_from_file` catches `OSError` and `JSONDecodeError` per-line.

**What's logged**: `frameworks_not_matched` field in `BrickInjectionResult` — callers can inspect/log this if needed.

---

## Decision 4: Injection Text Format

**Decision**: Use the exact format specified in BRIEF.md, with one addition — statement truncation at 200 characters.

```
你已经知道以下框架基线知识（来自 Doramagic 积木库）：

[Django] Django uses MTV, not MVC...
[React]  Hooks must be called at the top level.

你的任务是发现这个具体项目在基线之上的独特做法。不要重复以上知识。
```

**Truncation rationale**: Some brick statements are 400–800 characters (L2 bricks with UNSAID context). Injecting them verbatim would blow prompt budgets. 200 chars preserves the key fact while staying token-efficient. The LLM has the full brick in `domain_bricks.jsonl` if it needs to reference it.

**Label derivation**: `domain_id` field is used as the label. `domain-` prefix is stripped and the result is title-cased so `[domain-pkm]` becomes `[Pkm]` — cleaner for the LLM reader.

---

## Decision 5: output_dir=None Is Valid

**Decision**: `output_dir=None` means "don't write any file". `bricks_path` in the result is `None`.

**Rationale**:
- Not all callers need file output (e.g., in-memory pipeline tests, or Stage 1 that reads bricks directly from `raw_bricks`).
- Forcing a write would require a temp dir and complicate tests.
- The `raw_bricks: list[dict]` field in the result provides direct access without file I/O.

---

## Decision 6: raw_bricks Field in Result

**Decision**: Return the loaded bricks as `raw_bricks: list[dict]` (plain dicts, not pydantic models).

**Rationale**:
- Pydantic validation is not required here — we're a pass-through loader, not a validator.
- The bricks already validated when they were written by Race B's `brick_forge.py`.
- Returning dicts keeps the module dependency-free from `doramagic_contracts` at runtime (contracts import is best-effort via `try/except`).
- Callers that need `DomainBrick` objects can construct them: `DomainBrick(**brick_dict)`.

---

## Decision 7: No Dependency on doramagic_contracts at Runtime

**Decision**: The `DomainBrick` import is wrapped in a `try/except ImportError`. The module works without the contracts package installed.

**Rationale**:
- This is a race deliverable that must run standalone.
- The contracts package is a development dependency, not always on `sys.path` in every environment.
- Pure dict handling is sufficient for loading + writing JSONL.

---

## File Structure

```
races/r06/injection/s1-sonnet/
├── brick_injection.py          # Main module
├── DECISIONS.md                # This file
└── tests/
    └── test_brick_injection.py # 25+ test cases
```

---

## Test Coverage

| Category | Test Count |
|----------|------------|
| `_normalize_framework_name` | 4 |
| `_resolve_brick_filename` | 7 |
| `_load_bricks_from_file` | 5 |
| `_generate_injection_text` | 7 |
| `_write_merged_bricks` | 5 |
| `load_and_inject_bricks` (integration) | 14 |
| Real bricks (if available) | 5 |
| **Total** | **47** |

Tests use `pytest` fixtures (`tmp_path`, `tmp_bricks_dir`, `real_bricks_dir`). Real-brick tests auto-skip if the `bricks/` directory is not found.
