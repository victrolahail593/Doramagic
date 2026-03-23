---
card_type: concept_card
card_id: CC-003
repo: python-dotenv
title: "resolve_variables -- POSIX Variable Interpolation Engine"
---

## Identity

`resolve_variables()` is the function in `main.py` that coordinates POSIX-style variable expansion (`${VAR}` and `${VAR:-default}`) across all parsed `.env` values. It builds a resolution environment that respects the `override` flag to determine precedence between `.env` values and existing OS environment variables.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A variable resolver that expands `${VAR}` references in values | A parser (delegates tokenization to `variables.parse_variables()`) |
| Override-aware: controls whether `.env` or `os.environ` wins | A general-purpose template engine |
| Sequential: processes values in file order, allowing forward references within `.env` | Recursive (no nested `${${VAR}}` support) |
| A pure function (no side effects on `os.environ`) | An environment mutator (that is `set_as_environment_variables()`) |

## Key Attributes

### The Two-Layer Resolution Model

The `override` flag controls dict merge order, which determines variable lookup precedence:

| `override` | `env` dict build order | Effect |
|------------|----------------------|--------|
| `True` | `os.environ` first, then `new_values` on top | `.env` values shadow OS env vars |
| `False` | `new_values` first, then `os.environ` on top | OS env vars shadow `.env` values |

### Atom Types (from `variables.py`)

| Type | Example Input | `resolve(env)` Behavior |
|------|--------------|------------------------|
| `Literal` | plain text between `${}` refs | Returns its string value unchanged |
| `Variable` | `${DB_HOST}` | Looks up `name` in `env`, falls back to `default` or `""` |

### The `_posix_variable` Regex

Pattern: `\$\{(?P<name>[^\}:]*)(?::-(?P<default>[^\}]*))?\}`

Matches:
- `${VAR}` -- name=`VAR`, default=`None`
- `${VAR:-fallback}` -- name=`VAR`, default=`fallback`

Does NOT match:
- `$VAR` (no braces)
- `${VAR:=assign}` (other POSIX operators)
- `${VAR:+alternate}` (other POSIX operators)

## Boundaries

**Input:** An `Iterable[Tuple[str, Optional[str]]]` of raw (key, value) pairs from the parser, plus an `override` boolean.

**Output:** A `Mapping[str, Optional[str]]` with all `${VAR}` references resolved.

**Processing per value:**
1. If value is `None` (key-only line), result is `None`
2. Tokenize value into `Atom` sequence via `parse_variables()`
3. Build `env` dict with appropriate merge order based on `override`
4. Resolve each atom against `env`, concatenate results

**Delegates to:**
- `variables.parse_variables()` for tokenizing value strings into `Atom` sequences
- `Atom.resolve(env)` for per-atom resolution

**Key constraint:** Variables are resolved sequentially, so earlier `.env` entries are available to later ones (via `new_values` accumulator).

## Evidence

- `resolve_variables()`: `src/dotenv/main.py:L289-L311`
- Override merge order logic: `src/dotenv/main.py:L301-L306`
- `parse_variables()`: `src/dotenv/variables.py:L70-L86`
- `_posix_variable` regex: `src/dotenv/variables.py:L5-L13`
- `Variable.resolve()`: `src/dotenv/variables.py:L63-L67`
- `Literal.resolve()`: `src/dotenv/variables.py:L44-L45`
- Called from `DotEnv.dict()`: `src/dotenv/main.py:L83-L84`
