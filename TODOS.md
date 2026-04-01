# Doramagic TODOS

Generated from CEO Review + Eng Review on 2026-03-23.

## P1 — Next after Dual-Layer Fusion ships

### Cross-project GCD (Greatest Common Denominator)
- **What**: Implement cross-project knowledge extraction — find consensus patterns across N projects in the same domain
- **Why**: Second flywheel. More extractions → more reliable GCD → attracts same-domain users → more extractions
- **Context**: Research complete (2026-03-15). `cross_project/` package has discovery + synthesis code. `project_fingerprint.json` schema designed. Architecture prep (typed object persistence, N>1 synthesis interface) included in current build.
- **Effort**: L (human: 3-4 weeks / CC: 3-4 days)
- **Depends on**: Dual-Layer Fusion Phase 4 (E2E working) + Phase 5.5 (Brick System v2 for feedback loop)

### Phase B-H Crash Resume
- **What**: Make Phases B-H resumable from last checkpoint (currently only Phase A is resumable)
- **Why**: Phase C can take 10-30 min. Timeout/crash loses all progress.
- **Context**: Checkpoint-based lease system already persists state. Extension: save intermediate results per-phase so controller can resume mid-pipeline.
- **Effort**: M (human: 1-2 weeks / CC: 1-2 days)
- **Depends on**: Dual-Layer Fusion Phase 3 (controller wired)

## P1.5 — Codex 审查发现（2026-03-30）

### discovery_runner 中文放行条件过宽
- **What**: 非 ASCII > 30% 直接跳过相关性过滤，可能放入完全无关的仓库
- **Why**: Codex 审查指出：按字符比例绕过太粗糙，应保留弱相关校验
- **Fix**: 放行时至少检查 `candidate.name` 是否包含搜索词中的任意一个，或保留 star 数门槛
- **Severity**: MEDIUM

### DORAMAGIC_BRICKS_DIR 环境变量可能陈旧
- **What**: `setup_packages_path()` 用 `setdefault()` 设置 `DORAMAGIC_BRICKS_DIR`，不会覆盖已有值
- **Why**: 如果 shell 残留旧值，`_brick_catalog_dir()` 会读错目录，与当前 `DORAMAGIC_ROOT` 不一致
- **Fix**: 校验 env 路径与当前 root 一致，或改用 `os.environ[...] = ...` 显式覆盖
- **Severity**: MEDIUM（当前 OpenClaw 每次新进程，暂不触发）

## P2 — Medium-term

### 知识库格式统一（V1 JSONL → V2 YAML）
- **What**: 将 50 个 V1 JSONL 积木文件统一迁移为 V2 YAML 格式，当前已完成 24/50
- **Why**: V1/V2 并存导致格式分裂，维护成本高；V2 可读性更好，支持更丰富的结构（约束、场景）。知识库重构完成后需发布新版本（pip 包含 package_data）
- **Context**: bricks_v2/ 已有 25 场景文件 + 24 个已迁移文件。brick_stitcher.py 当前仅读 V1 JSONL，需适配 V2
- **Effort**: M (human: 2-3 weeks / CC: 2-3 days)
- **Depends on**: Skill 合规改造完成（pip 包架构就绪）
- **Added**: 2026-04-01，CEO 确认

### StitchCraft (Knowledge Stitching)
- **What**: Constrained knowledge combination from multiple source projects into a single skill
- **Why**: Users rarely find one perfect project — they need combinations. StitchCraft produces "combination possibility maps" not pre-sewn skills.
- **Context**: Design complete (6 conflict types: semantic, scope, architecture, dependency, operational, license). Not started.
- **Effort**: XL (human: 6-8 weeks / CC: 5-7 days)
- **Depends on**: Cross-project GCD working

### Domain Knowledge Map
- **What**: Pre-built knowledge graph per domain (finance, PKM, health, etc.) as flywheel cold-start fuel
- **Why**: When a user arrives, Doramagic already has organized memory about their domain instead of starting from scratch.
- **Context**: 6 domains selected (broad finance, PKM, private cloud, health data, information ingestion, smart home). Research at `research/pre-extraction-domains/`. Storage: SQLite + Parquet + JSONL.
- **Effort**: XL (human: 8-12 weeks / CC: 6-8 days)
- **Depends on**: Cross-project GCD + System B (preextract API)

