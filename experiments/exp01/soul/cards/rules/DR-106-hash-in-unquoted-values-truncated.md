---
card_type: decision_rule_card
card_id: DR-106
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Hash (#) in unquoted values is treated as inline comment, silently truncating the value"
rule: |
  If a value contains a # character and is not quoted, python-dotenv interprets
  everything after the # (preceded by whitespace) as a comment. The value is
  silently truncated. This commonly affects URLs with fragments, color codes,
  and passwords containing #.
context: |
  The parser regex (_comment pattern) matches optional whitespace followed by #
  as a comment. This follows Bash semantics but surprises users who paste URLs
  or generated passwords. The truncation is silent — no warning is logged. The
  fix is simple: wrap the value in double quotes.
do:
  - "Always quote values that may contain # characters"
  - "Use double quotes for URLs, color codes, and generated passwords"
  - "Review .env files for unquoted values containing # after copy-pasting"
dont:
  - "Paste URLs with fragments (e.g., https://example.com/page#section) without quoting"
  - "Use unquoted hex color codes (e.g., COLOR=#FF0000) — quote them"
  - "Assume all characters are safe in unquoted values"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E5
sources:
  - "Source code: parser.py _comment regex matches [^\\S\\r\\n]*#[^\\r\\n]*"
  - "https://saurabh-kumar.com/python-dotenv/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
