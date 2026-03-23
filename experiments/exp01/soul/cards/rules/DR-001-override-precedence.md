---
card_type: decision_rule_card
card_id: DR-001
repo: python-dotenv
type: DESIGN_DECISION
title: "Override Precedence -- When .env Wins vs OS Environ"
rule: |
  The `override` flag controls TWO independent behaviors:
  1. In `set_as_environment_variables()`: IF override=False AND key already exists in os.environ, THEN skip (do not overwrite).
  2. In `resolve_variables()`: IF override=True, THEN .env values shadow os.environ during variable interpolation. IF override=False, THEN os.environ shadows .env values.
context: |
  The `override` parameter has different defaults depending on the entry point:
  - `load_dotenv()` defaults to `override=False` (preserves existing env vars)
  - `dotenv_values()` always passes `override=True` (because it returns a dict, not modifying os.environ)
  - `DotEnv.__init__()` defaults to `override=True`
  This asymmetry means that calling `DotEnv` directly vs `load_dotenv()` produces different override behavior by default.
do:
  - "Use override=False (default) when you want existing environment variables to take precedence over .env file"
  - "Use override=True when .env file should be authoritative (e.g., testing)"
  - "Remember that override affects BOTH env-var setting AND variable interpolation resolution"
dont:
  - "Assume override only affects os.environ writes -- it also changes interpolation resolution order"
  - "Assume DotEnv() and load_dotenv() have the same override default"
applies_to_versions: ">=1.0.0"
confidence: 0.95
evidence_level: E5
sources:
  - "src/dotenv/main.py:L97-L110 (set_as_environment_variables override check)"
  - "src/dotenv/main.py:L289-L311 (resolve_variables override merge order)"
  - "src/dotenv/main.py:L383-L430 (load_dotenv defaults override=False)"
  - "src/dotenv/main.py:L433-L467 (dotenv_values always override=True)"
  - "src/dotenv/main.py:L42-L50 (DotEnv.__init__ defaults override=True)"
---

## Detailed Mechanics

### Environment Setting (Step 6 of load flow)

```python
# src/dotenv/main.py:L104-L106
if k in os.environ and not self.override:
    continue
if v is not None:
    os.environ[k] = v
```

Key observations:
- When `override=False` and key exists in `os.environ`, the `.env` value is silently dropped
- When value is `None` (key-only binding), it is NEVER written to `os.environ` regardless of override
- When `override=True`, `.env` always overwrites existing env vars

### Variable Interpolation (Step 4 of resolution flow)

```python
# src/dotenv/main.py:L300-L306
if override:
    env.update(os.environ)
    env.update(new_values)  # .env wins
else:
    env.update(new_values)
    env.update(os.environ)  # os.environ wins
```

The dict merge order determines which source "wins" for variable lookups during `${VAR}` expansion:
- `override=True`: `.env` values (in `new_values`) are applied last, so they override `os.environ`
- `override=False`: `os.environ` is applied last, so it overrides `.env` values
