# AllInOne exp01 Minimal Pipeline Skeleton Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the document and directory skeleton needed to run and record AllInOne's first minimal soul-extraction experiment.

**Architecture:** Build a lightweight experiments area under `docs/experiments/`, centered on one main experiment report plus reusable templates for question sets, judging, and run logs. Keep the structure implementation-ready but avoid premature scripting or infrastructure decisions.

**Tech Stack:** Markdown, filesystem directory structure, local project docs

---

### Task 1: Create experiment root docs

**Files:**
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/README.md`
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/exp01-minimal-pipeline-report.md`

**Step 1: Write README**
Describe experiment scope, naming, lifecycle, and how `exp01` fits the project.

**Step 2: Write main experiment report skeleton**
Include goals, hypotheses, success criteria, scope, workflow, evaluation method, logging fields, and result placeholders.

### Task 2: Create reusable templates

**Files:**
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/templates/exp01-question-set-template.md`
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/templates/exp01-judge-rubric.md`
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/templates/exp01-run-log-template.md`

**Step 1: Write question set template**
Define categories, metadata, and per-question answer capture fields.

**Step 2: Write judge rubric template**
Define evaluation dimensions and discrete rating guidance.

**Step 3: Write run log template**
Define execution facts, model/context metadata, metrics, issues, and artifact links.

### Task 3: Create result directories

**Files:**
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/runs/.gitkeep`
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/artifacts/.gitkeep`

**Step 1: Create empty result directories**
Expected: future run outputs and experiment artifacts have a stable home.

### Task 4: Verify completeness

**Files:**
- Verify: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/*`

**Step 1: Check directory structure**
Run: `find docs/experiments -maxdepth 2 -type f | sort`
Expected: README, main report, three templates, and `.gitkeep` files exist.

**Step 2: Check section completeness**
Run: `rg '^#' docs/experiments/exp01-minimal-pipeline-report.md`
Expected: all approved experiment sections exist.

