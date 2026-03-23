# S2-Codex Decisions

## 1. Keep the package implementation canonical

- Real logic lives in `packages/extraction/doramagic_extraction/stage15_agentic.py`.
- The race directory exposes a thin wrapper instead of a forked copy.
- Reason: orchestration and repo tests already import the package module; duplicating logic would create drift immediately.

## 2. Preserve the old deterministic path as the hard fallback

- `adapter=None`
- `router=None`
- all tools disabled

In those cases the module falls back to the previous deterministic Stage 1 evidence replay.

Reason:

- The brief explicitly requires mock fallback.
- Existing tests already lock envelope semantics, artifact names, and budget behavior.
- This keeps Stage 1.5 usable even when no live model/runtime is configured.

## 3. Route by capability, not by provider

- Stage 1.5 asks the router for `tool_calling` + `code_understanding`.
- The module never imports provider SDKs directly.
- All LLM interaction goes through `LLMAdapter.generate_with_tools(...)`.

Reason:

- This satisfies the model-agnostic constraint in the brief.
- Prompt-based tool fallback remains delegated to `LLMAdapter`, not reimplemented locally.

## 4. Implement repo tools as deterministic local functions

Implemented tools:

- `tool_list_tree`
- `tool_search_repo`
- `tool_read_file`
- `tool_read_artifact`
- `tool_append_finding`

Reason:

- Tool execution must be trustworthy and testable.
- The LLM decides *what* to inspect; Python decides *how* the repo is actually read.

## 5. Append claims incrementally, then reconcile at finalize time

- `append_finding` writes to `claim_ledger.jsonl` immediately.
- Finalization rewrites the ledger if the on-disk row count diverges from in-memory state.

Reason:

- This preserves the "real agent loop" feel of incremental ledger writes.
- It still guarantees deterministic artifacts after degraded/failure paths.

## 6. Define information gain conservatively

Information gain is counted when at least one of these happens:

- a tool produces a new file:line evidence key
- a claim is resolved as `confirmed` or `rejected`
- `append_finding` records evidence that was not already seen

Reason:

- This matches the brief's stop condition around "no information gain".
- It avoids infinite loops caused by repeated tree reads or repeated empty searches.

## 7. Canonical tests stay under `packages/extraction/tests`

Canonical tests:

- `packages/extraction/tests/test_stage15_agentic.py`
- `packages/extraction/tests/test_stage15_integration.py`

Canonical fixture:

- `data/fixtures/stage15_wifi_repo/`

Reason:

- Creating another `races/.../tests/test_stage15_agentic.py` would collide with pytest module discovery because the repo already has that basename.
- Keeping the executable tests in the package test tree avoids import-mismatch failures while still satisfying the brief's coverage goals.
