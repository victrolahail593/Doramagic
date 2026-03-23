---
name: dora
description: >
  Doramagic: 从开源世界提取项目灵魂（知识+know-how），注入AI，让AI站在开源项目的肩膀上。
  三模块一体：灵魂提取 + 模块地图 + 社区智慧。模型无关，任何 LLM 都能用。
  Triggers on: "dora", "doramagic", "AI顾问", "extract soul", "extract knowledge", "提取知识", "提取灵魂".
version: 1.1.0
user-invocable: true
tags: [knowledge-extraction, code-analysis, ai-advisor, doramagic]
metadata:
  openclaw:
    skillKey: dora
    category: knowledge
    requires:
      bins: ["node", "npx", "git", "python3"]
---

# Doramagic v1.1

从开源世界提取项目灵魂，注入AI，让AI站在开源项目的肩膀上。

**不教用户做事，给他工具。** — 产品灵魂

v1.1 新增：知识积木注入、置信度体系、暗雷检测、Knowledge Compiler。

## Stage 0: 准备 + 确定性提取

```bash
bash {baseDir}/scripts/prepare-repo.sh "<repo_url>"
```

记住输出的 `output=` 路径，然后运行确定性事实提取：

```bash
python3 {baseDir}/scripts/extract_repo_facts.py --repo-path "<output>/artifacts/_repo" --output-dir "<output>"
```

告诉用户："代码已下载，确定性事实已提取，开始注入积木..."

## Stage 0.5: 积木注入（v1.1 新增）

检查 `<output>/artifacts/repo_facts.json` 中的 `frameworks` 字段。如果检测到框架，加载对应积木：

```bash
PYTHONPATH={baseDir}/packages/contracts:{baseDir}/packages/shared_utils:{baseDir}/packages/extraction python3 -c "
from doramagic_extraction.brick_injection import load_and_inject_bricks
import json
facts = json.load(open('<output>/artifacts/repo_facts.json'))
frameworks = facts.get('frameworks', [])
if frameworks:
    result = load_and_inject_bricks(frameworks, bricks_dir='{baseDir}/bricks/', output_dir='<output>')
    print(f'已加载 {result.bricks_loaded} 块积木，框架: {result.frameworks_matched}')
else:
    print('未检测到已知框架，跳过积木注入')
"
```

如果加载了积木，后续 Stage 1 提取时你已经知道框架基线知识，集中挖掘项目独特的 WHY/UNSAID。

## Stage 1: 灵魂发现

读取并执行 `{baseDir}/stages/STAGE-1-essence.md` 中的指令。

**v1.1 更新**：包含 WHY 可恢复性判断 + 积木注入支持。

## Stage 2: 概念卡 + 工作流卡

读取并执行 `{baseDir}/stages/STAGE-2-concepts.md` 中的指令。

## Stage 3: 规则卡

读取并执行 `{baseDir}/stages/STAGE-3-rules.md` 中的指令。

## Stage 3.5: 验证 + 置信度 + 暗雷检测

**Step 1: 格式验证**

```bash
python3 {baseDir}/scripts/validate_extraction.py --output-dir "<output>"
```

如果 BLOCKED，修复错误后重试（最多 3 次）。

**Step 2: 置信度标注（v1.1 新增）**

```bash
PYTHONPATH={baseDir}/packages/contracts:{baseDir}/packages/shared_utils:{baseDir}/packages/extraction python3 -c "
from doramagic_extraction.card_loader import load_cards_from_dir
from doramagic_extraction.confidence_system import run_evidence_tagging
cards = load_cards_from_dir('<output>')
tagged = run_evidence_tagging(cards)
verdicts = {}
for c in tagged:
    v = c.get('verdict', 'NONE')
    verdicts[v] = verdicts.get(v, 0) + 1
print(f'置信度标注完成: {verdicts}')
"
```

告诉用户 verdict 分布。REJECTED 的卡片不会进入最终输出。

**Step 3: 暗雷检测（v1.1 新增）**

```bash
PYTHONPATH={baseDir}/packages/contracts:{baseDir}/packages/shared_utils:{baseDir}/packages/extraction python3 -c "
from doramagic_extraction.card_loader import load_cards_from_dir
from doramagic_extraction.deceptive_source_detection import run_dsd_checks
import json
cards = load_cards_from_dir('<output>')
facts = json.load(open('<output>/artifacts/repo_facts.json'))
community = open('<output>/artifacts/community_signals.md').read() if __import__('os').path.exists('<output>/artifacts/community_signals.md') else ''
report = run_dsd_checks(cards, facts, community)
print(f'暗雷检测: {report.overall_status} ({sum(1 for c in report.checks if c.triggered)} 项触发)')
for c in report.checks:
    if c.triggered:
        print(f'  ⚠️ {c.check_id}: {c.detail[:100]}')
"
```

DSD 是 WARNING 不是 BLOCKING——标注不阻断。如果 SUSPICIOUS，提醒用户注意。

## Stage 4: 专家叙事合成

读取并执行 `{baseDir}/stages/STAGE-4-synthesis.md` 中的指令。

## Stage 4.5: Knowledge Compiler（v1.1 新增）

```bash
PYTHONPATH={baseDir}/packages/contracts:{baseDir}/packages/shared_utils:{baseDir}/packages/extraction python3 -c "
from doramagic_extraction.knowledge_compiler import compile_knowledge
result = compile_knowledge('<output>')
print('Knowledge Compiler:', 'OK' if result else 'FAILED')
"
```

编译后的知识在 `<output>/soul/compiled_knowledge.md`，按类型路由格式（事实→结构化，哲学→叙事，陷阱→警告）。

## Stage M: 模块地图

读取并执行 `{baseDir}/stages/STAGE-M-modules.md` 中的指令。

## Stage C: 社区智慧合成

读取并执行 `{baseDir}/stages/STAGE-C-community.md` 中的指令。

## Stage F: 组装产出

```bash
python3 {baseDir}/scripts/assemble_output.py --output-dir "<output>"
```

然后向用户展示 `<output>/inject/CLAUDE.md` 的内容，并告知：
- **CLAUDE.md** — 放入项目根目录，Claude Code 会自动加载
- **.cursorrules** — 放入项目根目录，Cursor 会自动加载
- **advisor-brief.md** — 非技术用户可读的顾问简介
- **soul/project_soul.md** — 完整灵魂 + 知识卡片索引
