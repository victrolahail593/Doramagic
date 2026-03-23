# Doramagic Pipeline — S1-Sonnet (R07)

桥接脚本，将 OpenClaw SKILL.md 触发层与 Doramagic Python 核心引擎连接。

## 文件

| 文件 | 角色 |
|------|------|
| `doramagic_pipeline.py` | M1 主脚本，orchestrate 整条管线 |
| `multi_extract.py` | M2 并行提取模块 |

## 用法

```bash
python3 doramagic_pipeline.py \
  --need-profile /path/to/need_profile.json \
  --repos /path/to/repos.json \
  --run-dir /path/to/run_dir \
  --bricks-dir /path/to/bricks \
  --output /path/to/delivery
```

### 参数说明

| 参数 | 必须 | 说明 |
|------|------|------|
| `--need-profile` | 是 | need_profile.json 路径 |
| `--repos` | 是 | repos.json 路径 |
| `--run-dir` | 是 | 中间产物写入目录 |
| `--bricks-dir` | 否 | 领域积木目录（默认：`bricks/`）|
| `--output` | 是 | 交付文件输出目录 |
| `--max-workers` | 否 | 并行提取 worker 数（默认：3）|
| `--timeout-per-repo` | 否 | 每个 repo 超时秒数（默认：120）|

## 输入格式

**need_profile.json**（两种格式均支持）：
```json
{
  "user_need": "我想做一个记账 app",
  "keywords": ["accounting", "finance", "budget"],
  "domain": "personal_finance"
}
```
或完整 NeedProfile 格式（`raw_input`, `intent`, `search_directions` 等）。

**repos.json**：
```json
[
  {"name": "firefly-iii", "path": "/abs/path/to/firefly-iii", "stars": 16000, "url": "..."},
  {"name": "actual", "path": "/abs/path/to/actual", "stars": 14000, "url": "..."}
]
```

## 输出

`--output` 目录下生成：
- `SKILL.md` — OpenClaw skill 主文件
- `PROVENANCE.md` — 知识溯源
- `LIMITATIONS.md` — 排除项和冲突

stdout 打印 JSON 摘要：
```json
{
  "status": "success",
  "repos_extracted": 2,
  "repos_failed": 0,
  "delivery": {
    "SKILL.md": {"path": "...", "size_bytes": 1234},
    "PROVENANCE.md": {"path": "...", "size_bytes": 567},
    "LIMITATIONS.md": {"path": "...", "size_bytes": 890}
  },
  "warnings": []
}
```

## 降级策略

| 场景 | 行为 |
|------|------|
| 单个 repo 提取失败 | 跳过，继续处理剩余 repo |
| synthesis 失败 / 仅 1 个 repo | 降级为「最佳单项目」模式 |
| skill_compiler 失败 | fallback 函数生成简化版 SKILL.md |
| 所有 repo 均失败 | exit 1 + JSON 错误 |

## Import 测试

```bash
cd /Users/tang/Documents/vibecoding/Doramagic
python3 -c "
import sys
sys.path.insert(0, 'races/r07/pipeline/s1-sonnet')
from doramagic_pipeline import main
print('import ok')
"
```
