---
card_type: decision_rule_card
card_id: DR-004
repo: python-dotenv
type: DESIGN_DECISION
title: "Stream Acquisition Rules -- File vs Stream vs Fallback"
rule: |
  IF dotenv_path is provided AND path is a regular file or FIFO, THEN open it with the given encoding.
  ELSE IF stream is provided, THEN use it directly.
  ELSE yield empty StringIO("") and optionally log a warning (if verbose=True).
  Priority: dotenv_path > stream > empty fallback.
context: |
  The _get_stream() context manager implements a three-tier fallback. The FIFO support (added in v1.2.1) allows reading .env content from named pipes, enabling dynamic secret injection. The silent fallback to empty StringIO means missing .env files are not errors by default -- this is intentional for production environments where env vars may come from other sources.
do:
  - "Pass verbose=True during development to get warnings about missing .env files"
  - "Use stream parameter for testing or when .env content comes from non-file sources"
  - "Use FIFO support for dynamic/ephemeral secrets that should not persist on disk"
dont:
  - "Assume a missing .env file will raise an error -- it silently returns empty"
  - "Pass both dotenv_path and stream expecting stream to be used -- path takes priority"
applies_to_versions: ">=1.2.1"
confidence: 0.95
evidence_level: E5
sources:
  - "src/dotenv/main.py:L60-L73 (_get_stream context manager)"
  - "src/dotenv/main.py:L470-L482 (_is_file_or_fifo helper)"
---

## Decision Tree

```
_get_stream():
  IF dotenv_path AND _is_file_or_fifo(dotenv_path):
    -> open(dotenv_path, encoding=self.encoding)
  ELIF stream is not None:
    -> yield stream
  ELSE:
    -> IF verbose: log warning
    -> yield StringIO("")
```

### _is_file_or_fifo()

```python
# src/dotenv/main.py:L470-L482
def _is_file_or_fifo(path):
    if os.path.isfile(path):
        return True
    try:
        st = os.stat(path)
    except (FileNotFoundError, OSError):
        return False
    return stat.S_ISFIFO(st.st_mode)
```

This two-step check first tries the fast `isfile()` path, then falls back to `stat()` for FIFO detection.
