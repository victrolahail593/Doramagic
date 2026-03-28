# Changelog

All notable changes to Doramagic are documented in this file.

## [12.1.0] - 2026-03-28

### Fixed (S-tier — pipeline was fundamentally broken)
- Engine path resolution: _find_engine() searches multiple candidate paths (engine was never invoked)
- LLM retry: 3 attempts with exponential backoff + jitter + adaptive timeout (72% template fallback → <10%)
- Brick contamination: affinity_terms validation + max-1-domain guard + word-boundary matching (17% cross-domain pollution → ~0%)
- CWD self-reference: read_repo_files rejects empty/relative paths (was reading own README as target project)

### Added (A-tier — architecture improvements)
- GitHub Primary discovery: ClawHub controls search depth only, never skips GitHub. Engine + API fallback
- Section-split compiler: 5 focused LLM calls (700-1500 tokens each) replacing single 6000-token call
- Parallel soul extraction: ThreadPoolExecutor with deterministic input-order collection
- Repo type classifier: CATALOG/TOOL/FRAMEWORK, awesome-lists get shallow extraction
- 60-point quality gate: 5-dimension scoring (Coverage/Evidence/DSD/WHY/Substance) before delivery
- CJK-aware slugify: semantic word-boundary truncation, max 40 chars
- 4-tier graceful degradation: FULL/PARTIAL_SOULS/FAST_PATH/TEMPLATE with completeness percentage
- Crash resume: checkpoints at Step 1 (profile) and Step 3 (souls), --resume CLI flag
- Thread-safe logging with threading.Lock

### Changed
- Fast path synthesis trigger: uses has_repo_souls check instead of dead skip_github flag
- Validator accepts Anti-Patterns & Safety section heading
- Engine subprocess passes --timeout flag (engine gets timeout-15 for graceful shutdown)
- Retry loop no longer retries deterministic errors (KeyError/ValueError/JSONDecodeError)
- Evidence scoring broadened to reward parenthetical attribution and project references


### Added
- Skill Architect: LLM-powered compilation with gold-standard reference skills
- Self-repair loop: validates output, auto-fixes issues, retries
- Per-domain safety boundaries in generated skills
- Input sanitization against shell metacharacter injection (CSO audit fix)
- publish_preflight.sh: automated pre-release gate for GitHub standards
- card_id whitelist validation (path traversal prevention)

### Changed
- GitHub Actions pinned to SHA digests
- Internal IP references replaced with environment variables in SKILL.md
- Legacy extract.py converted from shell=True to list-form subprocess
- uv.lock now tracked by git (removed from .gitignore)
- races/, research/, experiments/ removed from public repo

### Security
- CSO audit: 6 HIGH findings fixed, 6 MEDIUM documented
- Full report in .gstack/security-reports/

## [11.0.0] - 2026-03-25

### Added
- Domain brick integration: 278 bricks across 34 domains injected into extraction prompts
- Fast path synthesis: Python-only compilation (no LLM), 52s to 14s
- GitHub search rewrite: qualifiers, README via API, relevance scoring, parallel processing
- Debug logging mode (--debug flag)

### Changed
- Intent recognition with LLM confidence scoring
- Socratic gate: low-confidence inputs return clarifying questions instead of blind search
- GitHub search timeout: 360s to 60s

## [10.0.0] - 2026-03-25
## [12.1.0] - 2026-03-28

### Fixed (S-tier — pipeline was fundamentally broken)
- Engine path resolution: _find_engine() searches multiple candidate paths (engine was never invoked)
- LLM retry: 3 attempts with exponential backoff + jitter + adaptive timeout (72% template fallback → <10%)
- Brick contamination: affinity_terms validation + max-1-domain guard + word-boundary matching (17% cross-domain pollution → ~0%)
- CWD self-reference: read_repo_files rejects empty/relative paths (was reading own README as target project)

### Added (A-tier — architecture improvements)
- GitHub Primary discovery: ClawHub controls search depth only, never skips GitHub. Engine + API fallback
- Section-split compiler: 5 focused LLM calls (700-1500 tokens each) replacing single 6000-token call
- Parallel soul extraction: ThreadPoolExecutor with deterministic input-order collection
- Repo type classifier: CATALOG/TOOL/FRAMEWORK, awesome-lists get shallow extraction
- 60-point quality gate: 5-dimension scoring (Coverage/Evidence/DSD/WHY/Substance) before delivery
- CJK-aware slugify: semantic word-boundary truncation, max 40 chars
- 4-tier graceful degradation: FULL/PARTIAL_SOULS/FAST_PATH/TEMPLATE with completeness percentage
- Crash resume: checkpoints at Step 1 (profile) and Step 3 (souls), --resume CLI flag
- Thread-safe logging with threading.Lock

