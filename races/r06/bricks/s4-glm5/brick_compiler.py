"""积木编译器 — 将 Markdown 源文件编译为 DomainBrick JSON。

编译流程:
1. 读取 Markdown 源文件
2. 解析 YAML frontmatter 和正文
3. 构建 DomainBrick 对象
4. 输出 JSON 文件

支持两种渲染模式:
- full: 完整内容，用于积木库存储
- compact: 压缩内容，用于注入 LLM context
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Optional

# 使用 sys.path 确保 imports 工作
import sys

sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "contracts"),
)

from doramagic_contracts.base import Confidence, EvidenceRef, KnowledgeType, SignalKind
from doramagic_contracts.domain_graph import DomainBrick

from .brick_schema import (
    BrickCompilationResult,
    BrickLayer,
    BrickSourceFile,
    estimate_tokens,
)


class RenderMode(str, Enum):
    """渲染模式。"""

    FULL = "full"  # 完整版，用于存储
    COMPACT = "compact"  # 压缩版，用于 LLM 注入


class BrickCompiler:
    """积木编译器。"""

    def __init__(self, output_dir: Optional[Path] = None):
        """初始化编译器。

        Args:
            output_dir: 编译产物输出目录，默认为源文件同目录的 compiled/ 子目录
        """
        self.output_dir = output_dir

    def compile_file(
        self,
        source_path: Path,
        mode: RenderMode = RenderMode.FULL,
    ) -> BrickCompilationResult:
        """编译单个积木源文件。

        Args:
            source_path: Markdown 源文件路径
            mode: 渲染模式

        Returns:
            编译结果
        """
        try:
            # 读取并解析源文件
            markdown = source_path.read_text(encoding="utf-8")
            brick_source = BrickSourceFile.from_markdown(markdown)

            # 编译为 DomainBrick
            domain_brick = self._compile_to_domain_brick(brick_source, mode)

            # 估算 token
            statement = self._build_statement(brick_source, mode)
            token_estimate = estimate_tokens(statement)

            return BrickCompilationResult(
                brick_id=brick_source.frontmatter.brick_id,
                success=True,
                domain_brick_json=domain_brick.model_dump(),
                token_estimate=token_estimate,
            )

        except Exception as e:
            return BrickCompilationResult(
                brick_id=source_path.stem,
                success=False,
                error=str(e),
            )

    def compile_and_save(
        self,
        source_path: Path,
        output_dir: Optional[Path] = None,
        mode: RenderMode = RenderMode.FULL,
    ) -> tuple[BrickCompilationResult, Optional[Path]]:
        """编译并保存 JSON 文件。

        Args:
            source_path: Markdown 源文件路径
            output_dir: 输出目录，默认为源文件同目录的 compiled/ 子目录
            mode: 渲染模式

        Returns:
            (编译结果, JSON 文件路径)
        """
        result = self.compile_file(source_path, mode)

        if not result.success:
            return result, None

        # 确定输出目录
        if output_dir is None:
            output_dir = self.output_dir
        if output_dir is None:
            output_dir = source_path.parent / "compiled"

        output_dir.mkdir(parents=True, exist_ok=True)

        # 写入 JSON 文件
        json_filename = f"{result.brick_id}.json"
        json_path = output_dir / json_filename

        json_path.write_text(
            json.dumps(result.domain_brick_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return result, json_path

    def compile_directory(
        self,
        source_dir: Path,
        output_dir: Optional[Path] = None,
        mode: RenderMode = RenderMode.FULL,
    ) -> list[BrickCompilationResult]:
        """编译目录下所有积木源文件。

        Args:
            source_dir: 源文件目录
            output_dir: 输出目录
            mode: 渲染模式

        Returns:
            编译结果列表
        """
        results = []

        for md_file in source_dir.glob("*.md"):
            result, _ = self.compile_and_save(md_file, output_dir, mode)
            results.append(result)

        return results

    def _compile_to_domain_brick(
        self,
        brick_source: BrickSourceFile,
        mode: RenderMode,
    ) -> DomainBrick:
        """将 BrickSourceFile 编译为 DomainBrick。"""
        fm = brick_source.frontmatter
        content = brick_source.content

        # 构建知识声明
        statement = self._build_statement(brick_source, mode)

        # 构建证据引用（从源文件元数据生成）
        evidence_refs = self._build_evidence_refs(brick_source)

        return DomainBrick(
            brick_id=fm.brick_id,
            domain_id=fm.domain_id,
            knowledge_type=fm.knowledge_type,  # type: ignore
            statement=statement,
            confidence=fm.confidence,  # type: ignore
            signal=fm.signal,  # type: ignore
            source_project_ids=fm.source_project_ids,
            support_count=fm.support_count,
            evidence_refs=evidence_refs,
            tags=fm.tags,
        )

    def _build_statement(
        self,
        brick_source: BrickSourceFile,
        mode: RenderMode,
    ) -> str:
        """构建知识声明文本。

        FULL 模式: 包含所有内容
        COMPACT 模式: 只包含核心内容，压缩表述
        """
        content = brick_source.content
        fm = brick_source.frontmatter

        if mode == RenderMode.COMPACT:
            return self._build_compact_statement(fm, content)
        else:
            return self._build_full_statement(fm, content)

    def _build_full_statement(
        self,
        fm,
        content,
    ) -> str:
        """构建完整声明。"""
        parts = []

        # 添加层级标识
        layer_name = "Framework-level" if fm.layer == BrickLayer.L1 else "Pattern-level"
        parts.append(f"[{layer_name}] Domain: {fm.domain_id}")

        # 设计哲学
        if content.design_philosophy:
            parts.append(f"\n## Design Philosophy\n{content.design_philosophy}")

        # 心智模型
        if content.mental_models:
            parts.append(f"\n## Mental Models\n{content.mental_models}")

        # UNSAID 知识 (L2 重点关注)
        if content.unsaid_knowledge and fm.layer == BrickLayer.L2:
            parts.append(f"\n## UNSAID Knowledge\n{content.unsaid_knowledge}")

        # 速查规则
        if content.quick_rules:
            parts.append(f"\n## Quick Rules\n{content.quick_rules}")

        # 代码影响
        if content.implications:
            parts.append(f"\n## Implications\n{content.implications}")

        # 反模式 (L2 重点关注)
        if content.anti_patterns and fm.layer == BrickLayer.L2:
            parts.append(f"\n## Anti-Patterns\n{content.anti_patterns}")

        return "\n".join(parts)

    def _build_compact_statement(
        self,
        fm,
        content,
    ) -> str:
        """构建压缩声明，用于 LLM 注入。

        Token 预算控制:
        - L1: 目标 200-400 tokens
        - L2: 目标 400-800 tokens
        """
        lines = []

        # 简短标题
        layer_short = "L1" if fm.layer == BrickLayer.L1 else "L2"
        lines.append(f"[{layer_short}/{fm.domain_id}]")

        # 核心哲学（压缩到 2-3 句）
        if content.design_philosophy:
            philosophy = self._compress_text(content.design_philosophy, max_sentences=3)
            lines.append(f"PHILOSOPHY: {philosophy}")

        # 心智模型（压缩到 1-2 句）
        if content.mental_models:
            models = self._compress_text(content.mental_models, max_sentences=2)
            lines.append(f"MODEL: {models}")

        # L2 增加 UNSAID 和规则
        if fm.layer == BrickLayer.L2:
            if content.unsaid_knowledge:
                unsaid = self._compress_text(content.unsaid_knowledge, max_sentences=3)
                lines.append(f"UNSAID: {unsaid}")

            if content.quick_rules:
                rules = self._compress_rules(content.quick_rules, max_rules=5)
                lines.append(f"RULES: {rules}")

            if content.anti_patterns:
                anti = self._compress_text(content.anti_patterns, max_sentences=2)
                lines.append(f"AVOID: {anti}")

        return "\n".join(lines)

    def _compress_text(self, text: str, max_sentences: int = 3) -> str:
        """压缩文本到指定句子数。"""
        # 简单实现：按句号分割，取前 N 句
        sentences = []
        current = []

        for char in text:
            current.append(char)
            if char in "。.!！?？":
                sentences.append("".join(current).strip())
                current = []

        if current:
            sentences.append("".join(current).strip())

        compressed = sentences[:max_sentences]
        result = " ".join(compressed)

        # 如果太长，截断并添加省略号
        if len(result) > 500:
            result = result[:497] + "..."

        return result

    def _compress_rules(self, text: str, max_rules: int = 5) -> str:
        """压缩规则到指定条数。"""
        # 按换行分割，提取规则行
        lines = text.strip().split("\n")
        rules = []

        for line in lines:
            line = line.strip()
            # 识别规则行（数字开头或 - 开头）
            if line and (line[0].isdigit() or line.startswith("-")):
                # 清理前缀
                clean_line = line.lstrip("0123456789.-) ")
                if clean_line:
                    rules.append(clean_line)

        # 取前 N 条
        compressed = rules[:max_rules]

        if not compressed:
            return text[:200] if len(text) > 200 else text

        return " | ".join(compressed)

    def _build_evidence_refs(self, brick_source: BrickSourceFile) -> list[EvidenceRef]:
        """构建证据引用列表。"""
        refs = []
        fm = brick_source.frontmatter

        # 从 source_project_ids 生成引用
        for i, project_id in enumerate(fm.source_project_ids):
            ref = EvidenceRef(
                kind="artifact_ref",
                path=f"projects/{project_id}/extraction/",
                artifact_name=f"{project_id}_soul.md",
            )
            refs.append(ref)

        return refs


def compile_brick_source(
    source_path: Path,
    output_dir: Optional[Path] = None,
    mode: RenderMode = RenderMode.FULL,
) -> tuple[BrickCompilationResult, Optional[Path]]:
    """便捷函数：编译单个积木源文件。"""
    compiler = BrickCompiler(output_dir)
    return compiler.compile_and_save(source_path, output_dir, mode)


def generate_brick_injection_context(
    brick_paths: list[Path],
    max_tokens: int = 2500,
    mode: RenderMode = RenderMode.COMPACT,
) -> str:
    """生成积木注入上下文。

    按优先级选择积木注入 LLM context:
    1. L1 框架级积木优先（1个完整版）
    2. L2 模式级积木按相关度选择（2-3个压缩版）
    3. 总 token 不超过 max_tokens

    Args:
        brick_paths: 积木 JSON 文件路径列表
        max_tokens: 最大 token 预算
        mode: 渲染模式

    Returns:
        注入上下文字符串
    """
    compiler = BrickCompiler()
    bricks_by_layer: dict[BrickLayer, list[tuple[Path, DomainBrick, int]]] = {
        BrickLayer.L1: [],
        BrickLayer.L2: [],
    }

    # 加载并分类积木
    for path in brick_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            brick = DomainBrick(**data)

            # 从 brick_id 推断层级
            if "-L1" in brick.brick_id:
                layer = BrickLayer.L1
            else:
                layer = BrickLayer.L2

            # 估算 token
            tokens = estimate_tokens(brick.statement)
            bricks_by_layer[layer].append((path, brick, tokens))

        except Exception:
            continue

    # 构建注入内容
    sections = []
    total_tokens = 0

    # 1. 添加 L1 积木（最多 1 个完整版）
    if bricks_by_layer[BrickLayer.L1]:
        path, brick, tokens = bricks_by_layer[BrickLayer.L1][0]
        if total_tokens + tokens <= max_tokens:
            sections.append(f"# Framework Knowledge\n\n{brick.statement}")
            total_tokens += tokens

    # 2. 添加 L2 积木（压缩版，直到预算用完）
    if bricks_by_layer[BrickLayer.L2]:
        pattern_sections = []
        for path, brick, tokens in bricks_by_layer[BrickLayer.L2]:
            if total_tokens + tokens <= max_tokens:
                pattern_sections.append(f"## Pattern: {brick.brick_id}\n{brick.statement}")
                total_tokens += tokens

        if pattern_sections:
            sections.append(f"\n# Pattern Knowledge\n\n" + "\n\n".join(pattern_sections))

    if not sections:
        return ""

    header = "# Domain Knowledge Injection\n\n> The following knowledge bricks are pre-validated framework patterns. Project code takes precedence over these bricks.\n\n"
    return header + "\n\n".join(sections)


class BrickRegistry:
    """积木注册表 — 管理积木库索引和检索。"""

    def __init__(self, bricks_dir: Path):
        """初始化注册表。

        Args:
            bricks_dir: 积木库目录（包含 compiled/ 子目录）
        """
        self.bricks_dir = bricks_dir
        self.compiled_dir = bricks_dir / "compiled"
        self._index: Optional[dict] = None

    def load_index(self) -> dict:
        """加载积木索引。"""
        index_path = self.bricks_dir / "index.json"
        if index_path.exists():
            return json.loads(index_path.read_text(encoding="utf-8"))
        return {}

    def save_index(self, index: dict) -> None:
        """保存积木索引。"""
        index_path = self.bricks_dir / "index.json"
        index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def rebuild_index(self) -> dict:
        """重建积木索引。"""
        index = {
            "bricks": {},
            "domains": {},
            "layers": {"L1": [], "L2": []},
            "total_bricks": 0,
        }

        if not self.compiled_dir.exists():
            return index

        for json_file in self.compiled_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                brick_id = data.get("brick_id", json_file.stem)
                domain_id = data.get("domain_id", "unknown")
                layer = "L1" if "-L1" in brick_id else "L2"

                index["bricks"][brick_id] = {
                    "path": str(json_file),
                    "domain_id": domain_id,
                    "layer": layer,
                    "tags": data.get("tags", []),
                    "token_estimate": estimate_tokens(data.get("statement", "")),
                }

                # 按域分组
                if domain_id not in index["domains"]:
                    index["domains"][domain_id] = []
                index["domains"][domain_id].append(brick_id)

                # 按层级分组
                index["layers"][layer].append(brick_id)

                index["total_bricks"] += 1

            except Exception:
                continue

        self.save_index(index)
        self._index = index
        return index

    def get_brick(self, brick_id: str) -> Optional[DomainBrick]:
        """获取指定积木。"""
        if self._index is None:
            self._index = self.load_index()

        brick_info = self._index.get("bricks", {}).get(brick_id)
        if not brick_info:
            return None

        path = Path(brick_info["path"])
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        return DomainBrick(**data)

    def get_bricks_by_domain(self, domain_id: str) -> list[DomainBrick]:
        """获取指定域的所有积木。"""
        if self._index is None:
            self._index = self.load_index()

        brick_ids = self._index.get("domains", {}).get(domain_id, [])
        bricks = []
        for bid in brick_ids:
            brick = self.get_brick(bid)
            if brick:
                bricks.append(brick)
        return bricks

    def get_bricks_by_tags(self, tags: list[str]) -> list[DomainBrick]:
        """根据标签搜索积木。"""
        if self._index is None:
            self._index = self.load_index()

        bricks = []
        for brick_id, info in self._index.get("bricks", {}).items():
            brick_tags = set(info.get("tags", []))
            if brick_tags & set(tags):  # 有交集
                brick = self.get_brick(brick_id)
                if brick:
                    bricks.append(brick)
        return bricks

    def get_injection_bricks(
        self,
        domain_id: str,
        max_tokens: int = 2500,
    ) -> list[DomainBrick]:
        """获取用于注入的积木列表。

        优先级：L1 > L2
        预算控制：总 token 不超过 max_tokens
        """
        domain_bricks = self.get_bricks_by_domain(domain_id)

        # 按层级分组
        l1_bricks = [b for b in domain_bricks if "-L1" in b.brick_id]
        l2_bricks = [b for b in domain_bricks if "-L2" in b.brick_id]

        selected = []
        total_tokens = 0

        # 添加一个 L1 积木
        for brick in l1_bricks[:1]:
            tokens = estimate_tokens(brick.statement)
            if total_tokens + tokens <= max_tokens:
                selected.append(brick)
                total_tokens += tokens

        # 添加 L2 积木直到预算用完
        for brick in l2_bricks:
            tokens = estimate_tokens(brick.statement)
            if total_tokens + tokens <= max_tokens:
                selected.append(brick)
                total_tokens += tokens

        return selected