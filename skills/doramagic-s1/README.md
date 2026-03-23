# Doramagic S1-Sonnet — 全量研究集成版

从开源世界找最好的作业，提取设计智慧（WHY + UNSAID），锻造开袋即食的 OpenClaw Skill。
集成全部 8 项研究成果。

触发词：`/dora <需求描述>`

---

## 8 项研究成果集成清单

| # | 研究成果 | 落地位置 |
|---|---------|---------|
| 1 | WHY 可恢复性判断 | SKILL.md Phase C Stage 0.5 + PROVENANCE.md |
| 2 | Deceptive Source Detection 8 指标 | SKILL.md 暗雷知识库 + Phase B 快扫 + validate_skill.py |
| 3 | 暗雷叠加效应 | SKILL.md 叠加规则 + LIMITATIONS.md 专节 |
| 4 | Soul Extractor Stage 1-4 | SKILL.md Phase C Stage 1-4（引导 AI 读 STAGE-*.md） |
| 5 | 5 类知识卡片 | cards/ 目录 + Phase C 格式规范 |
| 6 | 跨项目综合 | SKILL.md Phase E（共识/冲突/独有/假公约数检测） |
| 7 | 社区信号采集 | community_signals.py + Phase D + DSD 指标计算 |
| 8 | 预提取领域 API | SKILL.md Phase B-0（curl 查询，不可用时跳过） |

---

## 目录结构

```
skills/doramagic-s1/
├── SKILL.md                    ← 产品主入口，AI 读取后按指令执行（Phase A-H）
├── README.md                   ← 本文件
├── scripts/
│   ├── github_search.py        ← GitHub 搜索 + 下载（复用 doramagic/scripts/，PM 验证版）
│   ├── extract_facts.py        ← 确定性事实提取（复用 doramagic/scripts/）
│   ├── validate_skill.py       ← 扩展版质量门控（13 项检查：原有 9 + 新增 4 个 DSD 检测）
│   ├── assemble_output.py      ← 从草稿编译最终输出（复用 doramagic/scripts/）
│   └── community_signals.py    ← 社区信号采集 + DSD 指标计算（新增，参考 soul-extractor）
└── cards/                      ← 知识卡片（跨 run 共享，按项目前缀区分）
    ├── concept/                ← 概念卡（CC-{REPO}-{N}.md）
    ├── workflow/               ← 工作流卡（WF-{REPO}-{N}.md）
    ├── decision/               ← 决策卡（DC-{REPO}-{N}.md）
    ├── trap/                   ← 陷阱卡（TC-{REPO}-{N}.md）
    └── signature/              ← 特征卡（SC-{REPO}-{N}.md）
```

---

## 安装

### 前置条件

- python3 >= 3.8（标准库即可，无需 pip install）
- curl / unzip（系统自带）
- 网络可访问 GitHub API（api.github.com + codeload.github.com）

### 安装到 OpenClaw

```bash
# 方式一：放置在项目的 skills/ 目录下（Claude Code 会自动加载）
cp -r skills/doramagic-s1 ~/your-project/skills/

# 方式二：安装到 OpenClaw 全局 skills 目录
cp -r skills/doramagic-s1 ~/.openclaw/skills/

# 方式三：直接使用（已在本仓库中，Claude Code 已加载）
# 无需额外操作，直接在 Claude Code 中输入 /dora
```

### 安装到 Mac mini（s1-sonnet 命名空间隔离）

```bash
# 从本地推送到 Mac mini（按 namespace 隔离）
ssh tangsir@192.168.1.104 "mkdir -p ~/Doramagic-racers/s1-sonnet/skill"
scp -r skills/doramagic-s1/* tangsir@192.168.1.104:~/Doramagic-racers/s1-sonnet/skill/

# 创建运行数据目录
ssh tangsir@192.168.1.104 "mkdir -p ~/clawd/doramagic/s1-sonnet/{runs,cache,tmp,artifacts}"
```

---

## 使用方式

### 基本触发

```
/dora 我想做一个管理 WiFi 密码的工具
/dora 帮我做一个家庭健身追踪 skill
/dora 我需要一个个人财务记账 skill
```

AI 会自动执行 Phase A-H，最终在 `~/clawd/doramagic/s1-sonnet/runs/<run_id>/output/` 输出：

```
output/
├── SKILL.md        ← 锻造好的 Skill（含 WHY + UNSAID + 跨项目共识）
├── PROVENANCE.md   ← 按卡片 ID 溯源（含 Rationale Support Ratio）
└── LIMITATIONS.md  ← 暗雷评估结果 + 已知局限
```

知识卡片写入：
```
skills/doramagic-s1/cards/
├── concept/   CC-{REPO}-001.md   概念卡（至少 3 张）
├── decision/  DC-{REPO}-001.md   决策卡（至少 2 张）
├── trap/      TC-{REPO}-001.md   陷阱卡（至少 2 张）
└── signature/ SC-{REPO}-001.md   特征卡
```

---

## 脚本单独使用

