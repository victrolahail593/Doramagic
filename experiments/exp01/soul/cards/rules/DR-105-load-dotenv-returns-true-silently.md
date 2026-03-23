---
card_type: decision_rule_card
card_id: DR-105
repo: python-dotenv
type: UNSAID_GOTCHA
title: "load_dotenv() silently succeeds even when .env file is missing (older versions)"
rule: |
  In older versions, load_dotenv() returned True even when no .env file was
  found, making it impossible to detect missing configuration files. Since
  PR #388, it returns False when no variables are loaded. However, even in
  current versions, load_dotenv() does not raise an exception for missing
  files — it simply yields an empty StringIO and returns False. The verbose=True
  flag must be set to get a log warning.
context: |
  This silent behavior means your application can start without any configuration
  and fail later with cryptic KeyError or None-related errors. Many developers
  expect load_dotenv() to fail loudly when the file is missing. The find_dotenv()
  function returns an empty string when no file is found, which load_dotenv()
  treats as "no file" rather than an error.
do:
  - "Check the return value of load_dotenv() and handle False appropriately"
  - "Use verbose=True to get log warnings about missing .env files"
  - "Validate critical environment variables immediately after loading"
  - "Use find_dotenv(raise_error_if_not_found=True) if a missing file should be fatal"
dont:
  - "Assume load_dotenv() will raise an exception if the .env file is missing"
  - "Ignore the return value of load_dotenv()"
  - "Deploy without validating that required environment variables are actually set"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E5
sources:
  - "https://github.com/theskumar/python-dotenv/issues/321"
  - "Source code: main.py _get_stream() yields StringIO('') when file not found"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
