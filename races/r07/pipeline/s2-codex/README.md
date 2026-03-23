# Doramagic Pipeline Bridge

`races/r07/pipeline/s2-codex/` contains the bridge from SKILL.md execution to the deterministic Doramagic Python pipeline.

## Files

- `doramagic_pipeline.py`: end-to-end bridge for Phase C to H
- `multi_extract.py`: concurrent multi-repository extraction helper

## Usage

```bash
python3 races/r07/pipeline/s2-codex/doramagic_pipeline.py \
  --need-profile /path/to/need_profile.json \
  --repos /path/to/repos.json \
  --run-dir /path/to/run_dir \
  --bricks-dir /path/to/bricks \
  --output /path/to/delivery
```

## Behavior

- Reads `need_profile.json` and `repos.json`
- Extracts repositories in parallel into `{run_dir}/extractions/<repo_name>/`
- Builds a minimal `SynthesisInput` from deterministic extraction results
- Runs `run_synthesis()` when at least two repos succeed
- Falls back to best-single-project mode when synthesis is skipped or fails
- Runs `run_skill_compiler()` and then writes the final delivery bundle
- Prints a JSON summary to stdout

## Degradation Rules

- A single repo extraction failure is recorded as a warning and does not abort the run
- If all repos fail, the script exits with code `1`
- If synthesis fails, the pipeline compiles from the best single successful extraction
- If the skill compiler fails, the bridge still writes deterministic `SKILL.md`, `PROVENANCE.md`, and `LIMITATIONS.md`
