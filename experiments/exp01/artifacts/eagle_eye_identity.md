# Eagle Eye Identity: python-dotenv

## Project Identity

**What it is:** A Python library (v1.2.2, BSD-3-Clause) that reads key-value pairs from `.env` files and sets them as environment variables.

**What it does:** Parses `.env` files with Bash-like syntax (supporting quoting, escape sequences, comments, `export` prefix, multiline values, and POSIX variable expansion), loads them into `os.environ`, and provides a CLI for manipulating `.env` files. Also supports reading from streams and FIFOs.

**Who uses it:** Python developers building 12-factor applications who need to manage configuration via environment variables across development, staging, and production environments. ~3500 GitHub stars, downloaded millions of times monthly from PyPI.

**Design philosophy:** Zero runtime dependencies for the core library (click is optional for CLI). Single-purpose, small footprint (~1100 lines). Favors convention over configuration -- auto-discovers `.env` files by walking up the directory tree.

## Core Concepts

### 1. `load_dotenv` -- Primary User-Facing Function
The main entry point for loading `.env` files into `os.environ`. Supports `override`, `interpolate`, `encoding`, `verbose` parameters. Auto-discovers `.env` via `find_dotenv()` when no path given. Can be disabled via `PYTHON_DOTENV_DISABLED` env var.
- **Ref:** `main.py:383-430`

### 2. `dotenv_values` -- Dict-Based Access
Returns parsed `.env` content as `Dict[str, Optional[str]]` without modifying `os.environ`. Enables advanced patterns like merging multiple `.env` files with environment precedence.
- **Ref:** `main.py:433-467`

### 3. `DotEnv` Class -- Core Engine
The central orchestrator that ties together stream acquisition, parsing, interpolation, and environment variable setting. Holds configuration state (path, stream, encoding, interpolate, override) and caches results in `_dict`.
- **Ref:** `main.py:42-122`

### 4. Parser (`parse_stream` / `Binding` / `Reader`)
A hand-written recursive-descent parser that tokenizes `.env` content into `Binding(key, value, original, error)` tuples. Handles single-quoted, double-quoted, and unquoted values with different escape rules. The `Reader` class wraps a stream into a position-tracked string scanner.
- **Ref:** `parser.py:40-182`

### 5. Variable Interpolation (`resolve_variables` / `parse_variables`)
POSIX-style `${VAR}` and `${VAR:-default}` expansion. `parse_variables` tokenizes value strings into `Atom` sequences (Literal/Variable). `resolve_variables` in main.py determines resolution order based on `override` flag.
- **Ref:** `variables.py:70-86` (parsing), `main.py:289-311` (resolution)

### 6. `find_dotenv` -- File Discovery
Walks up the directory tree from the caller's location to find a `.env` file. Detects interactive mode (REPL, IPython, debugger) and uses cwd in those cases. Uses frame introspection (`sys._getframe()`) to find the caller's directory.
- **Ref:** `main.py:332-380`

### 7. File Rewriting (`set_key` / `unset_key` / `rewrite`)
Atomic file modification using temp-file-then-rename pattern. Preserves original file mode. Handles symlink safety (no follow by default). `set_key` replaces or appends bindings; `unset_key` removes them.
- **Ref:** `main.py:138-286`

### 8. CLI (`cli.py`)
Click-based command group with subcommands: `list`, `get`, `set`, `unset`, `run`. The `run` command executes a subprocess with loaded env vars (uses `execvpe` on Unix, `Popen` on Windows).
- **Ref:** `cli.py:38-247`

### 9. Override Behavior
Controls whether `.env` values take precedence over existing environment variables. Affects both `set_as_environment_variables` (main.py:104-106) and variable interpolation resolution order (main.py:301-306). Default is `override=False` for `load_dotenv`, `override=True` for `dotenv_values`.
- **Ref:** `main.py:97-110`, `main.py:289-311`

### 10. IPython Integration
Registers a `%dotenv` magic command via `IPythonDotEnv` class. Supports `-o` (override) and `-v` (verbose) flags. Loaded via `%load_ext dotenv`.
- **Ref:** `ipython.py:1-50`, `__init__.py:6-9`