### Changed
- Fast path synthesis trigger: uses has_repo_souls check instead of dead skip_github flag
- Validator accepts Anti-Patterns & Safety section heading
- Engine subprocess passes --timeout flag (engine gets timeout-15 for graceful shutdown)
- Retry loop no longer retries deterministic errors (KeyError/ValueError/JSONDecodeError)
- Evidence scoring broadened to reward parenthetical attribution and project references


### Added
- Skill Architect: LLM-powered compilation with gold-standard reference skills
- Self-repair loop: validates output, auto-fixes issues, retries
- Per-domain safety boundaries in generated skills
- Input sanitization against shell metacharacter injection (CSO audit fix)
- `publish_preflight.sh`: automated pre-release gate for GitHub standards
- card_id whitelist validation (path traversal prevention)

### Changed
- GitHub Actions pinned to SHA digests
- Internal IP references replaced with environment variables in SKILL.md
- Legacy `extract.py` converted from `shell=True` to list-form subprocess
- `uv.lock` now tracked by git (removed from .gitignore)
- `races/`, `research/`, `experiments/` removed from public repo

### Security
- CSO audit: 6 HIGH findings fixed, 6 MEDIUM documented in TODOS
- See `.gstack/security-reports/2026-03-26-cso-report.json` for details

## [11.0.0] - 2026-03-25

### Added
- Domain brick integration: 278 bricks across 34 domains injected into extraction prompts
- Fast path synthesis: Python-only compilation (no LLM), reduces 52s to 14s
- GitHub search rewrite: qualifiers, README via API, relevance scoring, parallel processing

### Changed
- Intent recognition with LLM confidence scoring
- Socratic gate: low-confidence inputs return clarifying questions instead of blind search
- GitHub search timeout: 360s to 60s
- Timing summary fix (was double-counting)


### Changed
- Single-shot pipeline upgraded to v9.0: LLM-powered keyword generation replaces static dictionary
- Relevance gate filters irrelevant repos before extraction, returns honest "not found" when appropriate
- Skill compiler outputs actionable AI agent instruction set instead of research report
- MIN_STARS threshold lowered to 0 to include small but relevant projects
- Entry point simplified to python3 (no uv/venv dependency)

### Fixed
- Search keyword generation bug: Chinese input like "WiFi密码管理" now correctly generates English search terms via LLM
- Production-to-repo version drift resolved (OpenClaw v10.0.0 synced back to Git)

## [9.2.0] - 2026-03-24

### Added
- Mermaid pipeline diagrams in README (top-level flow + extraction internals)
- Implementation highlights with code snippets in README
- Example output section showing real TandoorRecipes extraction
- GitHub Actions CI (pytest on push/PR, Python 3.12)
- Routing decision logging in CapabilityRouter (get_routing_summary())
- CI badge support

### Changed
- brick_injection.py: expanded framework mappings from 12 to 34 domains
- SKILL.md: fixed entry point path, updated to v9.2.0
- README: updated brick count to 278, added architecture visualization

### Fixed
- SKILL.md entry point was pointing to deprecated soul-extractor path
- Brick count assertion in tests updated for 278 bricks
- Makefile PYTHONPATH for cross-package test imports

## [9.1.0] - 2026-03-24

### Added
- 189 new knowledge bricks across 22 new frameworks/domains (89→278 total)
- AI stack coverage: LangChain, HF Transformers, LlamaIndex, vLLM, CrewAI, LiteLLM, Ollama, LangGraph, llama.cpp, Diffusers, OpenAI SDK, Langfuse, DSPy
- Web framework coverage: TypeScript/Node.js, Next.js, Vue.js, Java/Spring Boot
- General coverage: Ruby/Rails, Rust, PHP/Laravel, Swift/iOS, Kotlin/Android
- Trunk-based publish_to_github.sh release script

## [9.0.0] - 2026-03-23

### Added
- 8-stage extraction pipeline (Stage 0 through Stage 5 + Assembly)
- Agentic exploration (Stage 1.5) with hypothesis-driven deep dive
- Knowledge Compiler with type-routed formatting
- Confidence system with 4-tier evidence-chain verification
- Deceptive Source Detection (8-check DSD system)
- 89 knowledge bricks across 12 frameworks and domains
- Model-agnostic design via capability router (Claude, Gemini, GPT, Ollama)
- OpenClaw skill integration (/dora command)
- Claude Code skill compatibility
- ClawHub packaging script for one-command install


