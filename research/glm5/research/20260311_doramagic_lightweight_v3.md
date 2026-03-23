# Doramagic 技术与交互方案：轻量版 + OpenClaw 生态

> 日期：2026-03-11
> 版本：v3.0（轻量版 + 最佳交互）

---

## 一、核心理念

**Doramagic = 用 LLM 调用 Skills 的「元技能」**

- 不是独立系统，就是 OpenClaw 里的一个 Skill
- 零外部依赖，只用 OpenClaw 已有能力
- 利用 LLM 的理解 + 推理 + 生成能力

---

## 二、技术架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户输入                              │
│                   "Dora 我想管 Trello"                      │
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Doramagic Skill (纯 LLM)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  意图理解   │    │  Skill 规划  │    │  上下文读取  │    │
│   │   (Prompt)  │    │   (LLM)     │    │  (记忆文件)  │    │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    │
│          │                   │                   │             │
│          └───────────────────┼───────────────────┘             │
│                              ▼                             │
│                   ┌─────────────────┐                     │
│                   │   结果组装生成   │                     │
│                   │     (LLM)      │                     │
│                   └────────┬────────┘                     │
│                            ▼                               │
└─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Skill 调用层                              │
├─────────────────────────────────────────────────────────────────┤
│                                                          │
│   Doramagic 可以调用的 OpenClaw 能力：                     │
│                                                          │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│   │  Skills  │  │   LLM   │  │  记忆   │              │
│   │ 列表检索 │  │ 代码阅读 │  │  读取   │              │
│   └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块

#### 模块 1：意图理解

```python
INTENT_PROMPT = """你是一个技能规划专家。用户说：「{user_input}」

请分析用户的意图，输出 JSON：

{{
    "capability": "用户想要的能力（如：管理 Trello、监控股票）",
    "scenario": "使用场景（如：任务管理、日常监控）",
    "entities": ["关键实体（如：Trello、A股）"],
    "confidence": 0.0-1.0,
    "needs_clarification": true/false,
    "clarification_options": ["如果需要澄清，给出选项"]
}}
"""
```

#### 模块 2：Skill 规划

```python
SKILL_PLANNING_PROMPT = """你是一个技能组合专家。

用户想要：{capability}
使用场景：{scenario}
用户上下文：{user_context}

已有 Skills：
{available_skills}

请规划：
1. 可以调用哪些现有 Skills
2. 需要生成什么新能力
3. 如何组合

输出 JSON：
{{
    "use_existing": ["Skill 列表"],
    "generate_new": ["需要生成的能力"],
    "combination": "如何组合",
    "confidence": 0.0-1.0
}}
"""
```

#### 模块 3：上下文读取

```python
def read_user_context():
    """读取用户上下文"""
    
    # 1. 读取记忆文件
    memory = read_file("~/workspace/MEMORY.md")
    
    # 2. 读取用户配置
    user = read_file("~/workspace/USER.md")
    
    # 3. 列出已安装 Skills
    skills = list_skills()
    
    # 4. 可用模型
    models = get_available_models()
    
    return {
        "memory": memory,
        "user": user,
        "skills": skills,
        "models": models
    }
```

#### 模块 4：结果组装

```python
RESULT_GENERATION_PROMPT = """你是一个友好的技能助手。

用户想要：{capability}
规划结果：{planning_result}
用户上下文：{context}

请生成最终输出：
1. 推荐哪些能力（基于用户上下文个性化）
2. 每个能力简短说明
3. 用户需要做什么选择
4. 俏皮友好的语气（像哆啦A梦）

注意：
- 最多 4 个选项
- 优先推荐匹配用户上下文的
- 让用户做选择题，不是开放式问题
"""
```

---

## 三、用户交互设计

### 3.1 交互原则

| 原则 | 实现 |
|------|------|
| **Doraemon 风格** | 俏皮、友好、有帮助 |
| **少交互** | 最多 2 轮对话完成 |
| **选择题** | 不让用户自己想，给选项 |
| **透明** | 用户知道在做什么 |

### 3.2 完整交互流程

```
用户: Dora 我想管 Trello

──────────────────────────────────────────────
🎯 分析需求中...
✓ 理解：任务管理 + Trello
✓ 检索 Skills：找到 Trello Skill
✓ 读取上下文：你有 Trello API Key

──────────────────────────────────────────────
🎉 找到啦！

【推荐】Trello 能力

你可能想要：
A) 查看我的 Board  ← 推荐！记忆里有
B) 创建新卡片
C) 移动卡片到其他列表
D) 设置提醒

你想用 Trello 做什么呀？选一个或者直接说～ 😸

──────────────────────────────────────────────

用户: A

──────────────────────────────────────────────
✓ 选好了！

帮你生成 Skill：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
名称：我的 Trello 看板助手
触发词：查看 Board、我的任务
能力：list_boards, get_board_details
配置：已就绪 ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

要保存到你的 Skills 里吗？
──────────────────────────────────────────────
```

