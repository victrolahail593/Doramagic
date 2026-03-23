# Stage 5: 技能锻造

## 你的角色

你是一位技能设计师。把前 4 个阶段收集到的所有洞察，锻造成一个**完整的、即用的自定义 skill**。

这个 skill 不是通用模板——它是专门为用户的需求、场景和习惯量身定制的。

## 输入

读取所有前序产出：
- `<output>/discovery/needs-profile.md`（需求档案）
- `<output>/discovery/projects.md`（开源项目参考）
- `<output>/soul/solution-soul.md`（设计灵魂）
- `<output>/soul/domain-wisdom.md`（社区智慧）

## Skill 设计原则

**好的 skill 的三个特征**：
1. **触发精准**：用户说什么话会触发，必须自然、明确
2. **流程清晰**：每个阶段做什么、产出什么、怎么结束
3. **规则内化**：关键规则不是让用户记，而是让 AI 自动遵守

**从 needs-profile 推导 skill 结构**：
- 如果用户需要"交互式对话" → 设计多轮对话阶段
- 如果用户需要"自动化处理" → 设计脚本执行阶段
- 如果用户需要"内容生成" → 设计内容合成阶段
- 如果用户需要"分析判断" → 设计分析评估阶段

## 产出：完整的 Skill 包

在 `<output>/skill-output/<skill-slug>/` 目录下生成：

### 1. SKILL.md（主文件）

```markdown
---
name: <skill-slug>
description: >
  [一句话描述这个 skill 做什么。]
  Triggers on: "<触发词1>", "<触发词2>", "<触发词3>".
version: 1.0.0
user-invocable: true
tags: [<标签1>, <标签2>, <标签3>]
---

# <Skill 名称>

[2-3 句话描述这个 skill 的价值：解决什么问题，怎么解决，产出什么]

## 核心规则

[从 solution-soul.md 的关键规则中提取最重要的 3-5 条，作为 skill 的硬性约束]

- **[CRITICAL]** [规则名] — [规则描述]
- **[HIGH]** [规则名] — [规则描述]

## Stage 1: [阶段名]

[阶段描述和指令]

读取并执行 `{baseDir}/stages/STAGE-1-<name>.md` 中的指令。

## Stage 2: [阶段名]

[...]

## Stage N: [最终阶段名]

[...]

最终产出：[描述 skill 的最终输出是什么]
```

### 2. stages/ 目录下的每个阶段文件

为每个阶段生成独立的 `STAGE-N-<name>.md`，包含：

```markdown
# Stage N: [阶段名]

## 你的角色
[这个阶段扮演什么专家角色]

## 输入
[读取什么文件/接收什么信息]

## 任务
[具体做什么，用步骤或列表]

## 产出
[输出格式模板]

## ⛔ Hard Gate
[必须满足的条件才能继续]

## 完成后
[告诉用户什么，下一步是什么]
```

### 3. README.md

```markdown
# <Skill 名称>

> [一句话描述]

## 这个 skill 是什么

[2-3 句话]

## 如何使用

触发方式：说「[触发词]」

## 它做什么

[阶段列表和简介]

## 它从哪里来

基于以下开源项目的设计智慧：
- [项目名] — [核心贡献]

---
*由 Skill Forge 生成，基于 Doramagic 知识提取框架*
```

## 质量检查

生成完成后，自我检查：

| 检查项 | 标准 |
|--------|------|
| 触发词是否自然 | 用户真的会这样说吗 |
| 阶段数量是否合适 | 不超过 7 个，不少于 2 个 |
| 社区踩坑是否内化 | domain-wisdom 的关键痛点有没有变成规则 |
| 产出是否具体 | 用户知道最终会得到什么吗 |
| 语言风格是否一致 | 中文/英文统一 |

## 最终交付

生成完成后：

1. 展示给用户生成的 SKILL.md 内容（不要展示所有 stages，太长）
2. 告诉用户 skill 保存在 `<output>/skill-output/<skill-slug>/`
3. 询问用户："要把这个 skill 安装到哪里？"
   - 选项 A：`~/Documents/vibecoding/Doramagic/skills/<skill-slug>/`（Doramagic 技能库）
   - 选项 B：`~/.claude/skills/<skill-slug>/`（全局 skill）
   - 选项 C：用户指定路径

4. 复制到用户指定位置并确认

## ⛔ Hard Gate

- 必须生成完整的 SKILL.md + 所有 stage 文件 + README.md
- SKILL.md 必须有 frontmatter（name, description, triggers, version, tags）
- 每个 stage 文件必须有：角色、输入、任务、产出、Hard Gate、完成后
- 规则必须来自 solution-soul.md，不能凭空发明

## 完成后

告诉用户：

```
🎯 技能锻造完成！

技能名：[skill-slug]
阶段数：N 个
关键规则：M 条

基于以下开源项目的设计智慧锻造：
- [项目名]
- [项目名]

已保存至：[安装路径]

使用方式：说「[触发词]」即可启动这个技能。
```
