---
card_type: decision_rule_card
card_id: DR-005
repo: python-dotenv
type: DESIGN_DECISION
title: "Error Handling Rules -- Graceful Degradation Over Strict Failure"
rule: |
  IF a line fails to parse, THEN return Binding(error=True) and continue parsing remaining lines.
  IF the .env file is missing, THEN return empty results (no exception unless raise_error_if_not_found=True in find_dotenv).
  IF PYTHON_DOTENV_DISABLED is set to a truthy value, THEN skip loading entirely and return False.
  Parse errors are logged as warnings, not raised as exceptions.
context: |
  python-dotenv follows a "best effort" philosophy. In production, a malformed line in .env should not crash the application. The parser's error recovery mechanism (catch Error, consume rest-of-line, mark as error=True) ensures the maximum number of valid bindings are extracted even from partially malformed files.
do:
  - "Check return value of load_dotenv() to know if any vars were loaded"
  - "Enable logging at WARNING level to see parse errors"
  - "Use verbose=True to see file-not-found messages"
dont:
  - "Assume all lines in .env were successfully parsed -- check logs for warnings"
  - "Expect exceptions from malformed .env files -- they are silently degraded"
  - "Rely on load_dotenv() raising on missing files -- it returns False by default"
applies_to_versions: ">=0.9.0"
confidence: 0.90
evidence_level: E5
sources:
  - "src/dotenv/parser.py:L168-L175 (Error catch and recovery in parse_binding)"
  - "src/dotenv/main.py:L32-L39 (with_warn_for_invalid_lines logging)"
  - "src/dotenv/main.py:L60-L73 (_get_stream silent fallback)"
  - "src/dotenv/main.py:L389-L393 (PYTHON_DOTENV_DISABLED check)"
  - "src/dotenv/main.py:L332-L380 (find_dotenv raise_error_if_not_found)"
---

## Error Propagation Chain

```
Parser level:
  regex mismatch -> raise Error
  parse_binding catches Error -> Binding(error=True)

Main level:
  with_warn_for_invalid_lines -> logger.warning() + yield binding
  parse() -> filters out bindings where key is None

User level:
  load_dotenv() -> returns False if no vars set
  find_dotenv() -> returns "" if not found (unless raise_error_if_not_found=True)
```

### Truthy Values for PYTHON_DOTENV_DISABLED

```python
# src/dotenv/main.py:L28-L29
value = os.environ["PYTHON_DOTENV_DISABLED"].casefold()
return value in {"1", "true", "t", "yes", "y"}
```

Case-insensitive. Only these specific strings disable loading.