### 3.3 特殊情况处理

#### 情况 1：用户需求不清晰

```
用户: Dora 帮我做点事

──────────────────────────────────────────────
🎯 分析中...

⚠️ 你想做什么呀？我给你几个选项：

A) 管理任务（看板、待办、日程）
B) 搜信息（Discord、网页、文档）
C) 自动化（定时提醒、跨应用同步）
D) 其他（你告诉我）

选一个或者具体说说～ 🤖
──────────────────────────────────────────────
```

#### 情况 2：没有匹配的 Skill

```
用户: Dora 我想管某个还没上线的产品

──────────────────────────────────────────────
🎯 分析中...

⚠️ 目前没有现成的 Skill 能直接用这个功能

但我可以帮你：
A) 搜一下有没有类似的开源项目
B) 创建一个基础 Skill 框架，你告诉我能力
C) 等我学会了（需要你告诉我怎么用）

你想怎么处理？😸
──────────────────────────────────────────────
```

#### 情况 3：用户直接说答案

```
用户: Dora 我就要能创建 Trello 卡片就行

──────────────────────────────────────────────
🎯 收到！

✓ 正在生成 Skill...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
名称：Trello 卡片创建助手
触发词：创建 Trello 卡片、new card
能力：create_card
配置：待配置 Trello API Key
━━━━━━━━━━━━━━━━━━

配置一下就能用啦！要我帮你配置吗？
──────────────────────────────────────────────
```

---

## 四、关键能力实现

### 4.1 灵魂提取（不依赖外部数据库）

```python
async def extract_soul(project_name: str) -> dict:
    """用 LLM 提取开源项目的「灵魂」
    
    不需要向量库，直接用 LLM 读取和分析
    """
    
    # 1. 用 LLM 读取项目 README
    readme = await llm.read_url(f"https://github.com/{project_name}/README.md")
    
    # 2. 用 LLM 提取能力
    analysis = await llm.analyze(f"""
        分析这个项目：
        {readme}
        
        输出 JSON：
        {{
            "name": "项目名",
            "purpose": "解决什么问题",
            "capabilities": ["能力1", "能力2"],
            "triggers": ["触发词1", "触发词2"],
            "resources": {{"apis": [], "tools": []}}
        }}
    """)
    
    # 3. 存入记忆文件（供后续使用）
    memory_path = f"~/workspace/memory/doramagic/{project_name}.md"
    await write_file(memory_path, analysis)
    
    return analysis
```

### 4.2 Skill 组合

```python
async def compose_skill(user_choice: str, context: dict) -> Skill:
    """根据用户选择组合 Skill"""
    
    # 1. 根据选择确定能力
    capabilities = CAPABILITY_MAP[user_choice]
    
    # 2. 生成 Skill 结构
    skill = {
        "name": f"我的 {context['capability']} 助手",
        "triggers": generate_triggers(context['capability']),
        "capabilities": capabilities,
        "dependencies": check_dependencies(capabilities),
        "config_needed": identify_config_needed(capabilities)
    }
    
    # 3. 生成 SKILL.md
    skill_md = generate_skill_md(skill)
    
    return skill
```

---

## 五、与现有系统的集成

### 5.1 调用 OpenClaw Skills

```python
async def call_skill(skill_name: str, action: str):
    """调用现有 Skill"""
    
    # 使用 OpenClaw 的 skill 调用能力
    result = await openclaw.skills.execute(
        skill=skill_name,
        action=action
    )
    return result
```

### 5.2 读取用户上下文

```python
def get_user_context() -> dict:
    """获取用户上下文"""
    
    return {
        # 记忆
        "memory": read("~/workspace/MEMORY.md"),
        "preferences": read("~/workspace/USER.md"),
        
        # Skills
        "installed_skills": list_skills(),
        
        # 模型
        "available_models": get_available_models(),
        
        # 工具
        "tools": get_available_tools()
    }
```

---

## 六、优势总结

### 轻量方案 vs 重量方案

| 维度 | 轻量版（当前） | 重量版 |
|------|----------------|---------|
| **形态** | 纯 Skill | 独立系统 |
| **依赖** | 0 | Qdrant + Neo4j |
| **部署** | 即插即用 | 需要部署 |
| **个性化** | 记忆文件 | 向量库 |
| **知识** | LLM 实时提取 | 预索引 |

### 核心优势

1. **纯 Skill** - 就是 OpenClaw 里的一个能力
2. **零外部依赖** - 不需要额外数据库/服务
3. **LLM 驱动** - 用 LLM 的理解 + 推理能力
4. **记忆系统** - 用 OpenClaw 的记忆文件做知识存储
5. **Doraemon 风格** - 俏皮友好、选择题、进度透明

---

## 七、下一步

这个方案你觉得OK吗？需要讨论：
1. 具体的 SKILL.md 结构设计？
2. 触发词和对话流程？
3. 还是其他问题？

