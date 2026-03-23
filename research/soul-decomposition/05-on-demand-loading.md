# 按需加载机制研究报告

研究日期: 2026-03-10 | 模型: GLM-5

---

## 一、触发机制设计

### 1.1 触发器类型

按需加载机制的核心在于精准识别何时需要加载特定模块灵魂。以下是主要触发器类型：

#### 关键词触发
```yaml
# 触发器配置示例
triggers:
  - type: keyword
    patterns:
      - "git commit" → commit-message-soul.md
      - "refactor" → architecture-soul.md
      - "debug" → debugging-soul.md
    match_mode: fuzzy  # 精确匹配 | 模糊匹配 | 语义匹配
    priority: 0.8
```

**实现要点：**
- 支持多语言关键词（中英双语）
- 正则表达式支持复杂模式
- 语义扩展（"修bug" ≈ "debug" ≈ "fix"）

#### 文件路径触发
```yaml
triggers:
  - type: file_path
    patterns:
      - "src/api/**" → api-design-soul.md
      - "**/*.test.ts" → testing-soul.md
      - "docs/**/*.md" → documentation-soul.md
    glob_support: true
```

**路径匹配策略：**
- Glob 模式支持通配符
- 文件扩展名快速匹配
- 目录层级权重（越深越具体）

#### API 调用触发
```yaml
triggers:
  - type: api_call
    patterns:
      - "POST /api/users" → user-management-soul.md
      - "GET /api/analytics" → analytics-soul.md
    method_aware: true
```

**API 感知：**
- HTTP 方法区分（GET vs POST 不同处理）
- 路径参数解析（/users/:id）
- 请求体字段检测

#### 错误栈触发
```yaml
triggers:
  - type: error_stack
    patterns:
      - "TypeError: Cannot read" → debugging-soul.md
      - "ECONNREFUSED" → network-debug-soul.md
      - "SyntaxError" → syntax-fix-soul.md
    stack_depth: 5  # 分析前5层调用栈
```

**错误分析：**
- 错误类型分类
- 源文件定位
- 相关模块联想

### 1.2 多触发器组合

```yaml
combination_rules:
  - name: "API开发场景"
    triggers: [file_path, api_call]
    logic: AND
    soul: api-development-soul.md
    boost: 1.5  # 组合触发优先级提升
    
  - name: "调试场景"
    triggers: [error_stack, keyword]
    logic: OR
    soul: debugging-soul.md
```

### 1.3 触发时机

| 时机 | 描述 | 性能影响 |
|------|------|----------|
| **会话启动** | 预加载高频模块 | 低 |
| **用户输入** | 实时分析关键词 | 中 |
| **工具调用前** | 检查工具相关模块 | 低 |
| **错误发生后** | 错误栈分析 | 高 |
| **上下文切换** | 模块卸载/重载 | 中 |

---

## 二、加载策略

### 2.1 懒加载（Lazy Loading）

**核心思想：** 只在真正需要时才加载模块灵魂。

```python
class LazySoulLoader:
    def __init__(self, soul_registry):
        self.registry = soul_registry
        self.loaded_cache = {}
        
    def get_soul(self, soul_id):
        if soul_id not in self.loaded_cache:
            soul = self.registry.load(soul_id)
            self.loaded_cache[soul_id] = soul
        return self.loaded_cache[soul_id]
    
    def preload_descriptions(self):
        """预加载所有灵魂描述（轻量级）"""
        return self.registry.get_all_descriptions()
```

**懒加载触发流程：**
```
用户输入 → 关键词分析 → 匹配灵魂描述 → 决策加载 → 加载完整灵魂
```

**优点：**
- 最小化内存占用
- 减少启动时间
- 按需扩展

**缺点：**
- 首次加载延迟
- 需要预热机制

### 2.2 预加载（Preloading）

**策略：** 基于历史数据预测即将需要的模块。

