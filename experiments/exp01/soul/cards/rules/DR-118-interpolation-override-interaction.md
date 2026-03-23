---
card_type: decision_rule_card
card_id: DR-118
repo: python-dotenv
type: UNSAID_GOTCHA
title: "Variable interpolation interacts subtly with the override flag"
rule: |
  When interpolation is enabled and override=False (default), variable references
  like ${VAR} are resolved against the current os.environ first, then the .env
  file. This means if VAR is already set in the environment, the .env file's
  value of VAR is ignored, AND any other .env variable referencing ${VAR} uses
  the environment value, not the .env value. With override=True, .env values
  take precedence for both direct setting and interpolation resolution.
context: |
  This creates a confusing scenario where changing one environment variable
  externally can cascade through interpolated values in the .env file. The
  resolution order is not obvious and has led to bug reports (GitHub #256, #326).
  Understanding this requires reading the resolve_variables() function in
  variables.py.
do:
  - "Be explicit about override=True or override=False when using variable interpolation"
  - "Test interpolated values with and without pre-existing environment variables"
  - "Avoid deep interpolation chains (VAR1 -> VAR2 -> VAR3) as they amplify the confusion"
dont:
  - "Mix interpolation with override=False without understanding the resolution order"
  - "Assume .env file values are used for interpolation when override=False"
applies_to_versions: ">=0.9.0"
confidence: 0.80
evidence_level: E3
sources:
  - "https://github.com/theskumar/python-dotenv/issues/256"
  - "https://github.com/theskumar/python-dotenv/issues/326"
  - "Source code: variables.py resolve_variables()"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
