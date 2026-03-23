---
card_type: decision_rule_card
card_id: DR-107
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Single quotes preserve literal content; double quotes interpret escape sequences"
rule: |
  In python-dotenv, single-quoted values are treated literally (no escape
  processing), while double-quoted values interpret escape sequences like \n,
  \t, \\, etc. This follows Bash semantics but is not obvious from the
  documentation. Choosing the wrong quote type can cause subtle bugs with
  file paths (Windows backslashes), regex patterns, or JSON strings.
context: |
  Users frequently store Windows file paths (C:\Users\name) or regex patterns
  in .env files. With double quotes, backslashes are interpreted as escape
  characters, potentially corrupting the value. With single quotes, the
  backslashes are preserved literally. This distinction is critical but
  rarely documented clearly.
do:
  - "Use single quotes for values containing backslashes (Windows paths, regex)"
  - "Use double quotes when you intentionally need escape sequences (\\n for newline)"
  - "Document your quoting convention in the project's .env.example file"
dont:
  - "Use double quotes for Windows file paths (C:\\Users becomes C:Users with tab)"
  - "Assume single and double quotes behave identically"
  - "Mix quoting styles without understanding the escape behavior difference"
applies_to_versions: ">=0.9.0"
confidence: 0.90
evidence_level: E5
sources:
  - "Source code: parser.py handles single and double quotes with different regex"
  - "https://github.com/theskumar/python-dotenv/issues/35"
  - "https://saurabh-kumar.com/python-dotenv/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
