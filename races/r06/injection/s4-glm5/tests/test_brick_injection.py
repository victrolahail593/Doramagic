"""Tests for Brick Injection module."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "packages" / "contracts"))

import pytest

from brick_injection import (
    BrickInjector,
    InjectionConfig,
    InjectionResult,
    LoadedBrick,
    quick_inject,
    FRAMEWORK_TO_DOMAIN,
    MAX_INJECTION_TOKENS,
)


@pytest.fixture
def sample_bricks_dir(tmp_path: Path) -> Path:
    """创建示例积木目录。"""
    bricks_dir = tmp_path / "bricks"
    bricks_dir.mkdir()

    # 创建 Django 积木
    django_bricks = [
        {
            "brick_id": "django-orm-L1",
            "domain_id": "django",
            "knowledge_type": "rationale",
            "statement": "Django ORM follows the Active Record pattern",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["wger", "django-commerce"],
            "support_count": 2,
            "tags": ["orm", "models"],
            "_layer": "L1",
        },
        {
            "brick_id": "django-n-plus-1-L2",
            "domain_id": "django",
            "knowledge_type": "failure",
            "statement": "N+1 queries are a common pitfall when using select_related incorrectly",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["wger", "saleor"],
            "support_count": 3,
            "tags": ["performance", "orm"],
            "_layer": "L2",
        },
    ]

    django_jsonl = bricks_dir / "django.jsonl"
    with django_jsonl.open("w", encoding="utf-8") as f:
        for brick in django_bricks:
            f.write(json.dumps(brick, ensure_ascii=False))
            f.write("\n")

    # 创建 FastAPI 积木
    fastapi_bricks = [
        {
            "brick_id": "fastapi-async-L1",
            "domain_id": "fastapi",
            "knowledge_type": "capability",
            "statement": "FastAPI is built on Starlette and supports async/await natively",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["fastapi-todo", "full-stack-fastapi"],
            "support_count": 2,
            "tags": ["async", "performance"],
            "_layer": "L1",
        },
    ]

    fastapi_jsonl = bricks_dir / "fastapi.jsonl"
    with fastapi_jsonl.open("w", encoding="utf-8") as f:
        for brick in fastapi_bricks:
            f.write(json.dumps(brick, ensure_ascii=False))
            f.write("\n")

    return bricks_dir


class TestFrameworkToDomain:
    """测试框架名映射。"""

    def test_django_mapping(self):
        assert FRAMEWORK_TO_DOMAIN["django"] == "django"
        assert FRAMEWORK_TO_DOMAIN["Django"] == "django"
        assert FRAMEWORK_TO_DOMAIN["DJANGO"] == "django"

    def test_fastapi_mapping(self):
        assert FRAMEWORK_TO_DOMAIN["fastapi"] == "fastapi"
        assert FRAMEWORK_TO_DOMAIN["FastAPI"] == "fastapi"

    def test_nextjs_mapping(self):
        assert FRAMEWORK_TO_DOMAIN["next.js"] == "nextjs"
        assert FRAMEWORK_TO_DOMAIN["Next.js"] == "nextjs"

    def test_unknown_framework(self):
        # 未知框架返回小写原名
        assert FRAMEWORK_TO_DOMAIN.get("unknown-fw", "unknown-fw") == "unknown-fw"


class TestBrickInjector:
    """测试 BrickInjector 类。"""

    def test_init(self, sample_bricks_dir: Path):
        """测试初始化。"""
        injector = BrickInjector(sample_bricks_dir)
        assert injector.bricks_dir == sample_bricks_dir
        assert injector.config is not None

    def test_init_with_config(self, sample_bricks_dir: Path):
        """测试带配置初始化。"""
        config = InjectionConfig(max_tokens=1000)
        injector = BrickInjector(sample_bricks_dir, config)
        assert injector.config.max_tokens == 1000

    def test_load_all_bricks(self, sample_bricks_dir: Path):
        """测试加载所有积木。"""
        injector = BrickInjector(sample_bricks_dir)
        bricks = injector.load_all_bricks()

        assert "django" in bricks
        assert "fastapi" in bricks
        assert len(bricks["django"]) == 2
        assert len(bricks["fastapi"]) == 1

    def test_inject_single_framework(self, sample_bricks_dir: Path):
        """测试注入单个框架。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["Django"])

        assert result.success
        assert "Django" in result.frameworks
        assert len(result.matched_bricks) == 2
        assert result.total_tokens > 0

    def test_inject_multiple_frameworks(self, sample_bricks_dir: Path):
        """测试注入多个框架。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["Django", "FastAPI"])

        assert result.success
        assert len(result.matched_bricks) == 3  # 2 Django + 1 FastAPI

    def test_inject_unknown_framework(self, sample_bricks_dir: Path):
        """测试注入未知框架。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["UnknownFramework"])

        assert not result.success
        assert len(result.matched_bricks) == 0

    def test_injection_text_generation(self, sample_bricks_dir: Path):
        """测试注入文本生成。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["Django"])

        assert result.injection_text
        assert "领域基线知识" in result.injection_text
        assert "Django" in result.injection_text or "django" in result.injection_text
        assert "项目代码优先" in result.injection_text


class TestInjectionResult:
    """测试 InjectionResult 类。"""

    def test_save(self, sample_bricks_dir: Path, tmp_path: Path):
        """测试保存结果。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["Django"])

        output_dir = tmp_path / "output"
        paths = result.save(output_dir)

        assert output_dir.exists()
        assert paths["bricks"].exists()
        assert paths["injection_text"].exists()
        assert paths["metadata"].exists()

    def test_saved_bricks_format(self, sample_bricks_dir: Path, tmp_path: Path):
        """测试保存的积木格式。"""
        injector = BrickInjector(sample_bricks_dir)
        result = injector.inject(["Django"])

        output_dir = tmp_path / "output"
        paths = result.save(output_dir)

        # 读取并验证格式
        with paths["bricks"].open("r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 2  # 2 Django bricks

        for line in lines:
            data = json.loads(line)
            assert "brick_id" in data
            assert "domain_id" in data
            assert data["domain_id"] == "django"


class TestBudgetControl:
    """测试 Token 预算控制。"""

    def test_budget_limit(self, sample_bricks_dir: Path):
        """测试预算限制。"""
        config = InjectionConfig(max_tokens=100)  # 很小的预算
        injector = BrickInjector(sample_bricks_dir, config)
        result = injector.inject(["Django"])

        # 应该只选择能放下的积木
        assert result.total_tokens <= 100

    def test_l1_priority(self, sample_bricks_dir: Path):
        """测试 L1 优先选择。"""
        config = InjectionConfig(max_tokens=200)
        injector = BrickInjector(sample_bricks_dir, config)
        result = injector.inject(["Django"])

        # L1 积木应该被优先选择
        l1_count = sum(1 for lb in result.matched_bricks if lb.layer == "L1")
        assert l1_count > 0


class TestQuickInject:
    """测试便捷注入函数。"""

    def test_quick_inject(self, sample_bricks_dir: Path, tmp_path: Path):
        """测试快速注入。"""
        output_dir = tmp_path / "output"
        result = quick_inject(
            frameworks=["Django"],
            bricks_dir=sample_bricks_dir,
            output_dir=output_dir,
        )

        assert result.success
        assert output_dir.exists()


class TestDeprecationHandling:
    """测试废弃积木处理。"""

    def test_exclude_deprecated(self, tmp_path: Path):
        """测试排除废弃积木。"""
        bricks_dir = tmp_path / "bricks"
        bricks_dir.mkdir()

        # 创建一个废弃积木
        deprecated_brick = {
            "brick_id": "deprecated-brick",
            "domain_id": "test",
            "knowledge_type": "capability",
            "statement": "This is deprecated",
            "confidence": "high",
            "signal": "ALIGNED",
            "source_project_ids": ["project1"],
            "support_count": 1,
            "tags": ["deprecated"],
        }

        jsonl_path = bricks_dir / "test.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(deprecated_brick))

        config = InjectionConfig(exclude_deprecated=True)
        injector = BrickInjector(bricks_dir, config)
        result = injector.inject(["test"])

        assert len(result.matched_bricks) == 0


class TestConfidenceFilter:
    """测试置信度过滤。"""

    def test_min_confidence_high(self, tmp_path: Path):
        """测试只选择高置信度积木。"""
        bricks_dir = tmp_path / "bricks"
        bricks_dir.mkdir()

        bricks = [
            {
                "brick_id": "high-conf",
                "domain_id": "test",
                "knowledge_type": "capability",
                "statement": "High confidence",
                "confidence": "high",
                "signal": "ALIGNED",
                "source_project_ids": ["p1"],
                "support_count": 1,
            },
            {
                "brick_id": "low-conf",
                "domain_id": "test",
                "knowledge_type": "capability",
                "statement": "Low confidence",
                "confidence": "low",
                "signal": "ALIGNED",
                "source_project_ids": ["p1"],
                "support_count": 1,
            },
        ]

        jsonl_path = bricks_dir / "test.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f:
            for brick in bricks:
                f.write(json.dumps(brick))
                f.write("\n")

        config = InjectionConfig(min_confidence="high")
        injector = BrickInjector(bricks_dir, config)
        result = injector.inject(["test"])

        assert len(result.matched_bricks) == 1
        assert result.matched_bricks[0].brick.brick_id == "high-conf"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])