```python
class PreloadStrategy:
    def __init__(self):
        self.usage_history = UsageHistory()
        self.preload_threshold = 0.7
        
    def predict_next_souls(self, current_context):
        """基于上下文预测下一个需要的灵魂"""
        patterns = self.usage_history.find_patterns(current_context)
        predictions = []
        for pattern in patterns:
            if pattern.probability > self.preload_threshold:
                predictions.append(pattern.soul_id)
        return predictions
    
    def background_preload(self, predictions):
        """后台异步预加载"""
        for soul_id in predictions:
            asyncio.create_task(self.load_soul_async(soul_id))
```

**预加载决策矩阵：**

| 场景 | 预加载条件 | 预加载内容 |
|------|------------|------------|
| 新建文件 | 检测到编辑器打开新文件 | 语言相关灵魂 |
| 进入目录 | cd 到特定目录 | 项目相关灵魂 |
| 工具调用前 | 工具名称匹配 | 工具使用灵魂 |
| 错误发生 | 特定错误类型 | 调试灵魂 |
| 时间模式 | 每日固定任务 | 定时任务灵魂 |

### 2.3 缓存策略

#### LRU 缓存（最近最少使用）
```python
from functools import lru_cache

@lru_cache(maxsize=50)
def load_soul_cached(soul_id):
    return load_soul_from_disk(soul_id)
```

#### 分层缓存
```
┌─────────────────────────────────────────────┐
│ L1: 内存缓存 (热数据，最近使用)               │
│   - 大小限制：10个灵魂                        │
│   - 命中率目标：80%                           │
├─────────────────────────────────────────────┤
│ L2: 压缩缓存 (温数据，近期使用)               │
│   - 大小限制：100个灵魂（压缩存储）            │
│   - 压缩率：50-70%                            │
├─────────────────────────────────────────────┤
│ L3: 索引缓存 (元数据，快速检索)              │
│   - 所有灵魂的描述+关键词索引                 │
│   - 常驻内存                                  │
└─────────────────────────────────────────────┘
```

#### 缓存失效策略
```python
class SoulCache:
    def invalidate(self, soul_id, reason):
        """缓存失效处理"""
        if reason == "content_changed":
            # 内容变更，强制更新
            self.reload(soul_id)
        elif reason == "ttl_expired":
            # TTL 过期，后台刷新
            asyncio.create_task(self.refresh_async(soul_id))
        elif reason == "memory_pressure":
            # 内存压力，降级到压缩缓存
            self.demote_to_l2(soul_id)
```

---

## 三、上下文组装

### 3.1 多模块组合策略

#### 优先级叠加
```yaml
assembly_strategy:
  - name: priority_merge
    description: 按优先级合并多个灵魂
    
    steps:
      - sort_by_relevance: true
      - resolve_conflicts: "highest_priority"
      - deduplicate_rules: true
      - limit_total_tokens: 8000
```

#### 角色分工组装
```yaml
assembly_strategy:
  - name: role_assembly
    description: 根据任务角色组装灵魂
    
    roles:
      architect:
        souls: [architecture-soul, design-patterns-soul]
        weight: 1.0
        
      implementer:
        souls: [coding-standards-soul, testing-soul]
        weight: 0.8
        
      reviewer:
        souls: [code-review-soul, security-soul]
        weight: 0.6
```

### 3.2 上下文模板

```
## 已加载的灵魂模块

### 核心灵魂（主动加载）
- **{soul_name}**: {soul_summary}
  - 关联原因: {trigger_reason}
  - 加载时机: {load_time}

### 辅助灵魂（自动联想）
- **{soul_name}**: {soul_summary}
  - 关联原因: {association_reason}

---

## 模块特定指导

{merged_instructions}

---

## 共识冲突处理

{conflict_resolutions}
```

### 3.3 冲突解决机制

```python
class ConflictResolver:
    def resolve(self, soul_a, soul_b, conflict_type):
        strategies = {
            "rule_conflict": self.resolve_rule_conflict,
            "priority_conflict": self.resolve_priority_conflict,
            "context_conflict": self.resolve_context_conflict,
        }
        return strategies[conflict_type](soul_a, soul_b)
    
    def resolve_rule_conflict(self, rule_a, rule_b):
        """规则冲突解决"""
        # 策略1：更具体的规则优先
        if rule_a.specificity > rule_b.specificity:
            return rule_a
        
        # 策略2：更新时间优先
        if rule_a.updated_at > rule_b.updated_at:
            return rule_a
        
        # 策略3：显式声明优先级
        return max(rule_a, rule_b, key=lambda r: r.priority)
```

