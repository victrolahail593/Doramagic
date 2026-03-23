---
card_type: decision_rule_card
card_id: DR-115
repo: python-dotenv
type: UNSAID_PERFORMANCE
title: "load_dotenv() has no caching — each call re-reads and re-parses the file"
rule: |
  load_dotenv() creates a new DotEnv instance each time it is called. There is
  no built-in caching, deduplication, or guard against multiple loads. Each call
  opens the file, parses all lines, resolves variable interpolation, and writes
  to os.environ. While the performance impact is negligible for small .env files,
  it can add up in hot paths or large files.
context: |
  This is relevant in applications where multiple modules independently call
  load_dotenv() (e.g., a Flask app, a Celery worker, and a management command
  all calling it at import time). The DotEnv class has internal caching
  (self._dict), but load_dotenv() creates a fresh instance each time. With
  override=False (default), redundant loads are mostly harmless but wasteful.
do:
  - "Call load_dotenv() once in your application entry point, not in every module"
  - "Use a singleton pattern or initialization guard if multiple entry points exist"
  - "For performance-sensitive apps, call load_dotenv() only during startup"
dont:
  - "Call load_dotenv() in frequently-imported utility modules"
  - "Call load_dotenv() inside request handlers or hot loops"
  - "Assume python-dotenv caches results between calls"
applies_to_versions: ">=0.1.0"
confidence: 0.80
evidence_level: E5
sources:
  - "Source code: load_dotenv() creates new DotEnv() each call"
  - "https://github.com/theskumar/python-dotenv/issues/504"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
