# Eagle Eye Soul Locus: python-dotenv

## Scoring Methodology

Each locus is scored on 8 weighted dimensions (total = 100):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Domain Centrality (DC) | 20% | How central to the project's core purpose |
| Execution Influence (EI) | 15% | Impact on runtime behavior |
| Orchestration Power (OP) | 15% | Coordinates multiple components |
| Data/State Gravity (DSG) | 15% | Controls key data structures or state |
| Rule Density (RD) | 10% | Concentration of business rules/logic |
| Boundary Importance (BI) | 10% | Manages external interfaces (fs, env, user) |
| Cross-Module Bridge (CMB) | 10% | Connects different modules together |
| Concept Density (CD) | 5% | Number of distinct concepts per line |

Scores are 0-100 per dimension, then weighted.

## Scored Loci

### 1. `DotEnv` class (`main.py:42-122`)
The central orchestrator that binds stream handling, parsing, interpolation, caching, and environment mutation.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 95 | 90 | 95 | 90  | 60 | 80 | 90  | 80 | **88.3** |

- DC: Core abstraction representing a .env file's parsed state
- EI: Every load/values call flows through this class
- OP: Coordinates _get_stream -> parse_stream -> resolve_variables -> os.environ
- DSG: Owns `_dict` cache, configuration state
- RD: Moderate -- override logic, verbose logging
- BI: Opens files, writes to os.environ
- CMB: Bridges parser.py, variables.py, and os.environ
- CD: 6 concepts in 80 lines (stream mgmt, parsing, caching, interpolation, env-setting, key lookup)

---

### 2. `parse_stream` / `parse_binding` / `Reader` (`parser.py:69-182`)
The parsing engine that converts raw .env text into structured Binding tuples.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 90 | 85 | 70 | 75  | 95 | 50 | 60  | 95 | **79.0** |

- DC: Parsing is the foundational operation -- without it nothing works
- EI: Every .env file goes through this code path
- OP: Moderate -- coordinates regex matchers and Reader state
- DSG: Reader holds string + position state; produces Binding tuples
- RD: Highest rule density in codebase -- 13 regex patterns, quoting rules, escape handling
- BI: Low -- reads from already-opened stream
- CMB: Consumed only by main.py
- CD: Parser, Reader, Position, Binding, Original, escapes, quoting modes in 113 lines

---

### 3. `resolve_variables` (`main.py:289-311`)
Determines variable interpolation order based on override semantics, bridging parser output with variable expansion.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 85 | 80 | 80 | 70  | 85 | 60 | 85  | 70 | **78.3** |

- DC: Variable expansion is a key differentiator of the library
- EI: Controls the final resolved values for every interpolated variable
- OP: Orchestrates parse_variables + Atom.resolve + env precedence
- DSG: Builds and returns the final resolved dict
- RD: Override/no-override precedence rules, null handling
- BI: Reads from os.environ
- CMB: Bridges variables.py atoms with main.py's DotEnv context
- CD: Override logic, env merging, atom resolution in 23 lines

---

### 4. `load_dotenv` (`main.py:383-430`)
The primary user-facing function that ties everything together.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 90 | 90 | 85 | 50  | 55 | 75 | 70  | 50 | **75.5** |

- DC: The function most users call; the library's raison d'etre
- EI: Triggers the entire load pipeline
- OP: Coordinates find_dotenv -> DotEnv -> set_as_environment_variables
- DSG: Low -- delegates to DotEnv for state
- RD: Moderate -- disabled check, auto-find logic
- BI: Entry point from user code
- CMB: Connects find_dotenv with DotEnv
- CD: Moderate -- thin wrapper

---

### 5. `find_dotenv` (`main.py:332-380`)
File discovery with smart caller detection (interactive mode, debugger, frame introspection).

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 70 | 65 | 60 | 30  | 80 | 85 | 40  | 75 | **63.0** |

- DC: Important but auxiliary -- finding the file is a precondition, not the core purpose
- EI: Determines which file gets loaded
- OP: Moderate -- coordinates _walk_to_root, _is_interactive, _is_debugger
- DSG: Stateless
- RD: High -- interactive detection, debugger detection, frame walking, frozen app handling
- BI: Heavy filesystem interaction, sys._getframe introspection
- CMB: Low -- self-contained utility
- CD: 5 concepts in 48 lines

---

### 6. `parse_variables` / `Atom` / `Variable` / `Literal` (`variables.py:1-86`)
POSIX variable expansion type system and parser.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 75 | 60 | 30 | 50  | 70 | 20 | 50  | 80 | **54.5** |

