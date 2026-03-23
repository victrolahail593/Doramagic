---
card_type: decision_rule_card
card_id: DR-104
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Older versions used system locale encoding, causing UnicodeDecodeError on Windows"
rule: |
  Before the default encoding was changed to UTF-8, python-dotenv used the
  system's locale encoding (e.g., GBK on Chinese Windows, CP1252 on Western
  Windows). This caused UnicodeDecodeError when .env files contained non-ASCII
  characters like Chinese comments or accented characters. Modern versions
  (>=0.20.0) default to UTF-8, but passing encoding=None reverts to the old
  locale-dependent behavior.
context: |
  This was a critical cross-platform issue (GitHub #300, #207, #147, #121).
  Teams working across macOS (UTF-8 by default) and Windows would encounter
  crashes only on Windows. The fix (PR #306) set encoding="utf-8" as the
  default parameter. However, if you explicitly pass encoding=None to
  load_dotenv(), you get the old behavior, which can be a trap.
do:
  - "Ensure .env files are saved as UTF-8 (especially on Windows)"
  - "Use the default encoding parameter (utf-8) unless you have a specific reason not to"
  - "Pin python-dotenv >=0.20.0 if your .env files contain non-ASCII characters"
dont:
  - "Pass encoding=None to load_dotenv() unless you understand the locale implications"
  - "Assume .env files created on Windows are UTF-8 by default (editors may use ANSI)"
  - "Use non-ASCII characters in .env values without testing on all target platforms"
applies_to_versions: "all (fixed in >=0.20.0)"
confidence: 0.95
evidence_level: E5
sources:
  - "https://github.com/theskumar/python-dotenv/issues/300"
  - "https://github.com/theskumar/python-dotenv/pull/306"
  - "https://github.com/theskumar/python-dotenv/issues/207"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