---

## 四、性能优化

### 4.1 索引设计

#### 倒排索引
```python
class SoulInvertedIndex:
    """
    关键词 → 灵魂ID 的倒排索引
    支持快速全文搜索
    """
    def __init__(self):
        self.index = {}  # {keyword: [soul_ids]}
        
    def search(self, query):
        """搜索相关灵魂"""
        keywords = self.tokenize(query)
        soul_scores = defaultdict(float)
        
        for keyword in keywords:
            for soul_id in self.index.get(keyword, []):
                soul_scores[soul_id] += self.idf(keyword)
        
        return sorted(soul_scores.items(), key=lambda x: x[1], reverse=True)
```

#### 向量索引
```python
class SoulVectorIndex:
    """
    灵魂嵌入向量索引
    支持语义相似度搜索
    """
    def __init__(self, embedding_model):
        self.embeddings = {}
        self.model = embedding_model
        
    def semantic_search(self, query, top_k=5):
        """语义搜索"""
        query_vec = self.model.embed(query)
        
        similarities = {}
        for soul_id, soul_vec in self.embeddings.items():
            similarities[soul_id] = cosine_similarity(query_vec, soul_vec)
        
        return sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

#### 复合索引结构
```
┌────────────────────────────────────────────────────┐
│                    索引层                           │
├────────────────────────────────────────────────────┤
│ 关键词索引 (BM25)     │ 快速文本匹配              │
│ 向量索引 (FAISS)      │ 语义相似度搜索            │
│ 路径索引 (Glob)       │ 文件路径模式匹配          │
│ 元数据索引            │ 标签、优先级等属性过滤     │
└────────────────────────────────────────────────────┘
```

### 4.2 压缩策略

#### 语义压缩
```python
class SemanticCompressor:
    """将灵魂内容压缩为更紧凑的形式"""
    
    def compress(self, soul_content, target_ratio=0.5):
        """
        语义压缩：
        1. 提取核心规则
        2. 合并相似条目
        3. 移除冗余描述
        """
        # 提取关键句
        key_sentences = self.extract_key_sentences(soul_content)
        
        # 合并相似规则
        merged = self.merge_similar_rules(key_sentences)
        
        # 精简表达
        compressed = self.compact_expression(merged)
        
        return compressed
```

#### 分层压缩
```
原始灵魂 (100%)
    │
    ├── 描述层 (10%) - 永久保留
    │     └── 灵魂名称、简介、适用场景
    │
    ├── 索引层 (20%) - 常驻内存
    │     └── 关键词、触发条件、优先级
    │
    └── 内容层 (70%) - 按需加载
          ├── 核心规则 - 必要时加载
          └── 详细示例 - 仅在明确需要时
```

### 4.3 增量加载

```python
class IncrementalLoader:
    """增量加载：先加载骨架，后加载细节"""
    
    def load_skeleton(self, soul_id):
        """加载灵魂骨架（< 100 tokens）"""
        return {
            "id": soul_id,
            "name": self.get_name(soul_id),
            "summary": self.get_summary(soul_id),
            "keywords": self.get_keywords(soul_id),
            "priority": self.get_priority(soul_id),
        }
    
    def load_core_rules(self, soul_id):
        """加载核心规则（200-500 tokens）"""
        skeleton = self.load_skeleton(soul_id)
        skeleton["core_rules"] = self.get_core_rules(soul_id)
        return skeleton
    
    def load_full(self, soul_id):
        """加载完整内容（500-2000 tokens）"""
        core = self.load_core_rules(soul_id)
        core["examples"] = self.get_examples(soul_id)
        core["edge_cases"] = self.get_edge_cases(soul_id)
        return core
