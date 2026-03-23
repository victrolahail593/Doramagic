---
card_type: concept_card
card_id: CC-002
repo: python-dotenv
title: "Parser -- Hand-Written Recursive Descent .env Lexer"
---

## Identity

The parser (`parser.py`) is a hand-written recursive-descent parser that transforms a text stream of `.env` content into a sequence of `Binding` tuples. It handles the full grammar of dotenv files: unquoted, single-quoted, and double-quoted values, escape sequences, comments, `export` prefixes, and multiline whitespace.

## Is / Is Not

| IS | IS NOT |
|----|--------|
| A complete lexer+parser in one pass | A tokenizer that produces an AST |
| A position-tracked string scanner (`Reader`) | A line-by-line reader (reads entire stream into memory) |
| Error-tolerant (returns `error=True` bindings instead of raising) | Strict (never aborts on malformed input) |
| Stateless across calls (no global state) | Stateful between bindings (each `parse_binding` is independent) |
| Responsible for escape decoding (`decode_escapes`) | Responsible for variable interpolation (that is `variables.py`) |

## Key Attributes

### Data Structures

| Type | Fields | Purpose |
|------|--------|---------|
| `Binding` (NamedTuple) | `key`, `value`, `original`, `error` | Output unit -- one parsed key-value pair |
| `Original` (NamedTuple) | `string`, `line` | Raw source text and line number for round-tripping |
| `Position` | `chars`, `line` | Tracks character offset and line number |
| `Reader` | `string`, `position`, `mark` | Wraps stream into a scannable string with mark/recall |

### Regex Arsenal (13 pre-compiled patterns)

| Pattern | Purpose |
|---------|---------|
| `_newline` | `\r\n`, `\n`, `\r` |
| `_multiline_whitespace` | Any whitespace including newlines |
| `_whitespace` | Horizontal whitespace only (not newlines) |
| `_export` | Optional `export` keyword prefix |
| `_single_quoted_key` | Key wrapped in single quotes |
| `_unquoted_key` | Key without quotes (stops at `=`, `#`, whitespace) |
| `_equal_sign` | `=` followed by optional horizontal whitespace |
| `_single_quoted_value` | Value in `'...'` (supports `\'` escape) |
| `_double_quoted_value` | Value in `"..."` (supports `\"` escape) |
| `_unquoted_value` | Unquoted value (rest of line) |
| `_comment` | Optional `# comment` at end of line |
| `_end_of_line` | Line terminator |
| `_rest_of_line` | Catch-all for error recovery |

## Boundaries

**Input:** An `IO[str]` text stream (file or StringIO).

**Output:** An `Iterator[Binding]` -- each binding represents one logical line from the `.env` file.

**Scope of a single `parse_binding()` call:**
1. Skip multiline whitespace
2. Consume optional `export` prefix
3. Parse key (single-quoted or unquoted; `#` means comment-only line)
4. If `=` present, parse value (single-quoted, double-quoted, or unquoted)
5. Consume trailing comment and end-of-line
6. On any `Error`, consume rest-of-line and return `error=True` binding

**Does NOT do:**
- Variable interpolation (`${VAR}` is left as literal text)
- Environment mutation
- File I/O (receives an already-opened stream)

## Evidence

- `Reader` class: `src/dotenv/parser.py:L69-L104`
- `Binding` NamedTuple: `src/dotenv/parser.py:L40-L44`
- `parse_binding()`: `src/dotenv/parser.py:L142-L175`
- `parse_value()` with quoting dispatch: `src/dotenv/parser.py:L128-L139`
- `parse_key()` with comment detection: `src/dotenv/parser.py:L112-L120`
- `decode_escapes()`: `src/dotenv/parser.py:L107-L110`
- `parse_stream()` top-level iterator: `src/dotenv/parser.py:L179-L182`
- 13 regex definitions: `src/dotenv/parser.py:L18-L32`
