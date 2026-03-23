# Doramagic 自适应交互深度 - 技术架构方案

**日期：** 2026-03-11  
**版本：** v1.0  
**状态：** 技术方案研究报告

---

## 1. 执行摘要

本报告针对 Doramagic「自适应交互深度」功能提供完整的技术架构方案。该功能的核心目标是：根据用户表达的清晰度动态调整信息获取轮数，在用户需求不明确时主动追问，在需求清晰时直接执行。

**核心技术挑战：**
- 意图识别：从自然语言中提取「能力」和「场景」
- 置信度评分：量化评估「用户需求是否清晰」
- 选择题生成：生成覆盖用户意图的选项
- 对话状态管理：维护多轮对话上下文
- 提前终止：判断何时停止追问

---

## 2. 系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Input (Natural Language)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Clarification Engine                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Intent       │  │ Confidence   │  │ Question     │          │
│  │ Detection    │─▶│ Scoring      │─▶│ Generator    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                      │
│                  ┌──────────────┐                               │
│                  │ Dialogue     │                               │
│                  │ State Manager│                               │
│                  └──────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│   Proceed to Execute    │       │   Generate Clarification│
│   (High Confidence)     │       │   Questions (Low Conf.) │
└─────────────────────────┘       └─────────────────────────┘
```

---

## 3. 意图识别

### 3.1 问题定义

意图识别的目标是：从用户的自然语言输入中识别出：
1. **能力（Capability）**：用户想要什么功能/服务
2. **场景（Scenario）**：用户使用该能力的具体上下文

### 3.2 技术方案对比

| 方案 | 优点 | 缺点 | 适用场景 | 推荐度 |
|------|------|------|----------|--------|
| **Embedding + Vector DB** | 部署简单、无需训练 | 依赖向量质量、难以处理复杂意图 | 意图集合固定、量级中等 | ⭐⭐⭐ |
| **Fine-tuned LLM** | 精度高、可处理复杂意图 | 需要标注数据、训练成本高 | 意图种类多、要求高精度 | ⭐⭐⭐⭐ |
| **Prompt Engineering (LLM)** | 零样本、无需训练、可扩展 | 依赖模型能力、延迟较高 | 快速迭代、意图易变 | ⭐⭐⭐⭐⭐ |

### 3.3 推荐方案：Prompt Engineering + Structured Output

**理由：**
1. Doramagic 已有 LLM 调用能力（Gemini/Ollama），复用成本低
2. 意图种类可能随功能迭代变化，Prompt 方案更灵活
3. 可利用 LLM 的推理能力处理模糊表述

**Prompt 设计：**

```python
INTENT_DETECTION_PROMPT = """你是一个意图识别专家。请分析用户的输入，提取以下信息：

## 可识别的能力类型（从以下选择，可多选）：
- soul_extraction：灵魂提取，从代码库提取设计理念
- code_generation：代码生成，根据需求生成代码
- code_review：代码审查，审查现有代码
- documentation：文档生成，生成项目文档
- dependency_analysis：依赖分析，分析项目依赖

## 可识别的场景类型（从以下选择）：
- new_project：新项目启动
- debugging：问题排查
- refactoring：代码重构
- learning：学习理解
- optimization：性能优化
- migration：技术迁移

## 输出要求：
请以JSON格式输出，字段如下：
{
    "capabilities": ["能力1", "能力2"],  // 识别出的能力列表
    "scenario": "场景类型",               // 识别出的场景
    "raw_requirement": "用户原始表达",   // 保留原始输入
    "key_entities": ["实体1", "实体2"],  // 提取的关键实体
    "ambiguity_level": "high/medium/low" // 表达的清晰程度
}

## 分析规则：
1. 如果用户只说了解决方案（如"我要一个提醒功能"），需要追问场景
2. 如果用户只说了目标（如"我想学编程"），需要追问具体方向
3. 优先考虑用户的真实痛点，而非字面意思

用户输入：{user_input}
"""
```

### 3.4 多语言处理

```python
MULTILINGUAL_PROMPT = """检测用户输入的语言，并将其翻译为标准中文后进行意图分析。

规则：
- 如果输入是中文：直接分析
- 如果输入是英文：翻译为中文后分析，保留原文在 raw_input 中
- 如果输入是其他语言：先翻译为中文

输出格式增加：
{
    "detected_language": "zh/en/other",
    "translated_input": "翻译后的中文"  // 如果有翻译
}
"""
```

---

## 4. 置信度评分

### 4.1 评分指标体系

置信度评分采用多维度加权评估：

```python
class ConfidenceScorer:
    def __init__(self):
        self.weights = {
            'entity_completeness': 0.35,    # 实体完整度
            'intent_match_score': 0.25,     # 意图匹配度
            'ambiguity_detection': 0.20,   # 模糊词检测
            'context_coherence': 0.20      # 上下文连贯性
        }
    
    def score(self, intent_result: dict, context: dict) -> float:
        """
        计算综合置信度，返回 0.0 - 1.0 的分数
        """
