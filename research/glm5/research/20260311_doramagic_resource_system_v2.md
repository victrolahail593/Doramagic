# Doramagic 技术架构方案：资源检索与灵魂提取体系

> 日期：2026-03-11
> 版本：v2.0（重构版）
> 背景：基于所有研究文档综合 + Tangsir 讨论迭代

---

## 一、核心理念升级

### 1.1 之前方案的不足

之前的「资源检索」方案过于简单，仅仅是：
- 关键词搜索
- 向量检索

**遗漏了核心价值：灵魂提取**

### 1.2 新的理解

**「资源检索」 = 「灵魂提取」 + 「智能匹配」**

| 层次 | 内容 | 深度 |
|------|------|------|
| **代码层** | 项目做什么、架构意图、设计决策 | 理解 |
| **社区层** | 踩坑经验、workaround、最佳实践 | 洞察 |
| **资源层** | API、工具链、信息源、配置模板 | 整合 |
| **上下文层** | 用户记忆、偏好、可用模型 | 个性化 |

---

## 二、Doramagic 的「资源」全景图

### 2.1 资源来源

```
┌─────────────────────────────────────────────────────────────┐
│                    Doramagic 资源体系                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────┐     │
│  │              外部资源（可提取）                       │     │
│  ├─────────────────────────────────────────────────┤     │
│  │  GitHub 开源项目                                  │     │
│  │    ├─ 代码（设计意图、架构）                       │     │
│  │    ├─ Issues（踩坑经验）                          │     │
│  │    ├─ Discussions（最佳实践）                     │     │
│  │    └─ Wiki/Docs（配置模板）                       │     │
│  │                                                  │     │
│  │  OpenClaw 现有 Skills                             │     │
│  │    ├─ 能力定义                                    │     │
│  │    ├─ 触发条件                                    │     │
│  │    └─ 依赖配置                                    │     │
│  └─────────────────────────────────────────────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────┐     │
│  │              用户上下文（实时整合）                   │     │
│  ├─────────────────────────────────────────────────┤     │
│  │  OpenClaw 上下文                                 │     │
│  │    ├─ 可用模型（MiniMax, Claude, Gemini...）    │     │
│  │    ├─ 记忆文件（MEMORY.md, 记忆碎片）            │     │
│  │    ├─ 内置工具（浏览器、文件操作...）             │     │
│  │    └─ 已安装 Skills                              │     │
│  │                                                  │     │
│  │  用户对话上下文                                   │     │
│  │    └─ 当前对话历史                               │     │
│  └─────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 资源类型详细定义

| 资源类型 | 提取内容 | 提取方式 | 存储形式 |
|----------|----------|----------|----------|
| **代码灵魂** | 设计意图、架构决策、模块边界 | 代码分析 + LLM | 知识图谱 |
| **社区经验** | 踩坑记录、workaround、最佳实践 | Issues 挖掘 + NLP | 向量库 |
| **资源推荐** | API 端点、工具、信息源 | 项目生态分析 | 结构化数据库 |
| **Skill 能力** | 能力定义、触发条件 | Skill 解析 | 索引 |
| **用户上下文** | 记忆、偏好、模型 | 上下文读取 | 实时查询 |

---

## 三、技术架构设计

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          用户输入                                    │
│                    "Dora 我想管 Trello"                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    第一层：意图理解 + 上下文分析                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │   意图识别        │  │   上下文读取      │  │   置信度评估      │        │
│  │  (LLM Prompt)   │  │  (记忆+模型+工具) │  │  (多维度评分)     │        │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘        │
│           │                     │                     │                   │
│           └─────────────────┬─┴─────────────────────┘                   │
│                             ▼                                          │
│                    理解用户想要什么 + 用户的上下文                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    第二层：多源灵魂提取（核心）                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                   并行检索四大资源源                          │     │
│  │                                                              │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│     │
│  │  │ GitHub 代码 │  │ GitHub     │  │ OpenClaw   │  │ 用户上下文  ││     │
│  │  │   灵魂      │  │ 社区经验   │  │  Skills    │  │   匹配     ││     │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘│     │
│  │        │                │               │               │        │     │
│  │        ▼                ▼               ▼               ▼        │     │
│  │   代码分析器         Issues挖掘      Skill解析        上下文融合  │     │
│  │   + LLM             + NLP           + 索引           + 推荐    │     │
│  │                                                              │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                   结果融合与排序                             │     │
│  │              多源结果 → 相关度 → 个性化 → 展示               │     │
│  └──────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    第三层：智能呈现与用户交互                          │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │   能力积木呈现    │  │   配置建议       │  │   进度透明       │        │
│  │   (勾选式UI)     │  │   (开箱即用)     │  │   (实时反馈)     │        │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 核心模块详解

#### 模块 1：意图理解引擎

```python
class IntentUnderstandingEngine:
    """意图理解引擎"""
    
    def __init__(self, llm):
        self.llm = llm
        self.intent_prompt = PromptTemplate(...)
        
    async def understand(self, user_input: str) -> IntentResult:
        """理解用户意图"""
        
        # 1. 提取关键实体
        entities = self.llm.extract_entities(user_input)
        
        # 2. 识别能力需求
        capability = self.llm.detect_capability(user_input)
        
        # 3. 识别场景
        scenario = self.llm.detect_scenario(user_input)
        
        # 4. 置信度评估
        confidence = self.calculate_confidence(entities, capability, scenario)
        
        return IntentResult(
            entities=entities,
            capability=capability,
            scenario=scenario,
            confidence=confidence,
            original_input=user_input
        )
