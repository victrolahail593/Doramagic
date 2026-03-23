"""积木制作主流程 — 从项目提取结果生成积木候选。

流程:
1. 接收多项目提取结果（SynthesisDecision 列表）
2. LLM 辅助知识抽取和归类
3. 生成积木候选（Markdown + YAML frontmatter）
4. 人工审核后入库

Token 预算控制:
- L1 框架级: 200-400 tokens
- L2 模式级: 400-800 tokens
- 总注入预算: ≤ 2500 tokens
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "contracts"),
)
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared_utils"),
)

from doramagic_contracts.cross_project import SynthesisDecision
from doramagic_shared_utils.llm_adapter import LLMAdapter, LLMConfig, LLMResponse

from .brick_schema import (
    BrickCompilationResult,
    BrickContent,
    BrickLayer,
    BrickSourceFile,
    BrickSourceFrontmatter,
    estimate_tokens,
)
from .brick_compiler import BrickCompiler, RenderMode


@dataclass
class BrickMakerConfig:
    """积木制作器配置。"""

    output_dir: Path = field(default_factory=lambda: Path("bricks"))
    llm_adapter: Optional[LLMAdapter] = None
    llm_provider: str = "mock"
    llm_model: str = "mock-model"
    max_l1_tokens: int = 400
    max_l2_tokens: int = 800
    min_support_count: int = 2
    target_language: str = "zh-CN"  # 输出语言


@dataclass
class BrickCandidate:
    """积木候选。"""

    brick_id: str
    domain_id: str
    layer: BrickLayer
    source_decisions: list[SynthesisDecision]
    raw_knowledge: str
    suggested_content: Optional[BrickContent] = None
    confidence: str = "medium"
    signal: str = "ALIGNED"
    tags: list[str] = field(default_factory=list)
    token_estimate: int = 0
    needs_review: bool = True
    review_notes: str = ""


@dataclass
class BrickMakerResult:
    """积木制作结果。"""

    success: bool
    candidates: list[BrickCandidate] = field(default_factory=list)
    created_files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


class BrickMaker:
    """积木制作器。"""

    # LLM Prompt 模板
    EXTRACTION_PROMPT = """你是一个知识工程专家，负责从项目知识中提取"领域积木"。

领域积木是经过多项目验证的知识单元，可以注入到 Soul Extractor 的 Stage 0/1 加速提取过程。

## 输入
以下是从多个开源项目提取的知识决策：

{decisions_text}

## 任务
1. 识别跨项目共识知识（ALIGNED 信号）
2. 提取设计哲学（WHY）和心智模型
3. 归纳 UNSAID 知识（文档中没有但很重要的隐含知识）
4. 总结速查规则和反模式

## 输出格式
请以 JSON 格式输出：

```json
{{
  "design_philosophy": "设计哲学描述（2-3句话）",
  "mental_models": "核心心智模型（1-2句话）",
  "unsaid_knowledge": "隐含知识（3-5个要点）",
  "quick_rules": ["规则1", "规则2", "规则3"],
  "anti_patterns": ["反模式1", "反模式2"],
  "implications": "对写代码的影响",
  "suggested_tags": ["tag1", "tag2"],
  "layer_recommendation": "L1 或 L2",
  "confidence": "high/medium/low"
}}
```

## 注意事项
- 设计哲学应该解释"为什么这样设计"，而不是"怎么做"
- UNSAID 知识是文档中没有明说但开发者需要知道的陷阱
- 速查规则应该是可执行的、具体的
- 反模式是常见错误，帮助避免踩坑
"""

    LAYER_DECISION_PROMPT = """根据以下知识内容，判断它应该属于哪个层级：

L1 (框架级):
- 设计哲学和核心理念
- 框架级心智模型
- 跨所有项目通用的 WHY 层知识
- Token 预算: 200-400 tokens

L2 (模式级):
- 具体模式的 UNSAID 知识
- 常见陷阱和反模式
- 具体的速查规则
- Token 预算: 400-800 tokens

知识内容：
{content}

