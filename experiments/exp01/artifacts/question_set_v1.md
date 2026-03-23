# Question Set v1 — python-dotenv A/B/C Validation

**Created:** 2026-03-09
**Total questions:** 12
**Categories:** 5

---

## Category 1: Domain Concepts (3 questions)

### Q1. What is the architecture of python-dotenv's parsing pipeline? Describe the key components and how they connect.
**Type:** Structural understanding
**Target knowledge:** CC-001, CC-002, CC-003, WF-001

### Q2. How does python-dotenv handle variable interpolation? What syntax is supported and what is NOT supported?
**Type:** Factual + edge-case
**Target knowledge:** CC-003, DR-003, DR-108

### Q3. What quoting modes does python-dotenv support, and how do they differ in escape sequence handling?
**Type:** Factual recall + structural
**Target knowledge:** DR-002, DR-107

---

## Category 2: Workflows (2 questions)

### Q4. Walk through what happens when `load_dotenv()` is called with no arguments. What is the complete flow from invocation to environment variables being set?
**Type:** Structural understanding
**Target knowledge:** WF-001, CC-001, DR-004

### Q5. How does python-dotenv's parser recover from malformed lines in a .env file? Does it stop processing or continue?
**Type:** Structural understanding
**Target knowledge:** WF-002, DR-005

---

## Category 3: Rules/Conditions (3 questions)

### Q6. [HALLUCINATION TRAP] If I have `DB_URL=postgres://host:5432/db#pool=5` in my .env file (unquoted), what value will `os.environ['DB_URL']` contain after `load_dotenv()`?
**Type:** Edge case / gotcha
**Target knowledge:** DR-106, DR-002
**Why it's a trap:** An uninformed model may say the full URL is preserved. In reality, `#pool=5` is stripped as a comment (because whitespace before # is not required by the actual regex — the pattern is `\s+#.*` which requires whitespace, but the unquoted value regex itself may interact differently).

### Q7. [HALLUCINATION TRAP] I have this .env file:
```
BASE_URL=https://api.example.com
API_ENDPOINT=$BASE_URL/v2/users
```
What will `API_ENDPOINT` resolve to?
**Type:** Edge case / gotcha
**Target knowledge:** DR-003, DR-108
**Why it's a trap:** An uninformed model will likely say it resolves to `https://api.example.com/v2/users`. In reality, `$BASE_URL` (without braces) is treated as literal text. Only `${BASE_URL}` triggers expansion.

### Q8. What does the `override` parameter actually control in python-dotenv? Does it affect only environment variable setting, or does it have other effects?
**Type:** Rules / conditional behavior
**Target knowledge:** DR-001, DR-118

---

## Category 4: Risk/Gotchas (2 questions)

### Q9. I'm using the same .env file for both my Python application (via python-dotenv) and Docker Compose. Should I expect them to parse it identically? What could go wrong?
**Type:** UNSAID knowledge / risk
**Target knowledge:** DR-100, DR-107

### Q10. My `load_dotenv()` call seems to have no effect — my .env file values aren't showing up in `os.environ`. What are the most likely causes?
**Type:** UNSAID knowledge / debugging
**Target knowledge:** DR-102, DR-101, DR-105, DR-119

---

## Category 5: Solution Recommendations (2 questions)

### Q11. I'm building a Flask app that will be deployed in Docker. How should I structure my .env configuration to work correctly in both local development and production?
**Type:** Actionable advice
**Target knowledge:** DR-111, DR-113, DR-119, DR-117, DR-120

### Q12. I need to store an RSA private key (multiline PEM format) and a Windows file path (`C:\Users\deploy\config`) in my .env file. How should I format these values?
**Type:** Actionable advice
**Target knowledge:** DR-103, DR-107, DR-002, DR-114

---

## Question Design Notes

| Property | Count |
|----------|-------|
| Hallucination traps | 2 (Q6, Q7) |
| Structural understanding | 3 (Q1, Q4, Q5) |
| Community/UNSAID knowledge | 4 (Q9, Q10, Q11, Q12) |
| Code-level knowledge | 4 (Q2, Q3, Q6, Q8) |
| Practical developer questions | 12/12 |
