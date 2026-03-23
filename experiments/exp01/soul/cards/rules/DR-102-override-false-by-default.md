---
card_type: decision_rule_card
card_id: DR-102
repo: python-dotenv
type: UNSAID_GOTCHA
title: "load_dotenv() does NOT override existing environment variables by default"
rule: |
  load_dotenv(override=False) is the default. If a variable already exists in
  os.environ (e.g., set by Docker, systemd, or the shell), the .env file value
  is silently ignored. This is the opposite of what many developers expect,
  especially those coming from Node.js dotenv which also defaults to not
  overriding but makes it more visible.
context: |
  This is the single most common source of confusion. Developers add a variable
  to .env, but it has no effect because the same variable was already set in
  the shell or by the deployment platform. The silent nature of this behavior
  makes it very hard to debug. Notably, the DotEnv class constructor defaults
  override=True, but load_dotenv() defaults override=False — an internal
  inconsistency that further confuses contributors reading the source.
do:
  - "Use override=True explicitly when you want .env values to take precedence"
  - "Check os.environ before calling load_dotenv() when debugging missing values"
  - "Document in your project README which override mode you use"
dont:
  - "Assume .env file values will always be applied"
  - "Debug .env loading without checking if the variable already exists in the environment"
  - "Confuse DotEnv(override=True) default with load_dotenv(override=False) default"
applies_to_versions: ">=0.6.0"
confidence: 0.95
evidence_level: E5
sources:
  - "https://github.com/theskumar/python-dotenv/issues/79"
  - "https://github.com/theskumar/python-dotenv/issues/5"
  - "Source code: load_dotenv(override=False) vs DotEnv(override=True)"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
