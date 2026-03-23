"""Domain Bricks — 积木制作与编译模块。

核心组件:
- BrickMaker: 从项目提取结果生成积木候选
- BrickCompiler: 将 Markdown 源文件编译为 DomainBrick JSON
- BrickRegistry: 积木注册表，管理积木库索引和检索

使用示例:

    # 1. 制作积木
    from brick_maker import BrickMaker, BrickMakerConfig

    config = BrickMakerConfig(
        output_dir=Path("bricks"),
        llm_provider="mock",  # 生产环境使用 "anthropic" 或 "openai"
    )
    maker = BrickMaker(config)
    result = maker.make_bricks_from_decisions(
        decisions=synthesis_decisions,
        domain_id="django",
        project_ids=["wger", "django-commerce"],
    )

    # 2. 编译积木
    from brick_compiler import BrickCompiler, RenderMode

    compiler = BrickCompiler()
    result, json_path = compiler.compile_and_save(
        source_path=Path("bricks/django-core-L1.md"),
        mode=RenderMode.FULL,
    )

    # 3. 使用积木注册表
    from brick_compiler import BrickRegistry

    registry = BrickRegistry(Path("bricks"))
    bricks = registry.get_bricks_by_domain("django")
    injection_bricks = registry.get_injection_bricks("django", max_tokens=2500)

文件结构:

    bricks/
    ├── django-core-L1.md          # L1 积木源文件
    ├── django-orm-L2.md           # L2 积木源文件
    ├── compiled/                  # 编译产物目录
    │   ├── django-core-L1.json
    │   └── django-orm-L2.json
    ├── pending/                   # 待审核积木
    ├── approved/                  # 已批准积木
    ├── rejected/                  # 已拒绝积木
    └── index.json                 # 积木库索引

Token 预算控制:
- L1 框架级: 200-400 tokens
- L2 模式级: 400-800 tokens
- 总注入预算: ≤ 2500 tokens
- 注入策略: 1×L1(full) + 2-3×L2(compact)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .brick_schema import (
    BrickCompilationResult,
    BrickContent,
    BrickLayer,
    BrickLibraryIndex,
    BrickSourceFile,
    BrickSourceFrontmatter,
    estimate_tokens,
    validate_brick_source_file,
)
from .brick_compiler import (
    BrickCompiler,
    BrickRegistry,
    RenderMode,
    compile_brick_source,
    generate_brick_injection_context,
)
from .brick_maker import (
    BrickCandidate,
    BrickMaker,
    BrickMakerConfig,
    BrickMakerResult,
    BrickReviewWorkflow,
    make_bricks_from_synthesis,
)

__all__ = [
    # Schema
    "BrickSourceFrontmatter",
    "BrickContent",
    "BrickSourceFile",
    "BrickLayer",
    "BrickLibraryIndex",
    "BrickCompilationResult",
    "estimate_tokens",
    "validate_brick_source_file",
    # Compiler
    "BrickCompiler",
    "BrickRegistry",
    "RenderMode",
    "compile_brick_source",
    "generate_brick_injection_context",
    # Maker
    "BrickMaker",
    "BrickMakerConfig",
    "BrickCandidate",
    "BrickMakerResult",
    "BrickReviewWorkflow",
    "make_bricks_from_synthesis",
]

__version__ = "0.1.0"


def quick_make_brick(
    domain_id: str,
    brick_name: str,
    layer: str,
    design_philosophy: str,
    mental_models: str = "",
    unsaid_knowledge: str = "",
    quick_rules: Optional[list[str]] = None,
    source_project_ids: Optional[list[str]] = None,
    output_dir: Optional[Path] = None,
) -> tuple[Path, Path]:
    """快速创建积木的便捷函数。

    Args:
        domain_id: 领域标识，如 "django", "react"
        brick_name: 积木名称，如 "core", "orm"
        layer: 层级，"L1" 或 "L2"
        design_philosophy: 设计哲学
        mental_models: 心智模型
        unsaid_knowledge: UNSAID 知识
        quick_rules: 速查规则列表
        source_project_ids: 来源项目 ID 列表
        output_dir: 输出目录

    Returns:
        (Markdown 源文件路径, JSON 编译产物路径)
    """
    if output_dir is None:
        output_dir = Path("bricks")

    if source_project_ids is None:
        source_project_ids = ["unknown"]

    if quick_rules is None:
        quick_rules = []

    # 创建源文件
    brick_layer = BrickLayer.L1 if layer == "L1" else BrickLayer.L2

    frontmatter = BrickSourceFrontmatter(
        brick_id=f"{domain_id}-{brick_name}-{layer}",
        domain_id=domain_id,
        layer=brick_layer,
        knowledge_type="rationale" if layer == "L1" else "assembly_pattern",
        confidence="high",
        signal="ALIGNED",
        source_project_ids=source_project_ids,
        support_count=len(source_project_ids),
        tags=[domain_id, brick_name],
    )

    content = BrickContent(
        design_philosophy=design_philosophy,
        mental_models=mental_models,
        unsaid_knowledge=unsaid_knowledge,
        quick_rules="\n".join(f"{i+1}. {r}" for i, r in enumerate(quick_rules)),
    )

    source_file = BrickSourceFile(
        frontmatter=frontmatter,
        content=content,
    )

    # 写入源文件
    md_path = output_dir / f"{frontmatter.brick_id}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(source_file.to_markdown(), encoding="utf-8")

    # 编译
    compiler = BrickCompiler(output_dir / "compiled")
    result, json_path = compiler.compile_and_save(md_path)

    return md_path, json_path if json_path else Path("")