```

#### 模块 2：多源灵魂提取器

```python
class SoulExtractor:
    """灵魂提取器 - 核心模块"""
    
    def __init__(self):
        self.github_code = GitHubCodeExtractor()
        self.github_community = GitHubCommunityExtractor()
        self.skill_analyzer = SkillAnalyzer()
        self.context_matcher = ContextMatcher()
        
    async def extract_all(self, intent: IntentResult, user_context: dict) -> ExtractionResult:
        """并行提取所有资源"""
        
        # 并行执行四个提取器
        code_soul, community_exp, skill_cap, context_match = await asyncio.gather(
            self.github_code.extract(intent),
            self.github_community.extract(intent),
            self.skill_analyzer.analyze(intent),
            self.context_matcher.match(intent, user_context)
        )
        
        # 融合结果
        return self.fuse_results(
            code_soul=code_soul,
            community_exp=community_exp,
            skill_cap=skill_cap,
            context_match=context_match
        )
```

##### 2.1 GitHub 代码灵魂提取

```python
class GitHubCodeExtractor:
    """从 GitHub 代码中提取灵魂"""
    
    async def extract(self, intent: IntentResult) -> CodeSoulResult:
        """提取代码层面的知识"""
        
        # 1. 定位相关仓库
        repo = self定位_repo(intent.capability)
        
        # 2. 代码结构分析
        structure = await self.analyze_structure(repo)
        # - 模块划分
        # - 核心类/函数
        # - 数据流
        
        # 3. 设计意图提取（使用 LLM）
        design_intent = await self.llm.extract_design_intent(
            repo=repo,
            prompt="这个项目解决什么问题？架构设计理念是什么？"
        )
        
        # 4. API/能力映射
        api_mapping = self.extract_api_endpoints(repo)
        
        return CodeSoulResult(
            design_intent=design_intent,
            architecture=structure,
            api_endpoints=api_mapping,
            key_components=self.identify_key_components(repo)
        )
```

##### 2.2 GitHub 社区经验提取

```python
class GitHubCommunityExtractor:
    """从 GitHub Issues/Discussions 提取经验"""
    
    async def extract(self, intent: IntentResult) -> CommunityExperienceResult:
        """提取社区经验"""
        
        # 1. 检索相关 Issues
        issues = await self.search_issues(
            keywords=intent.entities,
            repo=intent.target_repo,
            sort="reactions"  # 按有用程度排序
        )
        
        # 2. 提取踩坑记录
        pitfalls = []
        for issue in issues[:20]:
            if self.is_pitfall(issue):
                pitfalls.append(self.extract_pitfall(issue))
                
        # 3. 提取 workaround
        workarounds = self.extract_workarounds(issues)
        
        # 4. 提取最佳实践
        best_practices = self.extract_best_practices(issues)
        
        return CommunityExperienceResult(
            pitfalls=pitfalls,
            workarounds=workarounds,
            best_practices=best_practices,
            related_issues=issues[:10]
        )
```

##### 2.3 Skill 能力提取

```python
class SkillAnalyzer:
    """分析 OpenClaw 现有 Skills"""
    
    async def analyze(self, intent: IntentResult) -> SkillResult:
        """分析现有 Skills"""
        
        # 1. 检索相关 Skills
        related_skills = await self.search_skills(
            keywords=intent.capability,
            threshold=0.7
        )
        
        # 2. 解析 Skill 能力
        capabilities = []
        for skill in related_skills:
            cap = self.parse_skill_capabilities(skill)
            capabilities.append(cap)
            
        # 3. 识别增强机会
        enhancements = self.identify_enhancement_opportunities(
            intent=intent,
            existing_skills=related_skills
        )
        
        return SkillResult(
            skills=related_skills,
            capabilities=capabilities,
            enhancements=enhancements
        )