```

#### 4.1.1 实体完整度 (Entity Completeness)

**定义：** 用户输入中是否包含完成任务所需的关键实体

**实体类型：**
- **能力相关实体**：如代码语言、框架类型、目标平台
- **场景相关实体**：如项目规模、团队情况、时间约束
- **约束条件**：如预算、优先级、性能要求

**计算公式：**
```
entity_score = filled_entities / required_entities
```

#### 4.1.2 意图匹配度 (Intent Match Score)

**定义：** LLM 对意图判断的确定性程度

**来源：**
- LLM 输出时的概率分布（如果可用）
- 或通过追问确认："你确定是X吗？"

**计算方式：**
```python
# 通过多次采样计算一致性
def calculate_intent_consistency(user_input: str, llm) -> float:
    results = []
    for _ in range(3):
        result = llm.extract_intent(user_input)
        results.append(result['primary_intent'])
    
    # 计算多数一致性
    majority = max(set(results), key=results.count)
    consistency = results.count(majority) / len(results)
    return consistency
```

#### 4.1.3 模糊词检测 (Ambiguity Detection)

**定义：** 检测用户输入中的模糊表述

**模糊词清单：**
```python
AMBIGUOUS_WORDS = {
    'high': ['随便', '都行', '都可以', '无所谓', '一般', '还行', '还好'],
    'medium': ['好一点', '更好', '优化一下', '改进', '完善', '提升'],
    'specific': ['具体', '明确', '详细']  # 用户明确要求详细时
}

# 模糊词权重
AMBIGUITY_WEIGHTS = {
    'high': 0.0,      # 包含高模糊词，置信度直接降低
    'medium': 0.3,   # 中等模糊词，按比例降低
    'low': 0.7       # 低模糊词，基本不影响
}
```

#### 4.1.4 上下文连贯性 (Context Coherence)

**定义：** 当前输入与历史对话的连贯程度

**检测方法：**
```python
def calculate_coherence(current_input: str, history: list) -> float:
    if not history:
        return 0.5  # 无历史记录，中等置信
    
    # 使用简单重叠检测
    current_tokens = set(tokenize(current_input))
    history_tokens = set()
    for h in history[-3:]:  # 最近3轮
        history_tokens.update(tokenize(h['user_input']))
    
    overlap = len(current_tokens & history_tokens)
    union = len(current_tokens | history_tokens)
    
    return overlap / union if union > 0 else 0.5
```

### 4.2 阈值设定依据

| 置信度区间 | 行为 | 阈值依据 |
|------------|------|----------|
| **≥ 0.70** | 直接执行 | 行业标准（Dialogflow 0.6-0.8, LivePerson 0.6） |
| **0.40 - 0.69** | 生成选择题追问 | 需要澄清但不紧急 |
| **< 0.40** | 深度追问 + 场景还原 | 需要大量补充信息 |

**70% 阈值的依据：**
1. **行业实践**：Dialogflow、LivePerson、Amazon Lex 等主流平台均采用 60-70% 作为默认值
2. **平衡体验**：过高导致频繁追问影响体验，过低导致误解用户意图
3. **可调参数**：建议设计为可配置项，根据实际准确率调整

**阈值调优策略：**
```python
# A/B 测试不同阈值
THRESHOLD_CONFIGS = {
    'conservative': 0.80,   # 减少误执行，适合关键任务
    'balanced': 0.70,       # 平衡体验与效率
    'aggressive': 0.60      # 减少追问，适合简单任务
}
```

---

## 5. 选择题生成

### 5.1 选项来源

| 来源 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **知识库** | 准确、可控 | 需要维护、更新成本 | 成熟功能、常见场景 |
| **LLM 生成** | 灵活、可扩展 | 质量不稳定 | 新功能、探索阶段 |
| **预设模板** | 快速、可控 | 覆盖度有限 | 核心场景、高频需求 |

### 5.2 推荐策略：混合模式

```python
class QuestionGenerator:
    def __init__(self, knowledge_base, llm):
        self.knowledge_base = knowledge_base
        self.llm = llm
    
    def generate_options(self, intent: dict, missing_info: list) -> list:
        """
        生成澄清问题的选项
        
        missing_info: 缺失的信息列表，如 ['language', 'framework', 'platform']
        """
        options = []
        
        for info_type in missing_info:
            # 1. 先从知识库获取常见选项
            kb_options = self.knowledge_base.get_common_options(info_type)
            
            # 2. 补充 LLM 生成的个性化选项
            if len(kb_options) < 3:
                llm_options = self.llm.generate_options(info_type, intent)
                options.extend(kb_options + llm_options)
            else:
                options.extend(kb_options)
        
        return self.deduplicate_and_rank(options)
