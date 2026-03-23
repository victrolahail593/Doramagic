---
card_type: decision_rule_card
card_id: DR-108
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Variable interpolation requires ${VAR} syntax — bare $VAR is not expanded"
rule: |
  python-dotenv only expands variables using the ${VARIABLE} syntax with curly
  braces. The bare $VARIABLE syntax (without braces) is NOT expanded and is
  kept as a literal string. This differs from Bash where both forms work.
context: |
  Developers familiar with Bash or docker-compose variable expansion expect
  $VARIABLE to work. When it does not expand, the literal string "$VARIABLE"
  ends up in the environment, causing hard-to-debug configuration errors.
  The interpolation can be disabled entirely with interpolate=False.
do:
  - "Always use ${VAR} syntax (with braces) for variable references in .env files"
  - "Disable interpolation with interpolate=False if values contain literal $ characters"
  - "Test variable expansion in your .env files during development"
dont:
  - "Use bare $VAR syntax expecting it to expand like Bash"
  - "Store values with literal ${...} patterns without disabling interpolation"
  - "Assume python-dotenv's interpolation is identical to Bash variable expansion"
applies_to_versions: ">=0.9.0"
confidence: 0.85
evidence_level: E4
sources:
  - "https://pypi.org/project/python-dotenv/"
  - "https://github.com/theskumar/python-dotenv/issues/326"
  - "https://saurabh-kumar.com/python-dotenv/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
