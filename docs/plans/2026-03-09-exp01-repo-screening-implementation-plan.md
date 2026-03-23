# AllInOne exp01 Repo Screening Skeleton Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a reusable repository-screening guide and scorecard for `exp01`, plus a current shortlist of candidate validation repositories.

**Architecture:** Capture local project criteria, combine them with a lightweight primary-source review of current GitHub repository candidates, then write the results into one reusable guide and one reusable scorecard template. Update the experiment README and main exp01 report so the selection path is anchored in the experiment skeleton.

**Tech Stack:** Markdown, GitHub primary-source links, local project documentation

---

### Task 1: Create repo-screening guide

**Files:**
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/exp01-repo-selection-guide.md`

**Step 1: Write screening principles and hard filters**
Expected: clear explanation of what counts as a good first validation repository.

**Step 2: Add weighted score dimensions**
Expected: reusable evaluation rubric for future candidate repositories.

**Step 3: Add current shortlist and recommendation**
Expected: one primary recommendation, backup choices, and one stretch candidate.

### Task 2: Create scorecard template

**Files:**
- Create: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/templates/exp01-repo-scorecard-template.md`

**Step 1: Write per-repository scoring table**
Expected: future repositories can be compared with the same dimensions.

### Task 3: Anchor the experiment docs

**Files:**
- Modify: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/README.md`
- Modify: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/exp01-minimal-pipeline-report.md`

**Step 1: Add selection guide references**
Expected: experiment docs point readers to the new screening guide and scorecard.

**Step 2: Update current candidate status**
Expected: the main exp01 report reflects the primary candidate and backups instead of `待定`.

### Task 4: Verify completeness

**Files:**
- Verify: `/Users/tang/Documents/work/vibecoding/allinone/docs/experiments/*`

**Step 1: Check new files exist**
Run: `find docs/experiments -maxdepth 2 -type f | sort`
Expected: selection guide and scorecard template appear.

**Step 2: Check main exp01 report reflects recommendation**
Run: `rg 'python-dotenv|PyJWT|itsdangerous|Requests' docs/experiments/exp01-minimal-pipeline-report.md`
Expected: current candidate status is no longer empty.

