# Phase Runner Decisions

## Scope

This runner only orchestrates deterministic and adapter-mediated stages. It does not execute the OpenClaw prompt-driven Stage 1/2/3/4 steps itself.

## Decisions

- Enrich old `repo_facts.json` in place. The current CLI script still emits a legacy payload, so the runner merges in deterministic Stage 0 fields like `frameworks`, `languages`, `entrypoints`, `dependencies`, and `repo_summary` before downstream stages use the artifact.
- Skip Stage 1.5 unless structured Stage 1 output exists. The runner looks for a full `stage1_scan_output.json` or split `stage1_findings.json` and `hypothesis_list.json`. If hypotheses are absent, Stage 1.5 is skipped instead of forcing the agent loop to fail on empty input.
- Persist confidence annotations back into card frontmatter. `run_evidence_tagging()` only mutates in-memory dicts, but `compile_knowledge()` reads markdown files from disk. The runner therefore rewrites card frontmatter with `evidence_tags`, `verdict`, and `policy_action` before Stage 4.5.
- Treat validation as the hard gate. If validation does not pass, Stage 4.5 and Stage 5 are skipped. Other Stage 3.5 substeps may still run so the user gets as much diagnostic output as possible.
- Let assembly run even if Stage 4.5 fails. `assemble_output.py` already falls back from `compiled_knowledge.md` to `expert_narrative.md`, so compile failure should not automatically suppress final packaging.
