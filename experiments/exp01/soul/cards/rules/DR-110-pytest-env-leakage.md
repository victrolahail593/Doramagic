---
card_type: decision_rule_card
card_id: DR-110
repo: python-dotenv
type: UNSAID_GOTCHA
title: "load_dotenv() in application code pollutes test environments with dev settings"
rule: |
  When application code calls load_dotenv() at import time or module level,
  those .env values leak into the test environment. Since load_dotenv() mutates
  the global os.environ, test isolation is broken. Dev-only values (API keys,
  database URLs) may cause tests to hit real services or produce inconsistent
  results across machines.
context: |
  This is a well-known issue (GitHub #253). The pytest-dotenv plugin exists to
  provide controlled .env loading for tests, but it conflicts with application-
  level load_dotenv() calls. The core problem is that os.environ is global and
  mutable, and load_dotenv() provides no cleanup mechanism.
do:
  - "Use monkeypatch.setenv() or unittest.mock.patch.dict(os.environ) in tests"
  - "Load .env conditionally (e.g., only when not in test mode)"
  - "Use pytest-dotenv to load a test-specific .env.test file"
  - "Call load_dotenv() in your entry point (main.py, wsgi.py), not at module level"
dont:
  - "Call load_dotenv() at module-level in library code that tests will import"
  - "Assume test environments are clean — previous test runs may have polluted os.environ"
  - "Mix real API credentials in .env with test fixtures"
applies_to_versions: ">=0.1.0"
confidence: 0.85
evidence_level: E3
sources:
  - "https://github.com/theskumar/python-dotenv/issues/253"
  - "https://pypi.org/project/pytest-dotenv/"
  - "https://pytest-with-eric.com/pytest-best-practices/pytest-environment-variables/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