- DC: Variable interpolation is a significant feature
- EI: Only activated when interpolate=True
- OP: Low -- linear tokenization, no orchestration
- DSG: Defines Atom type hierarchy
- RD: POSIX regex, default value handling
- BI: None -- pure computation
- CMB: Consumed by resolve_variables in main.py
- CD: Abstract class hierarchy, regex, iterator protocol in 86 lines

---

### 7. `set_key` / `unset_key` / `rewrite` (`main.py:138-286`)
Atomic file modification with symlink safety and mode preservation.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 60 | 55 | 65 | 40  | 75 | 90 | 55  | 65 | **62.0** |

- DC: Write operations are secondary to the read-oriented core purpose
- EI: Only affects mutation use cases
- OP: Coordinates rewrite context, parse_stream, file writing
- DSG: Manages temp files and file modes
- RD: Quote mode logic, symlink handling, newline edge cases, mode preservation
- BI: Highest boundary importance -- filesystem writes, temp files, os.replace
- CMB: Uses parser.py; consumed by cli.py
- CD: Atomic rewrite, quoting, export prefix, symlink safety

---

### 8. CLI (`cli.py:38-247`)
Click-based command-line interface for .env manipulation.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 40 | 45 | 55 | 30  | 50 | 80 | 45  | 40 | **48.0** |

- DC: Optional feature (separate extra), not the core library purpose
- EI: Only activated via CLI invocation
- OP: Moderate -- coordinates multiple subcommands
- DSG: Passes through to main.py for state
- RD: Moderate -- output format handling, override flag
- BI: User-facing CLI, process execution (execvpe/Popen)
- CMB: Consumes main.py functions
- CD: Standard Click patterns

---

### 9. `__init__.py` (`__init__.py:1-51`)
Public API surface and re-exports.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 50 | 30 | 30 | 10  | 15 | 60 | 65  | 20 | **35.5** |

- DC: Defines what the library exposes but contains minimal logic
- EI: Low -- pure re-exports
- OP: Low
- DSG: No state
- RD: Only `get_cli_string` has logic
- BI: Package boundary for users
- CMB: Bridges main.py to external consumers
- CD: Low

---

### 10. IPython Integration (`ipython.py:1-50`)
Magic command for Jupyter/IPython environments.

| DC | EI | OP | DSG | RD | BI | CMB | CD | **Weighted** |
|----|----|----|-----|----|----|-----|----|-------------|
| 30 | 25 | 30 | 10  | 25 | 50 | 30  | 30 | **29.0** |

- DC: Niche feature for a subset of users
- EI: Only in IPython contexts
- OP: Low -- delegates to load_dotenv/find_dotenv
- DSG: No state
- RD: Argument parsing for magic
- BI: IPython API integration
- CMB: Thin wrapper over main.py
- CD: Low

---

## Ranked Summary

| Rank | Locus | Score | File:Lines |
|------|-------|-------|------------|
| 1 | `DotEnv` class | **88.3** | `main.py:42-122` |
| 2 | Parser (`parse_stream`/`Reader`/`Binding`) | **79.0** | `parser.py:69-182` |
| 3 | `resolve_variables` | **78.3** | `main.py:289-311` |
| 4 | `load_dotenv` | **75.5** | `main.py:383-430` |
| 5 | `find_dotenv` | **63.0** | `main.py:332-380` |
| 6 | `set_key`/`unset_key`/`rewrite` | **62.0** | `main.py:138-286` |
| 7 | `parse_variables`/Atom hierarchy | **54.5** | `variables.py:1-86` |
| 8 | CLI | **48.0** | `cli.py:38-247` |
| 9 | `__init__.py` | **35.5** | `__init__.py:1-51` |
| 10 | IPython Integration | **29.0** | `ipython.py:1-50` |

**Calibration check:** 4 out of 10 loci (40%) score below 70: `parse_variables` (54.5), CLI (48.0), `__init__.py` (35.5), IPython (29.0). Meets the >30% requirement.

## Deep Dive Queue

The top 3 loci are selected for Deep Dive (Phase 2) based on their weighted scores and the density of concepts that benefit from detailed extraction:

| Priority | Locus | Score | Rationale |
|----------|-------|-------|-----------|
| **L1** | `DotEnv` class | 88.3 | Highest score. Central orchestrator -- understanding its state management, stream handling, and delegation patterns is essential for complete soul extraction. |
| **L2** | Parser (`parse_stream`/`Reader`) | 79.0 | Highest rule density in the codebase. The 13 regex patterns, quoting modes, escape handling, and error recovery contain the most concentrated domain logic. |
| **L3** | `resolve_variables` | 78.3 | Critical bridge between parser output and final values. Override semantics and env-precedence logic are the most nuanced behavioral rules in the library. |