```

### 5.3 选项覆盖策略

**原则：**
1. **互斥性**：选项之间不重叠
2. **完整性**：覆盖用户可能的意图
3. **可操作性**：选项应该是用户可以明确选择的

```python
# 选项生成模板
OPTION_TEMPLATES = {
    'language': {
        'question': '你主要使用什么编程语言？',
        'options': ['Python', 'JavaScript', 'TypeScript', 'Go', 'Java', 'Rust', '其他'],
        'source': 'knowledge_base'
    },
    'framework': {
        'question': '你使用的是哪个框架？',
        'source': 'llm_generated',  # 根据 language 动态生成
    },
    'scenario': {
        'question': '你遇到的是什么场景？',
        'options': [
            {'text': '新项目启动，需要从零开始', 'tag': 'new_project'},
            {'text': '现有项目遇到问题需要排查', 'tag': 'debugging'},
            {'text': '代码需要重构或优化', 'tag': 'refactoring'},
            {'text': '学习理解现有代码库', 'tag': 'learning'}
        ],
        'source': 'template'
    }
}
```

### 5.4 选项质量保证

```python
def validate_options(options: list, user_intent: dict) -> bool:
    """验证选项是否覆盖用户意图"""
    
    # 1. 覆盖率检查
    coverage = calculate_intent_coverage(options, user_intent)
    if coverage < 0.7:
        return False
    
    # 2. 区分度检查
    if not has_discriminability(options):
        return False
    
    # 3. 可理解性检查
    if not all_understandable(options):
        return False
    
    return True
```

---

## 6. 对话状态管理

### 6.1 状态数据结构

```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class DialogueState:
    """对话状态"""
    
    # 会话标识
    session_id: str
    user_id: str
    
    # 当前轮次信息
    turn: int = 0
    max_turns: int = 5  # 最大追问轮数
    
    # 意图与实体
    current_intent: Optional[dict] = None
    collected_entities: dict = field(default_factory=dict)
    missing_entities: list = field(default_factory=list)
    
    # 置信度历史
    confidence_history: list = field(default_factory=list)
    
    # 历史记录
    conversation_history: list = field(default_factory=list)
    
    # 状态标志
    status: str = 'initial'  # initial, clarifying, executing, completed, failed
    last_question: Optional[str] = None
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 上下文继承
    parent_session_id: Optional[str] = None  # 用于跨会话继承
```

### 6.2 状态存储方案

```python
# 推荐使用 Redis 进行状态存储
class DialogueStateStore:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 状态有效期 1 小时
    
    def save(self, state: DialogueState):
        key = f"dialogue:{state.session_id}"
        self.redis.setex(
            key,
            self.ttl,
            json.dumps(asdict(state))
        )
    
    def load(self, session_id: str) -> Optional[DialogueState]:
        key = f"dialogue:{session_id}"
        data = self.redis.get(key)
        if data:
            return DialogueState(**json.loads(data))
        return None
    
    def update(self, session_id: str, updates: dict):
        state = self.load(session_id)
        if state:
            for k, v in updates.items():
                setattr(state, k, v)
            state.updated_at = datetime.now()
            self.save(state)
