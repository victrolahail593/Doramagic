# Doramagic S2

`skills/doramagic-s2/` 是 S2-Codex 的 Doramagic 全量研究集成交付目录。它把 Doramagic 固定为 OpenClaw Skill 形态，通过 `SKILL.md` 驱动 `/dora`，而不是通过本地 CLI 主程序启动。

## 目录结构

```text
skills/doramagic-s2/
├── SKILL.md
├── cards/
│   ├── concept/
│   ├── workflow/
│   ├── decision/
│   ├── trap/
│   └── signature/
├── scripts/
│   ├── extract_facts.py
│   ├── community_signals.py
│   ├── assemble_output.py
│   └── validate_skill.py
├── README.md
└── WORKLOG.md
```

共享的 GitHub 搜索与下载脚本继续复用 [github_search.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic/scripts/github_search.py)。

## 能力边界

AI 自身负责：

- 需求理解
- WHY / UNSAID 提取
- Soul Extractor Stage 1-4 执行
- 跨项目综合
- 专家叙事

确定性脚本负责：

- GitHub 搜索和 zip 下载
- repo facts 抽取
- 社区 signals 采集
- 最终交付文件组装
- 平台校验和研究型硬检查

## 关键集成点

- WHY 可恢复性判断
- 8 项 Deceptive Source Detection 指标
- 暗雷叠加效应高危升级
- Soul Extractor Stage 1-4
- 5 类知识卡片
- 至少 2 个项目的跨项目综合
- 社区 signals 自动采集
- 预提取 Domain API 先验知识

## 依赖

- `python3`
- `curl`
- `unzip`
- 仓库内已有 `packages/contracts/`
- 仓库内已有 `packages/extraction/`
- 仓库内已有 `packages/platform_openclaw/`
- 仓库内已有 `packages/cross_project/`

不需要额外 LLM SDK。

## 使用方式

1. 把整个 `skills/doramagic-s2/` 同步到 OpenClaw Skill 目录。
2. 让 AI 读取 [SKILL.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/SKILL.md)。
3. 通过 `/dora ...` 触发，例如：

```text
/dora 我想做一个管理 WiFi 密码的工具
```

4. AI 会按 Phase A-H 执行：
   - 查询 Domain API
   - 搜索并下载至少 2 个真实 GitHub 项目
   - 调 `extract_facts.py` 和 `community_signals.py`
   - 读 `skills/soul-extractor/stages/STAGE-*.md`
   - 产出卡片并调用 `assemble_output.py`
   - 最后调用 `validate_skill.py`

## 运行数据布局

推荐布局：

```text
~/clawd/doramagic/runs/<run_id>/
  downloads/
  artifacts/
  output/
```

其中 `output/` 会包含：

- `SKILL.md`
- `PROVENANCE.md`
- `LIMITATIONS.md`
- `cards/`
- `soul/`
- `artifacts/validation_report.json`

## 脚本说明

- [extract_facts.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/extract_facts.py)
  - 从仓库中抽确定性事实
  - 输出 README / ADR / CHANGELOG / 注释密度等 WHY / DSD 线索
- [community_signals.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/community_signals.py)
  - 采集 issue 数据
  - 输出社区频繁问题、高评论 issue、边界声明和部分 DSD 指标
- [assemble_output.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/assemble_output.py)
  - 从 `assembly-context.json` 编译最终 bundle
  - 写出 5 类知识卡片、`soul/` 镜像和 provenance 索引
- [validate_skill.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/validate_skill.py)
  - 调 `platform_openclaw.validator`
  - 追加 WHY / DSD / 卡片数量 / 暗雷叠加的研究型硬检查

## 部署注意

- 不要把运行数据写进 skill 安装目录本身，统一写到 `~/clawd/doramagic/runs/`
- GitHub API 和 `codeload.github.com` 必须可访问
- Domain API `http://192.168.1.104:8420` 可选，但命中时会提升提取质量
- 真实验证不接受 mock 或 fallback
