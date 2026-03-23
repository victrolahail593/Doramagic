# Project Soul: python-dotenv

## What Makes python-dotenv Tick

python-dotenv is a **zero-dependency, single-purpose library** that bridges the gap between file-based configuration (`.env` files) and runtime environment variables (`os.environ`). Its soul can be distilled into three design principles:

### 1. Graceful Degradation Over Strict Failure

The library never crashes on bad input. Missing files silently return empty results. Malformed lines are logged as warnings and skipped. The `PYTHON_DOTENV_DISABLED` env var provides a global kill switch. This philosophy makes it safe to call `load_dotenv()` unconditionally in application startup -- if the `.env` file doesn't exist (e.g., in production with real env vars), nothing breaks.

### 2. Convention Over Configuration

Auto-discovery via `find_dotenv()` walks the directory tree upward -- no path needed. The `override=False` default in `load_dotenv()` means existing env vars take precedence, respecting the 12-factor app principle that the environment is the source of truth. The library "just works" with `load_dotenv()` and no arguments.

### 3. Bash-Compatible but Deliberately Limited

The parser implements a useful subset of Bash syntax (quoting, escapes, `export`, comments, `${VAR:-default}`) without attempting full shell compatibility. Only `${VAR}` syntax (with braces) triggers expansion. Only the `:-` (default) POSIX operator is supported. This constraint keeps the implementation at ~1100 lines while covering >95% of real-world use cases.

## Architecture in One Sentence

`load_dotenv()` -> `find_dotenv()` -> `DotEnv` orchestrator -> `parser.parse_stream()` yields `Binding` tuples -> `resolve_variables()` expands `${VAR}` references -> `os.environ[k] = v`.

## The Override Duality

The most subtle design decision: the `override` flag controls TWO things simultaneously -- whether `.env` values overwrite existing env vars, AND the resolution order during variable interpolation. This dual effect is the single most important thing to understand about python-dotenv's behavior.

---

## Card Index

### Concept Cards (L1 -- WHAT)

| ID | Title | File |
|----|-------|------|
| CC-001 | DotEnv Class -- Core Orchestrator | `cards/concepts/CC-001-dotenv-class.md` |
| CC-002 | Parser -- Hand-Written Recursive Descent .env Lexer | `cards/concepts/CC-002-parser.md` |
| CC-003 | resolve_variables -- POSIX Variable Interpolation Engine | `cards/concepts/CC-003-resolve-variables.md` |

### Workflow Cards (L2 -- HOW)

| ID | Title | File |
|----|-------|------|
| WF-001 | DotEnv Load Flow -- From File to os.environ | `cards/workflows/WF-001-dotenv-load-flow.md` |
| WF-002 | Parsing Flow -- Stream to Bindings | `cards/workflows/WF-002-parsing-flow.md` |
| WF-003 | Variable Resolution Flow -- ${VAR} Expansion | `cards/workflows/WF-003-variable-resolution-flow.md` |

### Decision Rule Cards (L3 -- WHY/WHEN)

| ID | Title | File |
|----|-------|------|
| DR-001 | Override Precedence -- When .env Wins vs OS Environ | `cards/rules/DR-001-override-precedence.md` |
| DR-002 | Quoting Rules -- How Value Quoting Affects Parsing | `cards/rules/DR-002-quoting-rules.md` |
| DR-003 | Interpolation Rules -- ${VAR} Expansion Behavior | `cards/rules/DR-003-interpolation-rules.md` |
| DR-004 | Stream Acquisition Rules -- File vs Stream vs Fallback | `cards/rules/DR-004-stream-acquisition-rules.md` |
| DR-005 | Error Handling Rules -- Graceful Degradation Over Strict Failure | `cards/rules/DR-005-error-handling-rules.md` |

---

## Key Insights

1. **The parser is error-tolerant by design.** Every `parse_binding()` call is wrapped in a try/except that catches regex failures and returns an `error=True` binding. This means malformed lines never halt processing -- the parser always advances to the next line.

2. **Variable resolution is sequential, not declarative.** Variables are resolved in file order, and each resolved value is immediately available to subsequent entries. This means `.env` file ordering matters. There is no cycle detection because there is no recursion -- just a single forward pass.

3. **The `_dict` cache is lazy but not invalidated.** Once `DotEnv.dict()` is called, results are cached in `_dict`. Subsequent calls return the cached dict. There is no mechanism to invalidate or refresh this cache if the underlying file changes.

4. **File rewriting is atomic.** `set_key()` and `unset_key()` use a temp-file-then-rename pattern via `rewrite()`, preserving file modes and handling symlink safety. This is separate from the `DotEnv` class entirely -- it's a standalone utility.

5. **`$VAR` vs `${VAR}` is the biggest user gotcha.** Only `${VAR}` triggers expansion. `$VAR` is treated as literal text. This is by design (simplicity) but catches users who expect shell-like behavior.
