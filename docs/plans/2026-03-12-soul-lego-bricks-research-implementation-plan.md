# Soul Lego Bricks Research Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce a Chinese research report at `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md` that evaluates optimal Soul Lego Bricks granularity from an engineering and architecture perspective.

**Architecture:** Use a problem-driven survey workflow. First gather evidence for AI tool knowledge architecture, RAG granularity engineering, and knowledge indexing/versioning. Then synthesize those findings into one report with explicit credibility labels, a granularity recommendation, a Top 20 priority list, a brick schema draft, and engineering risks.

**Tech Stack:** Markdown, official documentation, papers, public product documentation, local repository docs

---

### Task 1: Prepare report scaffold and evidence log

**Files:**
- Create: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`
- Create: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-sources.md`

**Step 1: Create report heading structure**

Expected: the report file contains all required top-level sections before detailed drafting begins.

**Step 2: Create source log structure**

Expected: the source log has sections for tools, RAG engineering, knowledge organization, and brick-format recommendations.

### Task 2: Gather evidence on AI tool knowledge architecture

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`

**Step 1: Research Cursor, GitHub Copilot, Sourcegraph Cody, and Continue.dev**

Run: targeted web lookups against official docs first, then strong secondary sources where official detail is incomplete
Expected: each tool has a short evidence block covering indexing, retrieval, framework docs, and confidence level

**Step 2: Add at least 1-2 adjacent tools if they materially inform framework pre-extraction**

Expected: the competitive landscape includes clear evidence for whether framework knowledge is prebuilt, retrieved, or left to model priors

### Task 3: Gather evidence on RAG granularity engineering

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`

**Step 1: Research chunking strategies in LlamaIndex, LangChain, and Haystack**

Expected: the report captures concrete splitter types, hierarchy patterns, and any code/document-specific guidance

**Step 2: Research benchmark evidence on chunk size, hierarchical retrieval, and adaptive chunking**

Expected: the report distinguishes what is benchmarked from what is merely recommended in framework docs

### Task 4: Gather evidence on knowledge organization and versioning

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-sources.md`
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`

**Step 1: Compare vector store, knowledge graph, and hybrid approaches**

Expected: the report names where each approach fits framework knowledge retrieval, hierarchy, and version control

**Step 2: Research public tools or patterns for knowledge compilation and versioned indexing**

Expected: the report includes real implementations or tooling references rather than abstract architecture only

### Task 5: Synthesize recommendations and ranking

**Files:**
- Modify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`

**Step 1: Write the granularity recommendation**

Expected: the recommendation explicitly compares framework-level, pattern-level, domain-level, and mixed approaches

**Step 2: Write the Top 20 priority framework/ecosystem list**

Expected: each ranked item has a short engineering-value rationale

**Step 3: Write the brick schema draft**

Expected: the report includes a concrete example and token-budget guidance

**Step 4: Write risks and failure modes**

Expected: the report names likely operational, retrieval, maintenance, and freshness risks

### Task 6: Verify completeness and source quality

**Files:**
- Verify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`
- Verify: `/Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-sources.md`

**Step 1: Check report structure**

Run: `rg '^#|^##' /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`
Expected: all major required sections exist

**Step 2: Check citation coverage**

Run: `rg 'http|https|arxiv|doi|docs\\.|github\\.com' /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md | wc -l`
Expected: enough source references are present to support each major finding

**Step 3: Check report size**

Run: `wc -m /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex/research/soul-lego-bricks/reports/codex-report.md`
Expected: the report is within the requested Chinese-length range after final editing

**Step 4: Commit**

Run: `git -C /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex add research/soul-lego-bricks/reports/codex-report.md research/soul-lego-bricks/reports/codex-sources.md docs/plans/2026-03-12-soul-lego-bricks-research-implementation-plan.md && git -C /Users/tang/Documents/vibecoding/Doramagic/.worktrees/research-soul-lego-bricks-codex commit -m "docs: add soul lego bricks codex research report"`
Expected: the research deliverable and plan are committed together
