# Race Brief: 积木注入 (Brick Injection into Stage 1/2/3)

> **Race ID**: r06-injection
> **赛道**: E

## 任务

实现积木注入 Stage 1/2/3 的机制。当 Stage 0 检测到目标项目使用 Django/FastAPI/React 等框架时，自动加载对应积木，注入到后续 Stage 的 prompt 中。

## 核心逻辑

1. **框架检测**（Stage 0 已有 repo_facts.frameworks）→ 匹配积木库
2. **积木加载** → 从 `bricks/{framework}.jsonl` 读取 DomainBrick 对象
3. **注入 Stage 1** → 积木作为 domain_bricks 字段传入，告诉 LLM "你已经知道这些基线知识"
4. **注入 Stage 2/3** → 积木作为锚点减少搜索面

## 输入

- `repo_facts.json` 中的 `frameworks` 字段（如 `["Django", "React"]`）
- `bricks/` 目录下的 JSONL 文件

## 输出

- `domain_bricks.jsonl` 写入 `<output>/artifacts/`（合并后的积木，供 Stage 1 读取）
- 返回积木文本摘要（供注入 prompt）

## 接口

```python
def load_and_inject_bricks(
    frameworks: list[str],
    bricks_dir: str = "bricks/",
    output_dir: str = None,
) -> BrickInjectionResult:
    """
    匹配框架 → 加载积木 → 写入 artifacts → 返回注入文本。
    """

class BrickInjectionResult:
    bricks_loaded: int
    frameworks_matched: list[str]
    injection_text: str  # 供注入 Stage 1 prompt 的文本
    bricks_path: str     # domain_bricks.jsonl 的路径
```

## 注入文本格式

```
你已经知道以下框架基线知识（来自 Doramagic 积木库）：

[Django] ORM 使用声明式模型定义，自动生成 migration。
[Django] N+1 查询是最常见性能陷阱，用 select_related/prefetch_related。
[React] Hooks 必须在组件顶层调用，不能在条件/循环中。
...

你的任务是发现这个具体项目在基线之上的独特做法。不要重复以上知识。
```

## 纯确定性。无 LLM。

## Deliverables

输出到 `races/r06/injection/{your-racer-id}/`:
1. `brick_injection.py`
2. `tests/test_brick_injection.py`
3. `DECISIONS.md`