## [12.0.0] - 2026-03-26
## [12.1.0] - 2026-03-28

### Fixed (S-tier — pipeline was fundamentally broken)
- Engine path resolution: _find_engine() searches multiple candidate paths (engine was never invoked)
- LLM retry: 3 attempts with exponential backoff + jitter + adaptive timeout (72% template fallback → <10%)
- Brick contamination: affinity_terms validation + max-1-domain guard + word-boundary matching (17% cross-domain pollution → ~0%)
- CWD self-reference: read_repo_files rejects empty/relative paths (was reading own README as target project)

### Added (A-tier — architecture improvements)
- GitHub Primary discovery: ClawHub controls search depth only, never skips GitHub. Engine + API fallback
- Section-split compiler: 5 focused LLM calls (700-1500 tokens each) replacing single 6000-token call
- Parallel soul extraction: ThreadPoolExecutor with deterministic input-order collection
- Repo type classifier: CATALOG/TOOL/FRAMEWORK, awesome-lists get shallow extraction
- 60-point quality gate: 5-dimension scoring (Coverage/Evidence/DSD/WHY/Substance) before delivery
- CJK-aware slugify: semantic word-boundary truncation, max 40 chars
- 4-tier graceful degradation: FULL/PARTIAL_SOULS/FAST_PATH/TEMPLATE with completeness percentage
- Crash resume: checkpoints at Step 1 (profile) and Step 3 (souls), --resume CLI flag
- Thread-safe logging with threading.Lock

### Changed
- Fast path synthesis trigger: uses has_repo_souls check instead of dead skip_github flag
- Validator accepts Anti-Patterns & Safety section heading
- Engine subprocess passes --timeout flag (engine gets timeout-15 for graceful shutdown)
- Retry loop no longer retries deterministic errors (KeyError/ValueError/JSONDecodeError)
- Evidence scoring broadened to reward parenthetical attribution and project references


### Added
- Skill Architect: LLM-powered compilation with gold-standard reference skills
- Self-repair loop: validates output, auto-fixes issues, retries
- Per-domain safety boundaries in generated skills
- Input sanitization against shell metacharacter injection (CSO audit fix)
- publish_preflight.sh: automated pre-release gate for GitHub standards
- card_id whitelist validation (path traversal prevention)

### Changed
- GitHub Actions pinned to SHA digests
- Internal IP references replaced with environment variables in SKILL.md
- Legacy extract.py converted from shell=True to list-form subprocess
- uv.lock now tracked by git (removed from .gitignore)
- races/, research/, experiments/ removed from public repo

### Security
- CSO audit: 6 HIGH findings fixed, 6 MEDIUM documented
- Full report in .gstack/security-reports/

## [11.0.0] - 2026-03-25

### Added
- Domain brick integration: 278 bricks across 34 domains injected into extraction prompts
- Fast path synthesis: Python-only compilation (no LLM), 52s to 14s
- GitHub search rewrite: qualifiers, README via API, relevance scoring, parallel processing
- Debug logging mode (--debug flag)

### Changed
- Intent recognition with LLM confidence scoring
- Socratic gate: low-confidence inputs return clarifying questions instead of blind search
- GitHub search timeout: 360s to 60s

## [10.0.0] - 2026-03-25
## [12.1.0] - 2026-03-28

### Fixed (S-tier — pipeline was fundamentally broken)
- Engine path resolution: _find_engine() searches multiple candidate paths (engine was never invoked)
- LLM retry: 3 attempts with exponential backoff + jitter + adaptive timeout (72% template fallback → <10%)
- Brick contamination: affinity_terms validation + max-1-domain guard + word-boundary matching (17% cross-domain pollution → ~0%)
- CWD self-reference: read_repo_files rejects empty/relative paths (was reading own README as target project)

### Added (A-tier — architecture improvements)
- GitHub Primary discovery: ClawHub controls search depth only, never skips GitHub. Engine + API fallback
- Section-split compiler: 5 focused LLM calls (700-1500 tokens each) replacing single 6000-token call
- Parallel soul extraction: ThreadPoolExecutor with deterministic input-order collection
- Repo type classifier: CATALOG/TOOL/FRAMEWORK, awesome-lists get shallow extraction
- 60-point quality gate: 5-dimension scoring (Coverage/Evidence/DSD/WHY/Substance) before delivery
- CJK-aware slugify: semantic word-boundary truncation, max 40 chars
- 4-tier graceful degradation: FULL/PARTIAL_SOULS/FAST_PATH/TEMPLATE with completeness percentage
- Crash resume: checkpoints at Step 1 (profile) and Step 3 (souls), --resume CLI flag
- Thread-safe logging with threading.Lock

