---
card_type: decision_rule_card
card_id: DR-109
repo: python-dotenv
type: UNSAID_COMPATIBILITY
title: "python-dotenv provides no type casting — all values are strings"
rule: |
  python-dotenv loads all values as strings into os.environ. It provides no
  built-in type casting, validation, or default value mechanisms. Boolean
  values like "True"/"False", integers, and lists all remain strings.
  Applications must handle conversion themselves.
context: |
  This is a fundamental design limitation that drives many users to alternatives
  like python-decouple (which has config('DEBUG', cast=bool)) or Pydantic
  Settings (which provides full type validation). Common bugs include treating
  os.environ.get('DEBUG') == 'False' as falsy (it is truthy because it is a
  non-empty string) or expecting os.environ.get('PORT') to return an integer.
do:
  - "Explicitly cast environment variables after loading (int(), bool checks, etc.)"
  - "Consider python-decouple or Pydantic Settings if you need type casting"
  - "Write a thin config layer that validates and casts env vars at startup"
  - "Treat 'False', '0', '' consistently — define your own truthiness rules"
dont:
  - "Use if os.getenv('DEBUG') to check boolean flags (non-empty strings are truthy)"
  - "Assume os.getenv('PORT') returns an integer"
  - "Compare os.getenv('FLAG') == True (it will always be False since value is a string)"
applies_to_versions: ">=0.1.0"
confidence: 0.90
evidence_level: E3
sources:
  - "https://dev.to/proteusiq/trending-anti-pattern-loading-environments-j55"
  - "https://pypy-django.github.io/blog/2024/07/06/comparing-django-environ-python-decouple-and-python-dotenv/"
  - "https://fastenv.bws.bio/comparisons"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