### BrickCandidate Semantic Deduplication
- **What**: Replace exact normalized title match with embedding-based similarity for brick candidate promotion
- **Why**: LLM-generated card titles vary in phrasing even for identical concepts. Exact match produces near-zero candidates.
- **Context**: v1 uses normalized exact match (lowercase + strip punctuation + collapse whitespace). Semantic dedup requires embedding model + ANN index.
- **Effort**: M (human: 1-2 weeks / CC: 1-2 days)
- **Depends on**: Brick System v2 running with real extraction data

## P3 — Future

### Web API Adapter
- **What**: PlatformAdapter implementation for REST API deployment
- **Why**: Enables Doramagic as a standalone web service independent of OpenClaw
- **Context**: PlatformAdapter protocol designed. CLI adapter in current build. Web adapter is the next platform.
- **Effort**: M (human: 2-3 weeks / CC: 2-3 days)
- **Depends on**: Dual-Layer Fusion Phase 4 (E2E with CLI adapter working)

### User Feedback Loop
- **What**: Collect user ratings/corrections on generated skills and feed back into extraction quality
- **Why**: Closes the quality flywheel — user signal improves extraction, better extraction attracts users
- **Context**: Requires deployed product with real users. No design yet.
- **Effort**: L (human: 3-4 weeks / CC: 3-4 days)
- **Depends on**: Deployed product on OpenClaw with real usage

### Multi-language Support
- **What**: Support extraction from non-English/Chinese codebases and deliver skills in other languages
- **Why**: Expands addressable market beyond Chinese-speaking developers
- **Context**: Not started. Current system assumes Chinese user input + English code.
- **Effort**: M
- **Depends on**: Stable product with proven extraction quality

## Security — MEDIUM findings from CSO audit (2026-03-26)

### ~~Indirect prompt injection via repo content~~ FIXED 2026-03-29
- **What**: `<repo_content>` delimiter tags + system prompt injection guards added to all three LLM stage runners (Stage 1/2/3)
- **Why**: Malicious GitHub repos can embed instructions in README that manipulate extraction output
- **Files**: `packages/extraction/doramagic_extraction/llm_stage_runner.py` — DONE; `scripts/doramagic_singleshot.py` — file no longer exists

### LLM call budget in singleshot.py
- **What**: Add per-session call counter with cap + total token logging
- **Why**: Unbounded LLM API calls = unbounded Aliyun/Bailian cost per /dora invocation
- **File**: `scripts/doramagic_singleshot.py`
- **Effort**: S (CC: ~15min)

### ReDoS via LLM-controlled regex in stage15 fallback
- **What**: Add pattern length limit (max 200 chars) before `re.compile()` in Python grep fallback
- **File**: `packages/extraction/doramagic_extraction/stage15_agentic.py:340`
- **Effort**: S (CC: ~5min)

### Security tests skipped in CI
- **What**: Re-enable `test_dsd.py` and `test_confidence_system.py` in CI (mock LLM layer if needed)
- **Why**: DSD (deceptive source detection) regression would go undetected
- **File**: `.github/workflows/ci.yml:34-38`
- **Effort**: M (CC: ~30min)

### ~~Over-permissive allowed-tools in legacy skills~~ FIXED 2026-03-29
- **What**: Scoped `allowed-tools` from `[exec, read, write]` to `[read, write]` in all four legacy SKILL.md files
- **Why**: `exec` removed to eliminate prompt injection blast radius; legacy skills are race artifacts and do not need to invoke shell commands directly
- **Files**: `skills/doramagic-s{1-4}/SKILL.md`

### races/ cleanup
- **What**: `git rm -r --cached races/` to remove internal experiments from tracking (already gitignored in this commit)
- **Why**: Internal experiments should not be in public repo
- **Effort**: S (CC: ~5min)
