---
card_type: decision_rule_card
card_id: DR-113
repo: python-dotenv
type: UNSAID_COMPATIBILITY
title: "Flask automatically loads .env and .flaskenv if python-dotenv is installed"
rule: |
  When python-dotenv is installed, Flask's CLI (flask run) automatically loads
  .flaskenv (for CLI config like FLASK_APP, FLASK_ENV) and .env (for app config).
  This happens before your application code runs. If you also call load_dotenv()
  in your app, variables are loaded twice, and the interaction between Flask's
  auto-load and your explicit load depends on override settings.
context: |
  Flask's auto-loading is triggered by the mere presence of python-dotenv in
  the environment. In Docker containers where env vars are injected directly,
  Flask still prints "python-dotenv is not installed" warnings if the package
  is absent (GitHub pallets/flask#3872). The two-file convention (.flaskenv for
  public CLI config, .env for private app config) is Flask-specific and not
  a python-dotenv feature.
do:
  - "Understand that Flask loads .env automatically — you may not need explicit load_dotenv()"
  - "Use .flaskenv for FLASK_APP/FLASK_DEBUG and .env for secrets"
  - "Set PYTHON_DOTENV_DISABLED=1 in production Docker containers using Flask"
dont:
  - "Call load_dotenv() redundantly in Flask apps without understanding Flask's auto-loading"
  - "Put secrets in .flaskenv (it is meant to be committed to version control)"
  - "Uninstall python-dotenv in Docker just to silence Flask's warning"
applies_to_versions: ">=0.9.0"
confidence: 0.85
evidence_level: E3
sources:
  - "https://github.com/pallets/flask/issues/2722"
  - "https://github.com/pallets/flask/issues/3872"
  - "https://prettyprinted.com/tutorials/automatically_load_environment_variables_in_flask/"
extracted_at: "2026-03-09"
last_verified: "2026-03-09"
status: draft
---
