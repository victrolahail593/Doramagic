# Design Decisions — Brick Injection

## 1. 架构设计

### 1.1 输入输出

**输入**:
- 框架名列表（如 `["Django", "FastAPI"]`）
- 积木目录路径（包含 `*.jsonl` 文件）

**输出**:
- `domain_bricks.jsonl` — 合并后的积木文件
- `injection_context.md` — 注入文本（给 LLM 的基线知识）
- `injection_meta.json` — 元数据

### 1.2 设计原则

1. **纯确定性 Python** — 不调用 LLM
2. **不直接 import LLM SDK** — 无 anthropic/openai/google.generativeai
3. **Schema 兼容** — 使用 `DomainBrick` schema

---

## 2. 核心类

### BrickInjector

积木注入器主类：

```python
injector = BrickInjector(bricks_dir=Path("bricks"))
result = injector.inject(frameworks=["Django", "FastAPI"])
```

职责：
- 从 `*.jsonl` 文件加载积木
- 按框架名匹配 `domain_id`
- 按 token 预算选择积木
- 生成注入文本

### InjectionResult

注入结果：

```python
@dataclass
class InjectionResult:
    success: bool
    frameworks: list[str]
    matched_bricks: list[LoadedBrick]
    injection_text: str
    total_tokens: int
    stats: dict
```

---

## 3. 关键决策

### 3.1 框架名映射

使用字典将常见框架名映射到 `domain_id`：

```python
FRAMEWORK_TO_DOMAIN = {
    "django": "django",
    "fastapi": "fastapi",
    "next.js": "nextjs",
    ...
}
```

支持大小写不敏感匹配。

### 3.2 Token 预算控制

**策略**:
1. L1 积木优先（框架级，WHY 哲学）
2. 按置信度排序（high > medium > low）
3. 按支持数排序（多项目验证优先）
4. 不超过 token 预算

**默认配置**:
- 总预算: 2500 tokens
- L1 预算: 200-400 tokens
- L2 预算: 400-800 tokens

### 3.3 注入文本格式

```markdown
# 领域基线知识 (Domain Bricks)

以下知识来自多个开源项目的验证，可作为你分析项目的先验知识。
**注意：项目代码优先于这些基线知识。如果项目实际做法不同，以项目代码为准。**

## 框架级知识 (L1)

### django

- **Django ORM follows the Active Record pattern**
- 标签: orm, models
- 来源项目: wger, django-commerce

## 模式级知识 (L2)

- **N+1 queries are a common pitfall...**
  - 标签: performance, orm

---
*注入了 2 个积木，约 150 tokens*
```

关键点：
- 明确告知 LLM "项目代码优先"
- 区分 L1/L2 层级
- 显示来源和标签

### 3.4 废弃积木处理

- 默认排除带 `deprecated` 标签的积木
- 可通过 `exclude_deprecated=False` 关闭

### 3.5 置信度过滤

- 默认接受 `medium` 及以上置信度
- 可通过 `min_confidence="high"` 只选择高置信度

---

## 4. 文件格式

### 输入: bricks/*.jsonl

每行一个 JSON 对象：

```json
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
  "_layer": "L1"
}
```

### 输出: domain_bricks.jsonl

与输入格式相同，包含 `_layer` 和 `_token_estimate` 字段。

---

## 5. 扩展性

### 5.1 添加新框架

在 `FRAMEWORK_TO_DOMAIN` 字典中添加映射即可。

### 5.2 自定义选择策略

继承 `BrickInjector` 并重写 `_select_bricks_by_budget()` 方法。

### 5.3 自定义注入文本

继承 `BrickInjector` 并重写 `_build_injection_text()` 方法。

---

## 6. 错误处理

- 积木目录不存在 → 返回空结果
- JSONL 文件格式错误 → 跳过无效行
- 未知框架 → 返回空匹配

不抛出异常，保证流程继续。

---

## 7. 性能考虑

- 积木缓存：首次加载后缓存在 `_brick_cache`
- 懒加载：`load_all_bricks()` 只在需要时调用
- 简单 token 估算：约 4 字符 = 1 token

---

## 8. 测试覆盖

| 测试类 | 覆盖场景 |
|--------|----------|
| `TestFrameworkToDomain` | 框架名映射 |
| `TestBrickInjector` | 核心注入逻辑 |
| `TestInjectionResult` | 结果保存 |
| `TestBudgetControl` | 预算控制 |
| `TestQuickInject` | 便捷函数 |
| `TestDeprecationHandling` | 废弃积木 |
| `TestConfidenceFilter` | 置信度过滤 |