```

### 6.3 上下文继承

```python
class ContextInheritance:
    """上下文继承机制"""
    
    def inherit_from_history(self, user_id: str, current_intent: dict) -> dict:
        """
        从历史对话中继承相关上下文
        """
        # 获取用户最近的对话历史
        recent_sessions = self.get_recent_sessions(user_id, limit=5)
        
        inherited = {
            'preferred_language': None,
            'recent_projects': [],
            'common_scenarios': [],
            'known_constraints': {}
        }
        
        for session in recent_sessions:
            if session.status == 'completed':
                # 继承已完成任务的偏好
                if session.current_intent:
                    inherited['preferred_language'] = session.current_intent.get('language')
                    inherited['recent_projects'].extend(
                        session.collected_entities.get('projects', [])
                    )
        
        return inherited
    
    def merge_context(self, current: dict, inherited: dict) -> dict:
        """合并当前输入与继承的上下文"""
        merged = current.copy()
        
        # 用历史偏好填充缺失字段
        for key, value in inherited.items():
            if key not in merged and value:
                merged[key] = value
                merged[f'{key}_source'] = 'inherited'
        
        return merged
```

### 6.4 状态机流转

```
┌─────────────┐
│   initial   │ ◀── 用户新输入
└──────┬──────┘
       │ intent detected
       ▼
┌─────────────┐     confidence >= 0.7     ┌─────────────┐
│  clarifying │ ─────────────────────────▶│  executing │
└──────┬──────┘                            └──────┬──────┘
       │                                            │
       │ confidence < 0.7                          │ completed
       │ max_turns reached                          ▼
       │ user confirms                  ┌─────────────┐
       ▼                                  │  completed  │
┌─────────────┐                          └─────────────┘
│  failed/    │
│  timeout    │
└─────────────┘
```

---

## 7. 提前终止策略

### 7.1 终止条件

```python
class TerminationChecker:
    """提前终止检查器"""
    
    def should_terminate(self, state: DialogueState) -> tuple[bool, str]:
        """
        检查是否应该终止追问
        
        返回: (should_terminate, reason)
        """
        
        # 条件1：最大轮次达到
        if state.turn >= state.max_turns:
            return True, "max_turns_reached"
        
        # 条件2：置信度达标
        current_confidence = state.confidence_history[-1] if state.confidence_history else 0
        if current_confidence >= 0.70:
            return True, "confidence_threshold_met"
        
        # 条件3：用户明确确认
        if self.user_confirmed(state):
            return True, "user_confirmed"
        
        # 条件4：实体已完整
        if not state.missing_entities:
            return True, "entities_complete"
        
        # 条件5：用户明确拒绝回答
        if self.user_refused(state):
            return True, "user_refused"
        
        return False, "continue"
    
    def user_confirmed(self, state: DialogueState) -> bool:
        """检测用户是否确认"""
        last_input = state.conversation_history[-1]['user'] if state.conversation_history else ""
        confirmation_patterns = ['是的', '对的', '正确', 'ok', 'yes', 'confirm']
        return any(p in last_input.lower() for p in confirmation_patterns)
    
    def user_refused(self, state: DialogueState) -> bool:
        """检测用户是否拒绝回答"""
        last_input = state.conversation_history[-1]['user'] if state.conversation_history else ""
        refusal_patterns = ['不知道', '随便', '都行', '不想说', '不用了']
        return any(p in last_input for p in refusal_patterns)
```

### 7.2 保守方案兜底

当无法继续追问或用户失去耐心时，使用保守方案：

```python
class ConservativeFallback:
    """保守方案兜底策略"""
    
    def generate_fallback(self, state: DialogueState) -> dict:
        """
        生成保守的兜底方案
        """
        
        # 1. 基于已有信息生成最可能的假设
        likely_intent = self.predict_likely_intent(state)
        
        # 2. 生成确认请求
        confirmation_message = self.generate_confirmation(likely_intent)
        
        return {
            'type': 'confirmation_request',
            'message': confirmation_message,
            'suggested_intent': likely_intent,
            'options': [
                '是的，继续',
                '不是，我想做别的',
                '让我重新描述一下'
            ]
        }
    
    def predict_likely_intent(self, state: DialogueState) -> dict:
        """基于已有信息预测最可能的意图"""
        
        # 使用最大置信度的历史意图
        if state.confidence_history:
            best_idx = state.confidence_history.index(max(state.confidence_history))
            return state.conversation_history[best_idx].get('intent', {})
        
        # 或者使用收集到的实体反推
        return self.infer_from_entities(state.collected_entities)
    
    def generate_confirmation(self, intent: dict) -> str:
        """生成确认信息"""
        
        capability = intent.get('capability', '这个')
        scenario = intent.get('scenario', '')
        
        if scenario:
            return f"我理解你想用{capability}能力来解决{scenario}场景的问题，是吗？"
        else:
            return f"我理解你想{capability}，对吗？"