```

---

## 五、优先级排序算法

### 5.1 相关性计算

```python
class RelevanceCalculator:
    def calculate(self, query, soul_metadata):
        """计算灵魂与当前上下文的相关性"""
        
        scores = {
            "keyword_match": self.keyword_score(query, soul_metadata),
            "semantic_similarity": self.semantic_score(query, soul_metadata),
            "recency": self.recency_score(soul_metadata),
            "frequency": self.frequency_score(soul_metadata),
            "context_fit": self.context_fit_score(query, soul_metadata),
        }
        
        # 加权综合评分
        weights = {
            "keyword_match": 0.3,
            "semantic_similarity": 0.25,
            "recency": 0.15,
            "frequency": 0.15,
            "context_fit": 0.15,
        }
        
        return sum(scores[k] * weights[k] for k in scores)
```

### 5.2 排序策略

#### 多维度排序
```python
def sort_souls(souls, context):
    """多维度排序"""
    
    # 第一轮：相关性过滤
    relevant = [s for s in souls if s.relevance > THRESHOLD]
    
    # 第二轮：优先级排序
    sorted_by_priority = sorted(relevant, key=lambda s: (
        -s.priority,           # 高优先级优先
        -s.relevance,          # 高相关性优先
        -s.last_used,          # 最近使用优先
        s.token_count,         # 小体积优先
    ))
    
    # 第三轮：多样性保证
    final = diversity_aware_selection(sorted_by_priority)
    
    return final
```

#### 多样性保证
```python
def diversity_aware_selection(sorted_souls, max_per_category=3):
    """确保不同类别的灵魂都被代表"""
    
    categories = defaultdict(list)
    
    for soul in sorted_souls:
        category = soul.category
        if len(categories[category]) < max_per_category:
            categories[category].append(soul)
    
    # 交错合并各类别
    result = []
    max_len = max(len(v) for v in categories.values())
    
    for i in range(max_len):
        for category in categories:
            if i < len(categories[category]):
                result.append(categories[category][i])
    
    return result
```

### 5.3 动态优先级调整

```python
class DynamicPriority:
    """基于使用反馈动态调整优先级"""
    
    def __init__(self):
        self.usage_stats = UsageStats()
        
    def adjust_priority(self, soul_id, feedback):
        """根据反馈调整优先级"""
        current = self.get_priority(soul_id)
        
        if feedback == "used_helpful":
            # 灵魂被使用且有帮助，提升优先级
            new_priority = min(1.0, current + 0.05)
        elif feedback == "used_not_helpful":
            # 灵魂被使用但无帮助，降低优先级
            new_priority = max(0.1, current - 0.1)
        elif feedback == "not_used_suggested":
            # 建议了但没被使用，轻微降低
            new_priority = max(0.1, current - 0.02)
        
        self.update_priority(soul_id, new_priority)
```

---

## 六、实现架构

### 6.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   CLI 入口   │  │  IDE 集成   │  │  API 服务   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      触发器引擎                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ 关键词触发器  │  │ 路径触发器   │  │ 错误触发器  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ API 触发器   │  │ 时间触发器   │  │ 组合触发器  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      调度器                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  相关性计算 → 优先级排序 → Token 预算分配 → 加载决策      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      加载器                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ 懒加载器    │  │ 预加载器    │  │ 增量加载器   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      缓存层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ L1 内存缓存  │  │ L2 压缩缓存 │  │ L3 索引缓存 │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      存储层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ 灵魂文件存储 │  │ 索引数据库   │  │ 向量数据库   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 核心数据结构

```typescript
// 灵魂元数据
interface SoulMetadata {
  id: string;
  name: string;
  description: string;
  version: string;
  category: string;
  tags: string[];
  keywords: string[];
  triggers: TriggerConfig[];
  priority: number;
  tokenCount: number;
  dependencies: string[];
  conflicts: string[];
}

// 触发器配置
interface TriggerConfig {
  type: 'keyword' | 'file_path' | 'api_call' | 'error_stack' | 'time' | 'composite';
  patterns: string[];
  weight: number;
  matchMode: 'exact' | 'fuzzy' | 'semantic';
}

