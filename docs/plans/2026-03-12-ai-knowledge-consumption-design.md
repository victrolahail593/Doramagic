# AI Knowledge Consumption Research Design

**Date:** 2026-03-12
**Owner:** Codex
**Scope:** `/research/ai-knowledge-consumption/reports/codex-report.md`

## Goal

Produce a Chinese research report that answers one primary engineering question: what delivery format lets downstream AI assistants consume extracted knowledge most effectively.

## Constraints

- User requested full execution without iterative discussion.
- Report target length is 3000-5000 Chinese characters.
- Every tool analysis must cite sources.
- The report must distinguish verified practice from inference.
- The output must include a concrete recommendation for Doramagic.

## Approaches Considered

### 1. Tool-by-tool survey

Compare each AI tool independently, then summarize common patterns.

**Pros:** straightforward, source-friendly, easy to verify  
**Cons:** tends to become descriptive rather than decision-oriented

### 2. Prompt-format theory first

Lead with prompt engineering and context-window theory, then map tools onto the theory.

**Pros:** stronger conceptual frame  
**Cons:** risks drifting away from practical product evidence

### 3. Problem-driven comparison matrix

Use one evaluation frame across all tools and evidence sources: format, placement, retrieval granularity, and context budget. Then map those findings into a knowledge-type-by-format recommendation matrix.

**Pros:** most decision-useful for Doramagic  
**Cons:** requires tighter synthesis discipline

## Chosen Approach

Approach 3: problem-driven comparison matrix.

The report will answer a single question: when knowledge is extracted for downstream AI consumption, should it stay structured, become narrative, or be compiled into a hybrid format?

## Core Evaluation Dimensions

1. Model readability: how naturally the format aligns with LLM pretraining and instruction-following behavior
2. Retrieval precision: how well the format supports chunking, filtering, and selective injection
3. Operational maintainability: how easy the format is to author, diff, version, and validate
4. Context efficiency: how much useful signal the format delivers per token
5. Placement compatibility: whether the format works best in system instructions, user context, or tool results

## Evidence Tiers

### A. Verified practice

Official documentation, official prompt guides, official product docs, source code, public architecture notes, or maintainers' formal writing.

### B. High-confidence industry evidence

Maintainer discussions, strong technical analyses, community best-practice threads, or tool-specific implementation notes.

### C. Inference and recommendation

Doramagic-specific synthesis derived from A and B.

## Report Structure

1. Executive summary
2. Problem definition: knowledge delivery as a downstream consumption problem
3. Real-world tool patterns
4. Context management engineering
5. Format compilation strategies
6. Recommendation matrix by knowledge type
7. Concrete Doramagic recommendation
8. Risks and unknowns
9. Sources

## Output Hypothesis To Test

The working hypothesis is not that one format wins universally. The more likely result is:

- narrative Markdown works best for philosophy, workflow, and behavioral guidance
- structured formats work best as source-of-truth and retrieval metadata
- the highest-performing production pattern is a compiled hybrid: structured source, narrative consumption layer
