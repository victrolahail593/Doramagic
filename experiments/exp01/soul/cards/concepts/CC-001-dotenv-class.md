---
card_type: concept_card
card_id: CC-001
repo: python-dotenv
title: "DotEnv Class -- Core Orchestrator"
---

## Identity

The `DotEnv` class is the central orchestrator of python-dotenv that ties together file/stream acquisition, parsing, variable interpolation, and environment variable injection. It is the single object through which all `.env` processing flows, whether invoked by `load_dotenv()`, `dotenv_values()`, or directly.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A configuration holder and pipeline orchestrator | A parser (delegates to `parser.py`) |
| A lazy-evaluated cache (`_dict` is populated on first `.dict()` call) | A file watcher or live-reload mechanism |
| A bridge between file I/O and `os.environ` | A validator of env var values |
| Capable of reading from both file paths and in-memory streams | A file writer (writing is handled by `set_key`/`unset_key` which bypass `DotEnv`) |
| Stateful -- stores config and caches results | Thread-safe (no locking around `_dict` cache) |

## Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `dotenv_path` | `Optional[StrPath]` | Path to the `.env` file on disk |
| `stream` | `Optional[IO[str]]` | Alternative text stream input |
| `_dict` | `Optional[Dict[str, Optional[str]]]` | Lazy-populated cache of parsed+resolved values |
| `verbose` | `bool` | Controls warning/info log output |
| `encoding` | `Optional[str]` | File encoding (default `utf-8` via callers) |
| `interpolate` | `bool` | Whether to perform `${VAR}` expansion |
| `override` | `bool` | Whether `.env` values override existing env vars |

## Boundaries

**Starts at:** Construction with a path or stream plus configuration flags.

**Core pipeline (4 stages):**
1. `_get_stream()` -- Opens the file/stream (or yields empty StringIO if not found)
2. `parse()` -- Delegates to `parser.parse_stream()`, filters via `with_warn_for_invalid_lines()`, yields `(key, value)` tuples
3. `dict()` -- Collects parse results, optionally passes through `resolve_variables()`, caches in `_dict`
4. `set_as_environment_variables()` -- Iterates `_dict` and writes to `os.environ` respecting `override`

**Delegates to:**
- `parser.py:parse_stream()` for lexing/parsing
- `variables.py:parse_variables()` via `main.py:resolve_variables()` for interpolation
- Standard library `os.environ` for environment mutation

**Does NOT handle:**
- File discovery (`find_dotenv()` is separate)
- File modification (`set_key()`/`unset_key()` are standalone functions)
- CLI concerns

## Evidence

- Class definition: `src/dotenv/main.py:L42-L122` (lines 3848-3929 in packed_full.xml)
- `_get_stream()` context manager: `src/dotenv/main.py:L60-L73`
- `dict()` with caching and interpolation branch: `src/dotenv/main.py:L75-L89`
- `parse()` generator: `src/dotenv/main.py:L91-L95`
- `set_as_environment_variables()` with override check: `src/dotenv/main.py:L97-L110`
- `load_dotenv()` instantiates DotEnv: `src/dotenv/main.py:L383-L430`
- `dotenv_values()` instantiates DotEnv with `override=True`: `src/dotenv/main.py:L433-L467`
