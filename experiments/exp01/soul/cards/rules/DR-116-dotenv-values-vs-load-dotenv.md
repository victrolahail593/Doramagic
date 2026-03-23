---
card_type: decision_rule_card
card_id: DR-116
repo: python-dotenv
type: UNSAID_GOTCHA
title: "dotenv_values() and load_dotenv() handle undefined variables differently"
rule: |
  dotenv_values() returns a dict where undefined/empty variables map to None,
  while load_dotenv() skips variables with None values (does not set them in
  os.environ). This means os.environ.get('KEY') returns None for a missing key
  in both cases, but the semantics differ: dotenv_values explicitly represents
  "defined but empty" as None, while load_dotenv simply does not touch os.environ
  for such keys.
context: |
  This matters when a variable is declared in .env without a value (e.g., just
  KEY on a line with no = sign). dotenv_values() will include it with None,
  while load_dotenv() will not set it in the environment. Code that checks
  'KEY' in os.environ vs os.environ.get('KEY') will behave differently depending
  on which function was used.
do:
  - "Use dotenv_values() when you need to distinguish between 'not set' and 'set to empty'"
  - "Use load_dotenv() for the common case of populating os.environ"
  - "Always assign values in .env files (KEY=value, not just KEY)"
dont:
  - "Assume dotenv_values() and load_dotenv() produce equivalent results"
  - "Declare keys without values in .env expecting load_dotenv() to set them"
applies_to_versions: ">=0.1.0"
confidence: 0.85
evidence_level: E5
sources:
  - "Source code: main.py set_as_environment_variables() skips None values"
  - "https://pypi.org/project/python-dotenv/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
