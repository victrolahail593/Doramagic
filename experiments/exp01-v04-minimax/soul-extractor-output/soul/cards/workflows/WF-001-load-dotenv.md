# Workflow Card: Loading .env File

**Card ID:** WF-001  
**Type:** Workflow  
**Repository:** python-dotenv  

## Overview

The core workflow of loading environment variables from a `.env` file into the Python process.

## Steps

```
┌─────────────────┐
│ 1. Find .env    │
│ find_dotenv()   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Open File    │
│ DotEnv._get_stream│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Parse        │
│ parser.parse_stream│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Expand Vars  │
│ variables.py    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Set Env     │
│ os.environ[key]=│
└────────────────1─┘
```

. **Find .env:** Search from current directory upward, check `usecwd`, respect symlink non-following
2. **Open File:** Use provided path or stream, handle encoding, create empty StringIO if missing
3. **Parse:** Tokenize line-by-line, handle quotes/escapes/comments, yield Bindings
4. **Expand:** Resolve `${VAR}` references using current environment
5. **Set Env:** Update `os.environ` with parsed values (respects `override` flag)

## Failure Modes

| Failure | Cause | Handling |
|---------|-------|----------|
| File not found | No .env in search path | Warning if `verbose=True` |
| Permission denied | File mode too restrictive | Raise `PermissionError` |
| Invalid syntax | Malformed line in .env | Skip, log warning, set `error=True` on Binding |
| Circular reference | `A=$B`, `B=$A` | Empty string result |
| Missing variable | `${NONEXISTENT}` | Use default or empty string |
