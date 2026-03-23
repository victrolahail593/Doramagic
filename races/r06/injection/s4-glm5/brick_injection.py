"""Brick Injection — 积木注入模块。

从 bricks 目录加载匹配的领域积木，生成注入文本供 Stage 1 使用。

设计原则：
1. 纯确定性 Python，不调用 LLM
2. 不能 import anthropic/openai/google.generativeai
3. 从 bricks/*.jsonl 加载积木（每行一个 JSON 对象）
4. 输出合并后的 domain_bricks.jsonl + 注入文本

用法：
    from brick_injection import BrickInjector, InjectionResult

    injector = BrickInjector(bricks_dir=Path("bricks"))
    result = injector.inject(frameworks=["Django", "FastAPI"])

    print(result.injection_text)  # 给 LLM 的基线知识
    result.save(output_dir=Path("output"))
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "packages" / "contracts"))

from doramagic_contracts.domain_graph import DomainBrick


# 框架名 → domain_id 映射
FRAMEWORK_TO_DOMAIN = {
    "django": "django",
    "fastapi": "fastapi",
    "flask": "flask",
    "react": "react",
    "next.js": "nextjs",
    "nextjs": "nextjs",
    "vue": "vue",
    "angular": "angular",
    "express": "express",
    "spring": "spring",
    "spring boot": "spring",
    "rust": "rust",
    "go": "go",
    "python": "python",
    "typescript": "typescript",
    "javascript": "javascript",
}

# Token 预算配置
MAX_INJECTION_TOKENS = 2500
L1_TOKEN_BUDGET = 400
L2_TOKEN_BUDGET = 800


@dataclass
class InjectionConfig:
    """注入配置。"""

    max_tokens: int = MAX_INJECTION_TOKENS
    l1_token_budget: int = L1_TOKEN_BUDGET
    l2_token_budget: int = L2_TOKEN_BUDGET
    include_l1: bool = True
    include_l2: bool = True
    min_confidence: str = "medium"  # high, medium, low
    exclude_deprecated: bool = True


@dataclass
class LoadedBrick:
    """已加载的积木。"""

    brick: DomainBrick
    layer: str  # L1 or L2
    token_estimate: int
    source_file: Path


@dataclass
class InjectionResult:
    """注入结果。"""

    success: bool
    frameworks: list[str]
    matched_bricks: list[LoadedBrick]
    injection_text: str
    total_tokens: int
    stats: dict = field(default_factory=dict)

    def save(self, output_dir: Path) -> dict[str, Path]:
        """保存结果到目录。

        Returns:
            保存的文件路径字典
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = {}

        # 保存 domain_bricks.jsonl
        bricks_path = output_dir / "domain_bricks.jsonl"
        with bricks_path.open("w", encoding="utf-8") as f:
            for loaded in self.matched_bricks:
                brick_dict = loaded.brick.model_dump()
                brick_dict["_layer"] = loaded.layer
                brick_dict["_token_estimate"] = loaded.token_estimate
                f.write(json.dumps(brick_dict, ensure_ascii=False, sort_keys=True))
                f.write("\n")
        paths["bricks"] = bricks_path

        # 保存注入文本
        text_path = output_dir / "injection_context.md"
        text_path.write_text(self.injection_text, encoding="utf-8")
        paths["injection_text"] = text_path

        # 保存元数据
        meta_path = output_dir / "injection_meta.json"
        meta = {
            "success": self.success,
            "frameworks": self.frameworks,
            "total_tokens": self.total_tokens,
            "brick_count": len(self.matched_bricks),
            "l1_count": sum(1 for b in self.matched_bricks if b.layer == "L1"),
            "l2_count": sum(1 for b in self.matched_bricks if b.layer == "L2"),
            "stats": self.stats,
        }
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        paths["metadata"] = meta_path

        return paths