```

### 7.3 提前终止触发场景

| 场景 | 触发条件 | 兜底行为 |
|------|----------|----------|
| **最大轮次** | `turn >= max_turns` | 生成最可能假设，请求确认 |
| **高置信度** | `confidence >= 0.7` | 直接执行，不追问 |
| **用户确认** | 用户说"是的/对" | 进入执行流程 |
| **用户拒绝** | 用户说"随便/不知道" | 提供默认方案或转人工 |
| **超时** | 无响应超过X分钟 | 保存状态，可恢复 |

---

## 8. 技术选型建议

### 8.1 推荐技术栈

| 层级 | 推荐方案 | 备选方案 | 理由 |
|------|----------|----------|------|
| **LLM 引擎** | Gemini 2.0 / GPT-4 | Ollama (本地) | 意图理解能力强，支持结构化输出 |
| **状态存储** | Redis | SQLite | 高性能、支持过期、可分布式 |
| **向量存储** | Qdrant | Milvus | 轻量、易部署、支持混合搜索 |
| **Prompt 管理** | 自研 / PromptHub | - | 版本控制、AB 测试 |
| **监控** | Langfuse | 自建 | 意图识别可观测性 |

### 8.2 开源 vs 自研权衡

| 组件 | 推荐 | 理由 |
|------|------|------|
| **意图识别** | 自研 (Prompt Engineering) | 利用现有 LLM，灵活度高 |
| **对话管理** | 自研 + Rasa 参考 | 状态管理逻辑不复杂 |
| **置信度评分** | 自研 | 业务相关，需定制 |
| **知识库** | 开源 (Qdrant + 自建) | 需要长期维护 |

### 8.3 性能与成本

```python
# 成本估算（基于 LLM 调用）

# 方案A: 每次交互 2 次 LLM 调用
# - Intent Detection: ~1000 tokens
# - Question Generation: ~500 tokens
# 单次成本: ~$0.002 (GPT-4) / ~$0.0001 (Gemini Pro)

# 优化策略:
OPTIMIZATIONS = {
    'caching': {
        'description': '缓存常见意图的识别结果',
        'impact': '减少 30-50% LLM 调用'
    },
    'streaming': {
        'description': '流式输出减少感知延迟',
        'impact': '提升用户体验'
    },
    'fallback_chain': {
        'description': '先用小模型尝试，失败再换大模型',
        'impact': '成本降低 60%'
    }
}
```

### 8.4 架构部署

```
┌──────────────────────────────────────────────────────────────┐
│                        API Gateway                             │
│                    (Rate Limit, Auth)                         │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                   Clarification Service                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Intent      │  │ Confidence  │  │ State       │           │
│  │ Detector    │  │ Scorer      │  │ Manager     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────┬────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐     ┌──────────┐
   │ Gemini   │    │ Qdrant  │     │  Redis   │
   │ API      │    │ (Cache) │     │ (State)  │
   └──────────┘    └──────────┘     └──────────┘
```

---

## 9. 实现路线图

### Phase 1: 基础能力 (1-2周)

- [ ] 实现基础的意图识别 Prompt
- [ ] 实现置信度评分算法（简化版）
- [ ] 使用内存存储实现对话状态
- [ ] 硬编码的选择题模板

### Phase 2: 增强功能 (2-3周)

- [ ] 完善置信度评分多维度计算
- [ ] 实现 Redis 状态存储
- [ ] 接入知识库生成选项
- [ ] 实现提前终止策略

### Phase 3: 优化迭代 (持续)

- [ ] 引入 LLM 生成选项
- [ ] 实现上下文继承
- [ ] 添加监控与可观测性
- [ ] A/B 测试阈值调优

---

## 10. 总结

本技术方案为 Doramagic 的「自适应交互深度」功能提供了完整的实现蓝图：

1. **意图识别**：采用 Prompt Engineering + LLM 结构化输出，复用现有 LLM 能力
2. **置信度评分**：四维度加权评估（实体完整度、意图匹配度、模糊词检测、上下文连贯性），70% 阈值基于行业标准
3. **选择题生成**：知识库 + LLM 混合模式，确保选项覆盖用户意图
4. **对话状态管理**：基于 Redis 的分布式状态存储，支持上下文继承
5. **提前终止**：多条件触发 + 保守方案兜底，确保用户体验

**核心理念**：通过「适度追问」在「信息不足」和「用户烦躁」之间取得平衡，让 Doramagic 能够理解模糊表达，同时不过度打扰用户。

---

*本报告由 G大脑袋 撰写*