```bash
# 搜索 GitHub 项目
python3 skills/doramagic-s1/scripts/github_search.py "wifi password manager" --top 5 \
  --output ~/clawd/doramagic/s1-sonnet/runs/test/discovery.json

# 下载项目
python3 skills/doramagic-s1/scripts/github_search.py --download "owner/repo" --branch main \
  --output ~/clawd/doramagic/s1-sonnet/runs/test/repos/

# 提取确定性事实
python3 skills/doramagic-s1/scripts/extract_facts.py /path/to/repo \
  --output ~/clawd/doramagic/s1-sonnet/runs/test/facts.json

# 采集社区信号（含 DSD 指标）
python3 skills/doramagic-s1/scripts/community_signals.py \
  --repo-url https://github.com/owner/repo \
  --repo-path /path/to/local/repo \
  --output ~/clawd/doramagic/s1-sonnet/runs/test/community.json

# 校验 Skill bundle（扩展版）
python3 skills/doramagic-s1/scripts/validate_skill.py /path/to/output/ \
  --output ~/clawd/doramagic/s1-sonnet/runs/test/report.json

# 组装输出文件
python3 skills/doramagic-s1/scripts/assemble_output.py \
  --skill-content-file /tmp/skill_draft.md \
  --provenance-content-file /tmp/provenance_draft.md \
  --limitations-content-file /tmp/limitations_draft.md \
  --output-dir /tmp/output/
```

---

## 扩展的 validate_skill.py（13 项检查）

在原有 9 项基础上，新增 4 项 DSD 检测：

| 检测项 | 类型 | 说明 |
|--------|------|------|
| WHY Over-Reasoning Check | warning | Rationale Support Ratio < 0.3 时告警 + Narrative-Evidence Tension 检测 |
| Provenance Card Traceability | warning | PROVENANCE.md 是否使用卡片 ID（CC-xxx, DC-xxx, TC-xxx）组织溯源 |
| Dark Trap Evaluation in LIMITATIONS | warning | LIMITATIONS.md 是否包含 DSD 暗雷评估结果 |
| WHY Recoverability Annotation | warning | SKILL.md 的 WHY 内容是否标注置信度/来源 |

---

## 验证案例（2026-03-20）

**输入：** `我想做一个管理 WiFi 密码的工具`

| 步骤 | 结果 |
|------|------|
| GitHub 搜索 | 真实调用，找到 rauchg/wifi-password (4543⭐) 和 sdushantha/wifi-password (3117⭐) |
| 暗雷快扫 | 两项目均 Low Risk（< 1 个暗雷触发） |
| WHY 可恢复性评估 | rauchg = MEDIUM（无设计文档）；sdushantha = HIGH（README 明确） |
| Soul Extractor Stage 1 | 完成 Q1-Q7，核心哲学：OS 是 WiFi 密码的唯一可信存储 |
| Stage 2 | 3 张概念卡（OS 凭证存储 + QR 导出 + 跨平台抽象） |
| Stage 3 | 2 张决策卡 + 2 张陷阱卡（Linux sudo 权限 + macOS Keychain 变化） |
| 跨项目综合 | 共识 2 项（OS 存储/CLI 优先），冲突 1 项（Shell vs Python） |
| validate_skill.py | **PASS 12/13**（1 warning：陷阱文档中 sudo 一词的预期误报） |

关键发现（WHY 样本）：
> OS 是 WiFi 密码的唯一可信存储。正确的设计不是再建一个加密数据库，
> 而是学会优雅地读取 OS 已经存好的数据（代码行为推断，置信度 MEDIUM）。

关键陷阱（UNSAID 样本）：
> macOS Ventura+ 的 Keychain 在非交互式会话（SSH/cron）中会弹出授权对话框在物理屏幕上，
> SSH 终端看不到，命令永远挂起。

---

## 架构原则

1. **AI 自身是 LLM** — SKILL.md 给 AI 指令，AI 直接完成理解/提取/叙事，不调外部 LLM API
2. **知识卡片作中间层** — Stage 1-4 产出结构化卡片，最终输出从卡片编译
3. **确定性脚本做确定性事** — 搜索/下载/校验/组装通过 exec 调用脚本
4. **暗雷是过滤器** — 检测结论写进 LIMITATIONS.md 让用户知情，不是拦截器
5. **WHY 可恢复性优先** — 没有证据不编造设计哲学，置信度明确标注

---

## 常见问题

**Q: GitHub API 有速率限制吗？**
A: 未认证用户每小时 60 次请求。普通使用足够。如遇限速（403/429），等待后重试。可设 `GITHUB_TOKEN` 环境变量提高限制。

**Q: 预提取 API 不可用怎么办？**
A: SKILL.md Phase B-0 中明确：API 是加成不是依赖。不可用时直接跳过，全流程仍可正常运行。

**Q: 生成的 Skill 质量如何保证？**
A: validate_skill.py 执行 13 项检查（9 原有 + 4 DSD 扩展）。所有 blocking 检查通过才交付。

**Q: 可以分析私有仓库吗？**
A: community_signals.py 支持 `--token` 参数或 `GITHUB_TOKEN` 环境变量。私有仓库需要有权限的 token。