class BrickInjector:
    """积木注入器。"""

    def __init__(
        self,
        bricks_dir: Path,
        config: Optional[InjectionConfig] = None,
    ):
        """初始化注入器。

        Args:
            bricks_dir: 积木目录，包含 *.jsonl 文件
            config: 注入配置
        """
        self.bricks_dir = Path(bricks_dir)
        self.config = config or InjectionConfig()
        self._brick_cache: dict[str, list[LoadedBrick]] = {}

    def _normalize_framework(self, framework: str) -> str:
        """标准化框架名称为 domain_id。"""
        fw_lower = framework.lower().strip()
        return FRAMEWORK_TO_DOMAIN.get(fw_lower, fw_lower)

    def _estimate_tokens(self, brick: DomainBrick) -> int:
        """估算积木的 token 数量。"""
        # 基于 statement 和 tags 估算
        text = brick.statement
        if brick.tags:
            text += " " + " ".join(brick.tags)
        # 简单估算：约 4 字符 = 1 token
        return max(50, len(text) // 4)

    def _load_bricks_from_file(self, jsonl_path: Path) -> list[LoadedBrick]:
        """从 JSONL 文件加载积木。"""
        bricks = []

        try:
            with jsonl_path.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        brick = DomainBrick(**data)

                        # 跳过废弃积木
                        if self.config.exclude_deprecated and brick.tags and "deprecated" in brick.tags:
                            continue

                        # 跳过低置信度积木
                        confidence_order = {"high": 0, "medium": 1, "low": 2}
                        if confidence_order.get(brick.confidence, 2) > confidence_order.get(self.config.min_confidence, 2):
                            continue

                        # 判断层级
                        layer = data.get("_layer", "L2")
                        token_estimate = data.get("_token_estimate") or self._estimate_tokens(brick)

                        bricks.append(LoadedBrick(
                            brick=brick,
                            layer=layer,
                            token_estimate=token_estimate,
                            source_file=jsonl_path,
                        ))
                    except Exception as e:
                        # 跳过无效行
                        continue
        except OSError:
            pass

        return bricks

    def load_all_bricks(self) -> dict[str, list[LoadedBrick]]:
        """加载所有积木，按 domain_id 分组。"""
        if self._brick_cache:
            return self._brick_cache

        bricks_by_domain: dict[str, list[LoadedBrick]] = {}

        # 遍历 bricks 目录下的所有 jsonl 文件
        if not self.bricks_dir.exists():
            return bricks_by_domain

        for jsonl_file in self.bricks_dir.glob("**/*.jsonl"):
            loaded = self._load_bricks_from_file(jsonl_file)
            for lb in loaded:
                domain_id = lb.brick.domain_id
                if domain_id not in bricks_by_domain:
                    bricks_by_domain[domain_id] = []
                bricks_by_domain[domain_id].append(lb)

        self._brick_cache = bricks_by_domain
        return bricks_by_domain

    def _select_bricks_by_budget(
        self,
        bricks: list[LoadedBrick],
        max_tokens: int,
    ) -> list[LoadedBrick]:
        """按 token 预算选择积木。

        策略：
        1. 优先选择 L1 积木（框架级）
        2. 按置信度排序
        3. 按支持数排序
        4. 不超过 token 预算
        """
        # 排序：L1 优先，然后按置信度和支持数
        confidence_order = {"high": 0, "medium": 1, "low": 2}

        def sort_key(lb: LoadedBrick):
            layer_priority = 0 if lb.layer == "L1" else 1
            confidence = confidence_order.get(lb.brick.confidence, 2)
            support = -lb.brick.support_count  # 负数，大的排前面
            return (layer_priority, confidence, support)

        sorted_bricks = sorted(bricks, key=sort_key)

        selected = []
        total_tokens = 0

        for lb in sorted_bricks:
            if total_tokens + lb.token_estimate <= max_tokens:
                selected.append(lb)
                total_tokens += lb.token_estimate

        return selected

    def _build_injection_text(self, bricks: list[LoadedBrick]) -> str:
        """构建注入文本。

        格式化积木内容，供 LLM 作为基线知识。
        """
        if not bricks:
            return ""

        lines = [
            "# 领域基线知识 (Domain Bricks)",
            "",
            "以下知识来自多个开源项目的验证，可作为你分析项目的先验知识。",
            "**注意：项目代码优先于这些基线知识。如果项目实际做法不同，以项目代码为准。**",
            "",
        ]

        # 按层级分组
        l1_bricks = [lb for lb in bricks if lb.layer == "L1"]
        l2_bricks = [lb for lb in bricks if lb.layer == "L2"]

        if l1_bricks:
            lines.append("## 框架级知识 (L1)")
            lines.append("")
            for lb in l1_bricks:
                lines.append(f"### {lb.brick.domain_id}")
                lines.append("")
                lines.append(f"- **{lb.brick.statement}**")
                if lb.brick.tags:
                    lines.append(f"- 标签: {', '.join(lb.brick.tags)}")
                lines.append(f"- 来源项目: {', '.join(lb.brick.source_project_ids)}")
                lines.append("")

        if l2_bricks:
            lines.append("## 模式级知识 (L2)")
            lines.append("")
            for lb in l2_bricks:
                lines.append(f"- **{lb.brick.statement}**")
                if lb.brick.tags:
                    lines.append(f"  - 标签: {', '.join(lb.brick.tags)}")
                lines.append("")

        lines.append("---")
        lines.append(f"*注入了 {len(bricks)} 个积木，约 {sum(lb.token_estimate for lb in bricks)} tokens*")

        return "\n".join(lines)

    def inject(
        self,
        frameworks: list[str],
        extra_domain_ids: Optional[list[str]] = None,
    ) -> InjectionResult:
        """执行积木注入。

        Args:
            frameworks: 框架名列表（如 ["Django", "FastAPI"]）
            extra_domain_ids: 额外的 domain_id 列表

        Returns:
            InjectionResult 实例
        """
        # 加载所有积木
        bricks_by_domain = self.load_all_bricks()

        # 确定目标 domain_ids
        domain_ids = set()
        for fw in frameworks:
            domain_id = self._normalize_framework(fw)
            domain_ids.add(domain_id)

        if extra_domain_ids:
            domain_ids.update(extra_domain_ids)

        # 收集匹配的积木
        matched_bricks: list[LoadedBrick] = []
        for domain_id in domain_ids:
            if domain_id in bricks_by_domain:
                matched_bricks.extend(bricks_by_domain[domain_id])

        # 按预算选择
        selected_bricks = self._select_bricks_by_budget(
            matched_bricks,
            self.config.max_tokens,
        )

        total_tokens = sum(lb.token_estimate for lb in selected_bricks)

        # 构建注入文本
        injection_text = self._build_injection_text(selected_bricks)

        # 统计
        stats = {
            "total_bricks_available": len(matched_bricks),
            "bricks_selected": len(selected_bricks),
            "l1_selected": sum(1 for lb in selected_bricks if lb.layer == "L1"),
            "l2_selected": sum(1 for lb in selected_bricks if lb.layer == "L2"),
            "domains_matched": list(domain_ids),
            "budget_used": total_tokens,
            "budget_limit": self.config.max_tokens,
        }

        return InjectionResult(
            success=len(selected_bricks) > 0,
            frameworks=list(frameworks),
            matched_bricks=selected_bricks,
            injection_text=injection_text,
            total_tokens=total_tokens,
            stats=stats,
        )


def quick_inject(
    frameworks: list[str],
    bricks_dir: Path,
    output_dir: Optional[Path] = None,
) -> InjectionResult:
    """便捷注入函数。

    Args:
        frameworks: 框架名列表
        bricks_dir: 积木目录
        output_dir: 可选输出目录

    Returns:
        InjectionResult 实例
    """
    injector = BrickInjector(bricks_dir)
    result = injector.inject(frameworks)

    if output_dir:
        result.save(output_dir)

    return result


# CLI 入口
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Brick Injection")
    parser.add_argument("--bricks-dir", required=True, help="Bricks directory")
    parser.add_argument("--frameworks", required=True, help="Comma-separated framework names")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--max-tokens", type=int, default=MAX_INJECTION_TOKENS)

    args = parser.parse_args()

    frameworks = [f.strip() for f in args.frameworks.split(",")]
    bricks_dir = Path(args.bricks_dir)
    output_dir = Path(args.output)

    config = InjectionConfig(max_tokens=args.max_tokens)
    injector = BrickInjector(bricks_dir, config)
    result = injector.inject(frameworks)

    paths = result.save(output_dir)

    print(f"Injection completed:")
    print(f"  Frameworks: {', '.join(result.frameworks)}")
    print(f"  Bricks selected: {len(result.matched_bricks)}")
    print(f"  Total tokens: {result.total_tokens}")
    print(f"  Output files:")
    for name, path in paths.items():
        print(f"    - {name}: {path}")


if __name__ == "__main__":
    main()