# AI Knowledge Consumption Research Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce a Chinese engineering-practice report at `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md` on the most effective knowledge delivery format for downstream AI assistants.

**Architecture:** Use a problem-driven survey workflow. First gather primary evidence on tool-specific knowledge injection formats, then gather evidence on context placement and budget engineering, then synthesize those findings into a format recommendation matrix and a Doramagic-specific compilation strategy.

**Tech Stack:** Markdown, official product documentation, public source code, prompt engineering guidance, research papers

---

### Task 1: Create report scaffold and source log

**Files:**
- Create: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`
- Create: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md`

**Step 1: Create the report section structure**

Expected: all required top-level sections exist before drafting starts

**Step 2: Create the evidence log structure**

Expected: sources are grouped by tool patterns, context engineering, compilation strategies, and benchmarks

### Task 2: Gather tool-format evidence

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`

**Step 1: Research CLAUDE.md, Cursor rules, Cursor @Docs, Copilot knowledge context, Continue @Docs, OpenAI instructions, Anthropic prompt guidance, and local Superpowers SKILL.md**

Expected: each system has a source-backed note for format, placement, and implied rationale

**Step 2: Add trustworthy secondary evidence if official docs leave implementation details unclear**

Expected: uncertainties are preserved instead of guessed

### Task 3: Gather context-management evidence

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`

**Step 1: Research system prompt vs user context vs tool results**

Expected: clear placement tradeoffs with citations

**Step 2: Research selective RAG injection vs full-context loading, and any available context-budget evidence**

Expected: the report makes evidence-based claims about token budgeting and "lost in the middle" style risks

### Task 4: Gather compilation and benchmark evidence

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`

**Step 1: Research structured-to-narrative conversion patterns**

Expected: concrete tools, libraries, or production patterns are identified

**Step 2: Research any public format-vs-performance evidence**

Expected: benchmark or A/B data is separated from anecdotal practice

### Task 5: Draft synthesis and recommendation

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`

**Step 1: Write the format recommendation**

Expected: the report clearly distinguishes structured source format from consumption format

**Step 2: Write the knowledge-type by format matrix**

Expected: different knowledge types receive different delivery recommendations if evidence supports it

**Step 3: Write the Doramagic-specific recommendation**

Expected: the report proposes how Soul Extractor output should be compiled before injection into AI assistants

### Task 6: Verify completeness and deliver

**Files:**
- Verify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`
- Verify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md`

**Step 1: Check report sections**

Run: `rg '^#|^##' /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`
Expected: all required sections exist

**Step 2: Check source coverage**

Run: `rg 'https?://' /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-sources.md | wc -l`
Expected: source log contains enough references to support each major claim

**Step 3: Check report size**

Run: `wc -m /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex/research/ai-knowledge-consumption/reports/codex-report.md`
Expected: final report is near the requested 3000-5000 Chinese-character range after editing

**Step 4: Commit**

Run: `git -C /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex add docs/plans/2026-03-12-ai-knowledge-consumption-design.md docs/plans/2026-03-12-ai-knowledge-consumption-implementation-plan.md research/ai-knowledge-consumption/reports/codex-report.md research/ai-knowledge-consumption/reports/codex-sources.md && git -C /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-ai-knowledge-consumption-codex commit -m "docs: add ai knowledge consumption codex research"`
Expected: design, plan, report, and source log are committed together
