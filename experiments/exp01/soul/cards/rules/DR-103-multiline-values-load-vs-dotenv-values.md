---
card_type: decision_rule_card
card_id: DR-103
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Multiline values may be truncated by load_dotenv() but work with dotenv_values()"
rule: |
  When using multiline values (e.g., SSH keys, certificates, JSON) in double
  quotes, load_dotenv() may only load the first line into os.environ, while
  dotenv_values() correctly returns the full multiline content. This
  inconsistency has been reported across multiple versions and platforms.
context: |
  This is a long-standing issue (GitHub #26, #82, #89, #548, #555). The root
  cause involves differences in how the parsed values are written to os.environ
  versus returned as a dict. When dotenv_path is explicitly specified, the
  behavior may differ from when the file is auto-discovered. A PR (#570) was
  opened to fix unquoted multiline, but the issue persists in certain edge cases.
  Workarounds include using \n escape sequences in double-quoted values or
  base64-encoding the content.
do:
  - "Use \\n escape sequences in double-quoted values for multiline content"
  - "Test multiline values explicitly with both load_dotenv() and os.environ.get()"
  - "Consider base64-encoding complex multiline values like certificates or keys"
  - "Verify behavior when upgrading python-dotenv versions"
dont:
  - "Assume raw multiline content in .env files will round-trip through os.environ"
  - "Use dotenv_values() results as a proxy for what load_dotenv() actually sets"
  - "Store large multiline content (like PEM keys) directly in .env without encoding"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E3
sources:
  - "https://github.com/theskumar/python-dotenv/issues/555"
  - "https://github.com/theskumar/python-dotenv/issues/548"
  - "https://github.com/theskumar/python-dotenv/issues/89"
  - "https://github.com/theskumar/python-dotenv/issues/26"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