### Changed
- Fast path synthesis trigger: uses has_repo_souls check instead of dead skip_github flag
- Validator accepts Anti-Patterns & Safety section heading
- Engine subprocess passes --timeout flag (engine gets timeout-15 for graceful shutdown)
- Retry loop no longer retries deterministic errors (KeyError/ValueError/JSONDecodeError)
- Evidence scoring broadened to reward parenthetical attribution and project references


### Added
- Skill Architect: LLM-powered compilation with gold-standard reference skills
- Self-repair loop: validates output, auto-fixes issues, retries
- Per-domain safety boundaries in generated skills
- Input sanitization against shell metacharacter injection (CSO audit fix)
- `publish_preflight.sh`: automated pre-release gate for GitHub standards
- card_id whitelist validation (path traversal prevention)

### Changed
- GitHub Actions pinned to SHA digests
- Internal IP references replaced with environment variables in SKILL.md
- Legacy `extract.py` converted from `shell=True` to list-form subprocess
- `uv.lock` now tracked by git (removed from .gitignore)
- `races/`, `research/`, `experiments/` removed from public repo

### Security
- CSO audit: 6 HIGH findings fixed, 6 MEDIUM documented in TODOS
- See `.gstack/security-reports/2026-03-26-cso-report.json` for details

## [11.0.0] - 2026-03-25

### Added
- Domain brick integration: 278 bricks across 34 domains injected into extraction prompts
- Fast path synthesis: Python-only compilation (no LLM), reduces 52s to 14s
- GitHub search rewrite: qualifiers, README via API, relevance scoring, parallel processing

### Changed
- Intent recognition with LLM confidence scoring
- Socratic gate: low-confidence inputs return clarifying questions instead of blind search
- GitHub search timeout: 360s to 60s
- Timing summary fix (was double-counting)


### Changed
- Single-shot pipeline upgraded to v9.0: LLM-powered keyword generation replaces static dictionary
- Relevance gate filters irrelevant repos before extraction, returns honest "not found" when appropriate
- Skill compiler outputs actionable AI agent instruction set instead of research report
- MIN_STARS threshold lowered to 0 to include small but relevant projects
- Entry point simplified to python3 (no uv/venv dependency)

### Fixed
- Search keyword generation bug: Chinese input like "WiFi密码管理" now correctly generates English search terms via LLM
- Production-to-repo version drift resolved (OpenClaw v10.0.0 synced back to Git)

## [9.2.0] - 2026-03-24

### Added
- Mermaid pipeline diagrams in README (top-level flow + extraction internals)
- Implementation highlights with code snippets in README
- Example output section showing real TandoorRecipes extraction
- GitHub Actions CI (pytest on push/PR, Python 3.12)
- Routing decision logging in CapabilityRouter (get_routing_summary())
- CI badge support

### Changed
- brick_injection.py: expanded framework mappings from 12 to 34 domains
- SKILL.md: fixed entry point path, updated to v9.2.0
- README: updated brick count to 278, added architecture visualization

### Fixed
- SKILL.md entry point was pointing to deprecated soul-extractor path
- Brick count assertion in tests updated for 278 bricks
- Makefile PYTHONPATH for cross-package test imports

## [9.1.0] - 2026-03-24

### Added
- 189 new knowledge bricks across 22 new frameworks/domains (89→278 total)
- AI stack coverage: LangChain, HF Transformers, LlamaIndex, vLLM, CrewAI, LiteLLM, Ollama, LangGraph, llama.cpp, Diffusers, OpenAI SDK, Langfuse, DSPy
- Web framework coverage: TypeScript/Node.js, Next.js, Vue.js, Java/Spring Boot
- General coverage: Ruby/Rails, Rust, PHP/Laravel, Swift/iOS, Kotlin/Android
- Trunk-based publish_to_github.sh release script

## [9.0.0] - 2026-03-23

### Added
- 8-stage extraction pipeline (Stage 0 through Stage 5 + Assembly)
- Agentic exploration (Stage 1.5) with hypothesis-driven deep dive
- Knowledge Compiler with type-routed formatting
- Confidence system with 4-tier evidence-chain verification
- Deceptive Source Detection (8-check DSD system)
- 89 knowledge bricks across 12 frameworks and domains
- Model-agnostic design via capability router (Claude, Gemini, GPT, Ollama)
- OpenClaw skill integration (/dora command)
- Claude Code skill compatibility
- ClawHub packaging script for one-command install


## [12.0.0] - 2026-03-26