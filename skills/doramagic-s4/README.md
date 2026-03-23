# Doramagic S4-GLM5

**OpenClaw Skill — 从开源世界提取智慧，锻造开袋即食的知识容器**

## 概述

Doramagic S4 是一个完整的知识提取和 Skill 锻造流水线，集成 8 项研究成果：

1. **WHY 可恢复性判断** — 评估证据充分性，避免过度推理
2. **暗雷检测 (8 项 DSD 指标)** — 识别可能误导提取的项目
3. **Stage 1-4 完整流程** — Soul Extractor 验证过的提取方法论
4. **5 类知识卡片** — 概念、工作流、决策、陷阱、特征卡
5. **跨项目综合** — 共识、冲突、独有检测
6. **社区信号采集** — 从 GitHub Issues 提取真实踩坑经验
7. **预提取 API 集成** — 可选的先验知识注入
8. **暗雷叠加效应警告** — 多风险检测

## 安装

```bash
# 克隆到 OpenClaw skills 目录
git clone <repo-url> ~/.claude/skills/doramagic-s4

# 或创建符号链接
ln -s /path/to/doramagic-s4 ~/.claude/skills/doramagic-s4
```

## 使用方法

```
/dora 我想做一个管理 WiFi 密码的工具
```

Skill 将自动执行 Phase A-H 流程：

| Phase | 任务 |
|-------|------|
| A | 需求理解 — 解析关键词、意图、约束 |
| B | 作业发现 — GitHub 搜索 + 暗雷扫描 + 下载 |
| C | 灵魂提取 — Stage 1-4 完整流程 |
| D | 社区信号采集 — Issues/PRs 分析 |
| E | 跨项目综合 — 共识/冲突/独有 |
| F | Skill 锻造 — 从卡片编译输出 |
| G | 质量门控 — 验证通过 |
| H | 交付 — SKILL.md + PROVENANCE.md + LIMITATIONS.md |

## 文件结构

```
skills/doramagic-s4/
├── SKILL.md                    # 主 Skill 文件
├── README.md                   # 本文件
└── scripts/
    ├── github_search.py        # GitHub 搜索和下载
    ├── community_signals.py    # 社区信号采集
    ├── validate_skill.py       # 质量验证
    └── assemble_output.py      # 输出组装
```

## 输出交付物

```
~/clawd/doramagic/runs/<run_id>/delivery/
├── SKILL.md           # 最终 Skill（含 WHY + UNSAID）
├── PROVENANCE.md      # 知识卡片追溯
├── LIMITATIONS.md     # 能力边界 + 暗雷评估
└── cards/             # 知识卡片存档
    ├── concept/       # 概念卡
    ├── workflow/      # 工作流卡
    ├── decision/      # 决策卡
    └── trap/          # 陷阱卡
```

## 依赖

- Python 3.9+
- curl, unzip（用于下载项目）

## 参考资料

- Soul Extractor Stages: `skills/soul-extractor/stages/STAGE-*.md`
- 开发 Brief: `docs/full-integration-dev-brief.md`

## 版本历史

- v2.0.0 (2026-03-20) — 全量研究集成版
- v1.0.0 — 基础版（7 问框架）