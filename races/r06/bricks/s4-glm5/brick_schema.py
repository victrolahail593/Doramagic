"""积木 Markdown 源文件 Schema 定义。

本模块定义积木的源文件格式（Markdown + YAML frontmatter），用于人类编辑和审核。
编译后生成 DomainBrick JSON 供程序消费。

源文件格式：
---
brick_id: django-core-L1
domain_id: django
layer: L1  # L1=框架级, L2=模式级
knowledge_type: capability
confidence: high
signal: ALIGNED
source_project_ids:
  - wger
  - django-commerce
support_count: 2
tags:
  - orm
  - models
---

# Design Philosophy

Django follows the "batteries included" philosophy...

# Mental Models

ORM acts as an in-memory representation of your database...

# UNSAID Knowledge

N+1 queries are a common pitfall when using select_related...

# Quick Rules

1. Always use select_related for foreign keys
2. Use prefetch_related for many-to-many
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class BrickLayer(str, Enum):
    """积木层级。"""

    L1 = "L1"  # 框架级: 20-30个, 200-400 tokens, WHY哲学+心智模型
    L2 = "L2"  # 模式级: 60-100个, 400-800 tokens, UNSAID+速查规则


class BrickSourceFrontmatter(BaseModel):
    """积木源文件的 YAML frontmatter 部分。"""

    brick_id: str = Field(..., description="积木唯一标识，格式: {domain}-{name}-{layer}")
    domain_id: str = Field(..., description="领域标识，如 django, react")
    layer: BrickLayer = Field(..., description="积木层级: L1 或 L2")
    knowledge_type: str = Field(
        ...,
        description="知识类型: capability, rationale, constraint, interface, failure, assembly_pattern",
    )
    confidence: str = Field(..., description="置信度: high, medium, low")
    signal: str = Field(..., description="信号类型: ALIGNED, STALE, MISSING, ORIGINAL, DRIFTED, DIVERGENT, CONTESTED")
    source_project_ids: list[str] = Field(default_factory=list, description="来源项目 ID 列表")
    support_count: int = Field(default=1, ge=1, description="支持该知识的项目数量")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    version: str = Field(default="1.0.0", description="积木版本号")
    deprecated: bool = Field(default=False, description="是否已废弃")
    replacement_brick_id: Optional[str] = Field(default=None, description="废弃时的替代积木 ID")

    @field_validator("knowledge_type")
    @classmethod
    def validate_knowledge_type(cls, v: str) -> str:
        valid_types = {"capability", "rationale", "constraint", "interface", "failure", "assembly_pattern"}
        if v not in valid_types:
            raise ValueError(f"knowledge_type must be one of {valid_types}, got: {v}")
        return v

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        valid = {"high", "medium", "low"}
        if v not in valid:
            raise ValueError(f"confidence must be one of {valid}, got: {v}")
        return v

    @field_validator("signal")
    @classmethod
    def validate_signal(cls, v: str) -> str:
        valid = {"ALIGNED", "STALE", "MISSING", "ORIGINAL", "DRIFTED", "DIVERGENT", "CONTESTED"}
        if v not in valid:
            raise ValueError(f"signal must be one of {valid}, got: {v}")
        return v


class BrickContent(BaseModel):
    """积木 Markdown 内容部分。"""

    design_philosophy: str = Field(default="", description="设计哲学 (WHY)")
    mental_models: str = Field(default="", description="心智模型")
    unsaid_knowledge: str = Field(default="", description="隐含知识 (UNSAID)")
    quick_rules: str = Field(default="", description="速查规则")
    implications: str = Field(default="", description="对写代码的影响")
    anti_patterns: str = Field(default="", description="反模式警示")


class BrickSourceFile(BaseModel):
    """完整的积木源文件模型。"""

    frontmatter: BrickSourceFrontmatter
    content: BrickContent
    raw_markdown: str = Field(default="", description="原始 Markdown 内容")

    @classmethod
    def from_markdown(cls, markdown: str) -> "BrickSourceFile":
        """从 Markdown 源文件解析。"""
        # 分离 YAML frontmatter 和 Markdown 内容
        if not markdown.startswith("---"):
            raise ValueError("Markdown must start with YAML frontmatter (---)")

        parts = markdown.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid Markdown format: missing closing ---")

        yaml_content = parts[1].strip()
        body = parts[2].strip()

        # 解析 YAML
        try:
            fm_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}") from e

        frontmatter = BrickSourceFrontmatter(**fm_data)

        # 解析 Markdown 内容
        content = cls._parse_markdown_body(body)

        return cls(
            frontmatter=frontmatter,
            content=content,
            raw_markdown=markdown,
        )

    @staticmethod
    def _parse_markdown_body(body: str) -> BrickContent:
        """解析 Markdown 正文，提取各个部分。"""
        sections = {
            "design_philosophy": "",
            "mental_models": "",
            "unsaid_knowledge": "",
            "quick_rules": "",
            "implications": "",
            "anti_patterns": "",
        }

        # 标题映射
        heading_map = {
            "# design philosophy": "design_philosophy",
            "# mental models": "mental_models",
            "# unsaid knowledge": "unsaid_knowledge",
            "# quick rules": "quick_rules",
            "# implications": "implications",
            "# anti-patterns": "anti_patterns",
            "# 反模式": "anti_patterns",
            "# 设计哲学": "design_philosophy",
            "# 心智模型": "mental_models",
            "# 隐含知识": "unsaid_knowledge",
            "# 速查规则": "quick_rules",
            "# 代码影响": "implications",
        }

        current_section: Optional[str] = None
        current_content: list[str] = []

        for line in body.split("\n"):
            line_lower = line.strip().lower()

            # 检查是否是标题
            matched = False
            for heading, section_name in heading_map.items():
                if line_lower.startswith(heading):
                    # 保存前一个 section
                    if current_section and current_content:
                        sections[current_section] = "\n".join(current_content).strip()
                    current_section = section_name
                    current_content = []
                    matched = True
                    break

            if not matched and current_section:
                current_content.append(line)

        # 保存最后一个 section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return BrickContent(**sections)

    def to_markdown(self) -> str:
        """转换为 Markdown 源文件格式。"""
        # 构建 YAML frontmatter
        fm_dict = self.frontmatter.model_dump(exclude_none=True)
        yaml_str = yaml.dump(fm_dict, allow_unicode=True, sort_keys=False, default_flow_style=False)

        # 构建 Markdown 正文
        sections = []
        if self.content.design_philosophy:
            sections.append(f"# Design Philosophy\n\n{self.content.design_philosophy}")
        if self.content.mental_models:
            sections.append(f"# Mental Models\n\n{self.content.mental_models}")
        if self.content.unsaid_knowledge:
            sections.append(f"# UNSAID Knowledge\n\n{self.content.unsaid_knowledge}")
        if self.content.quick_rules:
            sections.append(f"# Quick Rules\n\n{self.content.quick_rules}")
        if self.content.implications:
            sections.append(f"# Implications\n\n{self.content.implications}")
        if self.content.anti_patterns:
            sections.append(f"# Anti-Patterns\n\n{self.content.anti_patterns}")

        body = "\n\n".join(sections)
        return f"---\n{yaml_str}---\n\n{body}"


class BrickCompilationResult(BaseModel):
    """积木编译结果。"""

    brick_id: str
    success: bool
    domain_brick_json: Optional[dict] = None
    error: Optional[str] = None
    token_estimate: int = Field(default=0, description="预估 token 数量")


class BrickLibraryIndex(BaseModel):
    """积木库索引。"""

    domain_id: str
    bricks: list[str] = Field(default_factory=list, description="brick_id 列表")
    l1_count: int = Field(default=0, description="L1 积木数量")
    l2_count: int = Field(default=0, description="L2 积木数量")
    total_tokens: int = Field(default=0, description="总 token 预算")

    def add_brick(self, brick_id: str, layer: BrickLayer, tokens: int) -> None:
        """添加积木到索引。"""
        if brick_id not in self.bricks:
            self.bricks.append(brick_id)
            if layer == BrickLayer.L1:
                self.l1_count += 1
            else:
                self.l2_count += 1
            self.total_tokens += tokens


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量。

    使用简单的启发式方法：英文约 4 字符 = 1 token，中文约 1.5 字符 = 1 token。
    实际应用中应使用 tiktoken 或类似库。
    """
    # 简单估算：平均 4 字符 = 1 token
    # 实际项目中应该使用 tiktoken
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    other_chars = len(text) - chinese_chars
    return int(chinese_chars / 1.5 + other_chars / 4)


def validate_brick_source_file(path: Path) -> tuple[bool, Optional[str], Optional[BrickSourceFile]]:
    """验证积木源文件是否有效。

    Returns:
        (is_valid, error_message, brick_source)
    """
    if not path.exists():
        return False, f"File not found: {path}", None

    if not path.suffix == ".md":
        return False, f"Expected .md file, got: {path.suffix}", None

    try:
        content = path.read_text(encoding="utf-8")
        brick = BrickSourceFile.from_markdown(content)
        return True, None, brick
    except Exception as e:
        return False, str(e), None