// 加载状态
interface LoadState {
  soulId: string;
  loadLevel: 'skeleton' | 'core' | 'full';
  cached: boolean;
  lastAccessed: Date;
  accessCount: number;
}

// 上下文组装结果
interface AssembledContext {
  primarySouls: LoadedSoul[];
  secondarySouls: LoadedSoul[];
  totalTokens: number;
  conflicts: ConflictInfo[];
  resolutionNotes: string[];
}
```

### 6.3 接口设计

```python
class OnDemandLoader:
    """按需加载器主接口"""
    
    def analyze_context(self, context: Context) -> List[TriggerMatch]:
        """分析当前上下文，返回触发匹配"""
        pass
    
    def select_souls(self, triggers: List[TriggerMatch], 
                     budget: TokenBudget) -> List[SoulSelection]:
        """选择要加载的灵魂"""
        pass
    
    def load_souls(self, selections: List[SoulSelection],
                   level: LoadLevel) -> List[LoadedSoul]:
        """加载选中的灵魂"""
        pass
    
    def assemble_context(self, loaded_souls: List[LoadedSoul]) -> str:
        """组装最终上下文"""
        pass
    
    def get_recommended_souls(self, context: Context) -> List[SoulRecommendation]:
        """获取推荐灵魂列表（用于UI展示）"""
        pass
```

---

## 七、优先级建议

### P0 - 核心必需

| 模块 | 描述 | 工作量 | 依赖 |
|------|------|--------|------|
| 关键词触发器 | 基础文本匹配 | 2天 | 无 |
| 懒加载器 | 核心加载机制 | 3天 | 无 |
| LRU 缓存 | 基础缓存 | 1天 | 无 |
| 基础索引 | 关键词倒排索引 | 2天 | 无 |

### P1 - 重要增强

| 模块 | 描述 | 工作量 | 依赖 |
|------|------|--------|------|
| 语义搜索 | 向量嵌入匹配 | 5天 | 向量模型 |
| 优先级排序 | 多维度排序算法 | 3天 | 基础索引 |
| 上下文组装 | 多模块合并 | 4天 | 懒加载器 |
| 预加载策略 | 基于历史的预加载 | 3天 | 使用统计 |
| 分层缓存 | L1/L2/L3 缓存 | 3天 | LRU 缓存 |

### P2 - 优化体验

| 模块 | 描述 | 工作量 | 依赖 |
|------|------|--------|------|
| 动态优先级 | 基于反馈调整 | 2天 | 优先级排序 |
| 冲突解决 | 规则冲突处理 | 3天 | 上下文组装 |
| 语义压缩 | 内容智能压缩 | 5天 | LLM |
| 增量加载 | 分级加载 | 3天 | 懒加载器 |
| 组合触发器 | 多条件组合 | 2天 | 关键词触发器 |

---

## 附录：参考实现

### Cursor Rules 动态上下文机制

Cursor 的 Skills 系统实现要点：
1. **描述预加载**：所有 Skill 的描述常驻上下文，完整内容按需加载
2. **语义搜索**：Agent 使用 grep 和语义搜索发现相关 Skills
3. **静态 vs 动态**：Rules 为静态上下文（每次都加载），Skills 为动态（按需加载）

### GPTMe Lessons 机制

GPTMe 的 Lessons 系统特点：
1. **YAML Front Matter 匹配**：
   ```yaml
   ---
   match:
     keywords: [commit message, git commit]
     tools: [shell]
   ---
   ```
2. **多维度匹配**：关键词、工具、模式三重匹配
3. **会话限制**：默认最多 20 个 Lessons 防止上下文膨胀
4. **Progressive Disclosure**：索引常驻，详情按需

### 实现建议

基于以上分析，推荐实现路径：

1. **第一阶段（MVP）**：关键词触发 + 懒加载 + LRU 缓存
2. **第二阶段**：语义搜索 + 优先级排序
3. **第三阶段**：预加载 + 分层缓存 + 增量加载
4. **第四阶段**：动态优先级 + 冲突解决 + 语义压缩

---

*报告完成于 2026-03-10*