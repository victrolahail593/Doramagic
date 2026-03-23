---
card_type: decision_rule_card
card_id: DR-114
repo: python-dotenv
type: UNSAID_GOTCHA
title: "set_key() writes values with single quotes by default, disabling escape sequence processing"
rule: |
  The set_key() function wraps values in single quotes by default (quote_mode=
  "always"). This means values written by set_key() will NOT have escape
  sequences processed when read back — because single-quoted values are treated
  literally. If you write a value with \\n intending a newline, you get the
  literal characters \\n instead.
context: |
  This is a subtle asymmetry: if you manually write KEY="value\\nwith\\nnewlines"
  (double quotes) in .env, escape sequences work. But if you use set_key() or
  the dotenv CLI to set the same value, it gets wrapped in single quotes and
  the escapes are preserved literally. This can cause round-trip inconsistencies.
do:
  - "Be aware that set_key() uses single quotes — escape sequences won't be interpreted on read"
  - "Use quote_mode='never' if you need to preserve exact formatting"
  - "Manually edit .env files for values that need escape sequence processing"
dont:
  - "Expect set_key() and manual editing to produce identical behavior for escaped values"
  - "Use set_key() for values containing intentional escape sequences like \\n"
applies_to_versions: ">=0.18.0"
confidence: 0.85
evidence_level: E5
sources:
  - "Source code: main.py set_key() uses single quotes with quote_mode='always'"
  - "https://github.com/theskumar/python-dotenv/pull/330"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