请只回答 "L1" 或 "L2"。
"""

    def __init__(self, config: BrickMakerConfig):
        """初始化积木制作器。"""
        self.config = config

        # 初始化 LLM Adapter
        if config.llm_adapter:
            self.llm = config.llm_adapter
        else:
            llm_config = LLMConfig(
                provider=config.llm_provider,
                model=config.llm_model,
                max_tokens=2048,
                temperature=0.3,
            )
            self.llm = LLMAdapter(llm_config)

        self.compiler = BrickCompiler()
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def make_bricks_from_decisions(
        self,
        decisions: list[SynthesisDecision],
        domain_id: str,
        project_ids: list[str],
    ) -> BrickMakerResult:
        """从知识决策生成积木候选。

        Args:
            decisions: 综合决策列表
            domain_id: 领域标识
            project_ids: 来源项目 ID 列表

        Returns:
            制作结果
        """
        result = BrickMakerResult(success=True)
        candidates: list[BrickCandidate] = []

        # 1. 按 knowledge_type 分组
        grouped = self._group_decisions(decisions)

        # 2. 识别 L1 候选（设计哲学类）
        l1_candidates = self._identify_l1_candidates(
            grouped.get("rationale", []),
            domain_id,
            project_ids,
        )
        candidates.extend(l1_candidates)

        # 3. 识别 L2 候选（模式级知识）
        l2_candidates = self._identify_l2_candidates(
            grouped,
            domain_id,
            project_ids,
        )
        candidates.extend(l2_candidates)

        # 4. LLM 辅助内容生成
        for candidate in candidates:
            try:
                self._enhance_candidate_with_llm(candidate)
            except Exception as e:
                result.errors.append(f"LLM enhancement failed for {candidate.brick_id}: {e}")

        # 5. 生成 Markdown 文件
        for candidate in candidates:
            try:
                path = self._write_brick_source(candidate)
                result.created_files.append(path)
            except Exception as e:
                result.errors.append(f"Write failed for {candidate.brick_id}: {e}")

        result.candidates = candidates
        result.stats = {
            "total_decisions": len(decisions),
            "l1_candidates": len(l1_candidates),
            "l2_candidates": len(l2_candidates),
            "total_candidates": len(candidates),
            "errors": len(result.errors),
        }

        return result

    def _group_decisions(
        self,
        decisions: list[SynthesisDecision],
    ) -> dict[str, list[SynthesisDecision]]:
        """按知识类型分组。"""
        grouped: dict[str, list[SynthesisDecision]] = {}

        for decision in decisions:
            # 从 statement 推断知识类型
            ktype = self._infer_knowledge_type(decision)
            if ktype not in grouped:
                grouped[ktype] = []
            grouped[ktype].append(decision)

        return grouped

    def _infer_knowledge_type(self, decision: SynthesisDecision) -> str:
        """从决策推断知识类型。"""
        statement = decision.statement.lower()

        # 关键词映射
        if any(kw in statement for kw in ["design", "philosophy", "why", "rationale", "principle"]):
            return "rationale"
        elif any(kw in statement for kw in ["must", "should", "constraint", "limitation", "cannot"]):
            return "constraint"
        elif any(kw in statement for kw in ["api", "interface", "function", "method", "class"]):
            return "interface"
        elif any(kw in statement for kw in ["failure", "error", "bug", "pitfall", "trap", "anti-pattern"]):
            return "failure"
        elif any(kw in statement for kw in ["pattern", "practice", "approach", "strategy"]):
            return "assembly_pattern"
        else:
            return "capability"

    def _identify_l1_candidates(
        self,
        rationale_decisions: list[SynthesisDecision],
        domain_id: str,
        project_ids: list[str],
    ) -> list[BrickCandidate]:
        """识别 L1 框架级候选。"""
        candidates = []

        if not rationale_decisions:
            # 如果没有显式 rationale，从所有决策中提取
            return candidates

        # 合并设计哲学
        statements = [d.statement for d in rationale_decisions if d.decision == "include"]
        if not statements:
            return candidates

        brick_id = f"{domain_id}-core-L1"
        raw_knowledge = "\n".join(f"- {s}" for s in statements[:5])

        candidate = BrickCandidate(
            brick_id=brick_id,
            domain_id=domain_id,
            layer=BrickLayer.L1,
            source_decisions=rationale_decisions,
            raw_knowledge=raw_knowledge,
            confidence="high" if len(statements) >= 3 else "medium",
            signal="ALIGNED",
            tags=[domain_id, "core", "philosophy"],
        )
        candidates.append(candidate)

        return candidates

    def _identify_l2_candidates(
        self,
        grouped_decisions: dict[str, list[SynthesisDecision]],
        domain_id: str,
        project_ids: list[str],
    ) -> list[BrickCandidate]:
        """识别 L2 模式级候选。"""
        candidates = []

        # 处理 constraint 和 failure
        for ktype in ["constraint", "failure", "assembly_pattern"]:
            decisions = grouped_decisions.get(ktype, [])
            if not decisions:
                continue

            # 聚合相似知识
            clusters = self._cluster_by_similarity(decisions)

            for i, cluster in enumerate(clusters[:3]):  # 最多 3 个 L2 积木
                if len(cluster) < self.config.min_support_count:
                    continue

                # 生成 brick_id
                pattern_name = self._extract_pattern_name(cluster[0].statement)
                brick_id = f"{domain_id}-{pattern_name}-L2"

                raw_knowledge = "\n".join(f"- {d.statement}" for d in cluster)

                candidate = BrickCandidate(
                    brick_id=brick_id,
                    domain_id=domain_id,
                    layer=BrickLayer.L2,
                    source_decisions=cluster,
                    raw_knowledge=raw_knowledge,
                    confidence="high" if len(cluster) >= 3 else "medium",
                    signal="ALIGNED",
                    tags=[domain_id, pattern_name, ktype],
                )
                candidates.append(candidate)

        return candidates

    def _cluster_by_similarity(
        self,
        decisions: list[SynthesisDecision],
        threshold: float = 0.5,
    ) -> list[list[SynthesisDecision]]:
        """按相似度聚类决策。

        简单实现：基于关键词重叠。
        实际应用中应使用 embedding 相似度。
        """
        if not decisions:
            return []

        clusters: list[list[SynthesisDecision]] = []
        used = set()

        for i, d1 in enumerate(decisions):
            if i in used:
                continue

            cluster = [d1]
            used.add(i)
            words1 = set(d1.statement.lower().split())

            for j, d2 in enumerate(decisions):
                if j in used:
                    continue

                words2 = set(d2.statement.lower().split())
                # Jaccard 相似度
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                similarity = intersection / union if union > 0 else 0

                if similarity >= threshold:
                    cluster.append(d2)
                    used.add(j)

            clusters.append(cluster)

        return clusters

    def _extract_pattern_name(self, statement: str) -> str:
        """从声明中提取模式名称。"""
        # 简单实现：取前几个单词
        words = statement.lower().split()
        # 过滤常见词
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into", "through", "during", "before", "after", "above", "below", "between", "under", "again", "further", "then", "once"}

        filtered = [w for w in words[:5] if w not in stop_words and len(w) > 2]
        if filtered:
            return "-".join(filtered[:2])
        return "pattern"

    def _enhance_candidate_with_llm(self, candidate: BrickCandidate) -> None:
        """使用 LLM 增强候选内容。"""
        # 构建 decisions 文本
        decisions_text = "\n".join(
            f"- [{d.decision}] {d.statement}"
            for d in candidate.source_decisions[:10]
        )

        prompt = self.EXTRACTION_PROMPT.format(decisions_text=decisions_text)

        try:
            # 调用 LLM（同步方式）
            response = self.llm.chat_sync([{"role": "user", "content": prompt}])

            # 解析 JSON 响应
            content = response.content
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)

                candidate.suggested_content = BrickContent(
                    design_philosophy=data.get("design_philosophy", ""),
                    mental_models=data.get("mental_models", ""),
                    unsaid_knowledge=data.get("unsaid_knowledge", ""),
                    quick_rules=data.get("quick_rules", ""),
                    implications=data.get("implications", ""),
                    anti_patterns=data.get("anti_patterns", ""),
                )

                # 更新标签
                if data.get("suggested_tags"):
                    candidate.tags.extend(data["suggested_tags"])
                    candidate.tags = list(set(candidate.tags))

                # 更新置信度
                if data.get("confidence"):
                    candidate.confidence = data["confidence"]

                # 更新层级建议
                if data.get("layer_recommendation"):
                    candidate.layer = BrickLayer(data["layer_recommendation"])

        except Exception:
            # LLM 失败时使用原始知识
            candidate.suggested_content = BrickContent(
                design_philosophy=candidate.raw_knowledge,
            )

        # 估算 token
        if candidate.suggested_content:
            text = self._content_to_text(candidate.suggested_content)
            candidate.token_estimate = estimate_tokens(text)

    def _content_to_text(self, content: BrickContent) -> str:
        """将 BrickContent 转换为文本。"""
        parts = []
        if content.design_philosophy:
            parts.append(content.design_philosophy)
        if content.mental_models:
            parts.append(content.mental_models)
        if content.unsaid_knowledge:
            parts.append(content.unsaid_knowledge)
        if content.quick_rules:
            parts.append(str(content.quick_rules))
        if content.implications:
            parts.append(content.implications)
        if content.anti_patterns:
            parts.append(str(content.anti_patterns))
        return " ".join(parts)

    def _write_brick_source(self, candidate: BrickCandidate) -> Path:
        """写入积木源文件。"""
        # 构建 frontmatter
        fm = BrickSourceFrontmatter(
            brick_id=candidate.brick_id,
            domain_id=candidate.domain_id,
            layer=candidate.layer,
            knowledge_type="capability",  # 默认值，可根据内容调整
            confidence=candidate.confidence,
            signal=candidate.signal,
            source_project_ids=list(set(
                d.source_refs[0] if d.source_refs else "unknown"
                for d in candidate.source_decisions
            ))[:5],
            support_count=len(candidate.source_decisions),
            tags=candidate.tags,
        )

        # 构建 content
        content = candidate.suggested_content or BrickContent(
            design_philosophy=candidate.raw_knowledge,
        )

        # 创建源文件对象
        source_file = BrickSourceFile(
            frontmatter=fm,
            content=content,
        )

        # 写入文件
        path = self.output_dir / f"{candidate.brick_id}.md"
        path.write_text(source_file.to_markdown(), encoding="utf-8")

        return path

    def compile_brick(self, source_path: Path) -> BrickCompilationResult:
        """编译积木源文件。"""
        return self.compiler.compile_file(source_path, RenderMode.FULL)


def make_bricks_from_synthesis(
    synthesis_report: dict,
    domain_id: str,
    output_dir: Path,
    llm_provider: str = "mock",
) -> BrickMakerResult:
    """便捷函数：从综合报告生成积木。

    Args:
        synthesis_report: synthesis 模块输出的报告字典
        domain_id: 领域标识
        output_dir: 输出目录
        llm_provider: LLM 提供商

    Returns:
        制作结果
    """
    # 从报告提取决策
    decisions_data = synthesis_report.get("data", {})
    selected = decisions_data.get("selected_knowledge", [])
    consensus = decisions_data.get("consensus", [])

    # 构建 SynthesisDecision 对象
    decisions = []
    for item in selected + consensus:
        decision = SynthesisDecision(
            decision_id=item.get("decision_id", ""),
            statement=item.get("statement", ""),
            decision=item.get("decision", "include"),
            rationale=item.get("rationale", ""),
            source_refs=item.get("source_refs", []),
            demand_fit=item.get("demand_fit", "medium"),
        )
        decisions.append(decision)

    # 配置
    config = BrickMakerConfig(
        output_dir=output_dir,
        llm_provider=llm_provider,
    )

    # 提取项目 ID
    project_ids = list(set(
        ref for d in decisions for ref in d.source_refs[:1]
    ))

    # 制作积木
    maker = BrickMaker(config)
    return maker.make_bricks_from_decisions(decisions, domain_id, project_ids)


class BrickReviewWorkflow:
    """积木审核工作流。"""

    def __init__(self, bricks_dir: Path):
        """初始化审核工作流。"""
        self.bricks_dir = bricks_dir
        self.pending_dir = bricks_dir / "pending"
        self.approved_dir = bricks_dir / "approved"
        self.rejected_dir = bricks_dir / "rejected"

        for d in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def submit_for_review(self, brick_path: Path) -> Path:
        """提交积木到审核队列。"""
        target = self.pending_dir / brick_path.name
        if brick_path != target:
            brick_path.rename(target)
        return target

    def approve(self, brick_id: str) -> Optional[Path]:
        """批准积木。"""
        pending = self.pending_dir / f"{brick_id}.md"
        if not pending.exists():
            return None

        approved = self.approved_dir / f"{brick_id}.md"
        pending.rename(approved)

        # 编译
        compiler = BrickCompiler(self.bricks_dir / "compiled")
        result, json_path = compiler.compile_and_save(approved)

        return json_path if result.success else None

    def reject(self, brick_id: str, reason: str) -> Optional[Path]:
        """拒绝积木。"""
        pending = self.pending_dir / f"{brick_id}.md"
        if not pending.exists():
            return None

        # 添加拒绝原因到文件
        content = pending.read_text(encoding="utf-8")
        rejected_content = f"{content}\n\n---\n\n## Rejection Reason\n\n{reason}\n"

        rejected = self.rejected_dir / f"{brick_id}.md"
        pending.rename(rejected)
        rejected.write_text(rejected_content, encoding="utf-8")

        return rejected

    def list_pending(self) -> list[Path]:
        """列出待审核积木。"""
        return list(self.pending_dir.glob("*.md"))

    def generate_review_report(self) -> str:
        """生成审核报告。"""
        pending = list(self.pending_dir.glob("*.md"))
        approved = list(self.approved_dir.glob("*.md"))
        rejected = list(self.rejected_dir.glob("*.md"))

        lines = [
            "# Brick Review Report",
            f"\nGenerated: {datetime.now().isoformat()}",
            "\n## Summary",
            f"- Pending: {len(pending)}",
            f"- Approved: {len(approved)}",
            f"- Rejected: {len(rejected)}",
        ]

        if pending:
            lines.append("\n## Pending Bricks")
            for p in pending:
                lines.append(f"- {p.stem}")

        return "\n".join(lines)