```

##### 2.4 用户上下文匹配

```python
class ContextMatcher:
    """匹配用户上下文"""
    
    async def match(self, intent: IntentResult, user_context: dict) -> ContextMatchResult:
        """匹配用户上下文"""
        
        # 1. 分析可用模型
        available_models = user_context.get("models", [])
        model_recommendations = self.recommend_models(intent, available_models)
        
        # 2. 读取记忆文件
        memory = user_context.get("memory", {})
        memory_insights = self.extract_insights_from_memory(intent, memory)
        
        # 3. 已安装 Skills
        installed_skills = user_context.get("installed_skills", [])
        skill_suggestions = self.suggest_from_installed(
            intent, installed_skills
        )
        
        # 4. 内置工具
        builtin_tools = user_context.get("tools", [])
        tool_recommendations = self.recommend_tools(intent, builtin_tools)
        
        return ContextMatchResult(
            model_recommendations=model_recommendations,
            memory_insights=memory_insights,
            skill_suggestions=skill_suggestions,
            tool_recommendations=tool_recommendations,
            personalization_score=self.calculate_personalization(
                intent, user_context
            )
        )
```

#### 模块 3：结果融合与排序

```python
class ResultFusion:
    """多源结果融合"""
    
    async def fuse(self, 
                  code_soul: CodeSoulResult,
                  community: CommunityExperienceResult,
                  skills: SkillResult,
                  context: ContextMatchResult) -> FusionResult:
        """融合所有结果"""
        
        # 1. 计算综合相关度
        combined_scores = self.calculate_combined_scores(
            code=code_soul.relevance,
            community=community.relevance,
            skills=skills.relevance,
            context=context.relevance
        )
        
        # 2. 个性化调整
        personalized = self.apply_personalization(
            scores=combined_scores,
            context=context
        )
        
        # 3. 去重与合并
        deduplicated = self.deduplicate(personalized)
        
        # 4. 分组呈现
        grouped = self.group_for_presentation(deduplicated)
        
        return FusionResult(
            main_recommendations=grouped.main,
            complementary=grouped.complementary,
            enhancements=grouped.enhancements,
            context_insights=context.summary
        )
```

---

## 四、用户交互设计（重要！）

### 4.1 交互原则

**即使内部处理复杂，对用户必须简洁友好**

| 原则 | 实现 |
|------|------|
| **少说多做** | 多个子代理并行工作，用户只需要等一轮 |
| **透明可见** | 每个阶段展示进度，用户知道在做什么 |
| **个性化** | 基于用户上下文推荐，用户觉得"懂我" |
| **可退出** | 用户可以随时说"直接给我看" |

### 4.2 交互流程示例

```
用户: Dora 我想管 Trello

─────────────────────────────────────────────────────────
🎯 正在分析你的需求...（并行处理中）
   
   ✓ 理解需求：任务管理 + Trello
   ✓ 检索代码：找到 3 个相关项目
   ✓ 挖掘社区：找到 15 个踩坑记录
   ✓ 分析 Skills：发现已安装 Trello Skill
   ✓ 匹配上下文：检测到你有 Claude 模型

─────────────────────────────────────────────────────────
🎉 找到以下能力积木

【推荐】Trello 能力（基于你的上下文）

核心能力：
✅ 查看所有 Board         ← 推荐：匹配你的记忆
✅ 创建新 Card
✅ 移动 Card
✅ 留评论

增强能力（配置后解锁）：
⚡ Webhook 通知      ← 你有 ngrok，可能用得上
⚡ 自动化规则         ← 需要付费 Power-Up

【你可能还感兴趣】
• CalDAV 日历同步    ← 检测到你在用日历
• GitHub Issues       ← 检测到你是开发者

─────────────────────────────────────────────────────────
```

---

## 五、技术实现路线

### 5.1 短期（v1.0）

- [ ] 实现意图识别模块
- [ ] 实现 GitHub Issues 检索
- [ ] 实现 Skill 解析
- [ ] 实现基础的上下文读取
- [ ] 实现单轮交互呈现

### 5.2 中期（v1.1）

- [ ] 实现代码灵魂提取（LLM 分析）
- [ ] 实现多源结果融合
- [ ] 实现个性化推荐
- [ ] 实现进度透明化

### 5.3 长期（v2.0）

- [ ] 实现完整知识图谱
- [ ] 实现实时社区挖掘
- [ ] 实现跨项目推理
- [ ] 实现自学习优化

---

## 六、总结

### 6.1 核心理念

| 维度 | 内容 |
|------|------|
| **资源来源** | GitHub + OpenClaw Skills + 用户上下文 |
| **提取深度** | 代码灵魂 + 社区经验 + 资源推荐 |
| **用户体验** | 少交互、高个性化、可视化进度 |
| **技术实现** | 多源并行检索 + LLM 分析 + 智能融合 |

### 6.2 关键创新

1. **灵魂提取体系化**：不只是检索，是理解 + 洞察 + 推荐
2. **上下文深度整合**：用户的记忆、模型、工具都是资源
3. **交互简化**：内部复杂，外部简洁

---

*本方案基于 2026-03-11 所有研究文档综合设计*
