# 研究报告：用户问题到开源知识的映射

**日期**: 2026-03-11  
**主题**: 如何将用户问题映射到开源项目的知识和经验

---

## 1. 本质是什么？

**核心是语义检索 + 意图识别。**

用户描述的"麻烦"（自然语言）→ 需要转化为 → 结构化查询 → 匹配知识库中的解决方案。

这本质是一个 **Question-Answering over Knowledge Base** 问题，涉及：
- **意图识别 (Intent Detection)**: 理解用户想解决什么问题
- **实体抽取 (Entity Extraction)**: 提取关键信息（错误码、工具名、场景）
- **语义匹配 (Semantic Matching)**: 将问题映射到相关文档/解决方案

---

## 2. 简单技术方案

### 方案 A: RAG (Retrieval Augmented Generation) — 推荐

```
用户问题 → Embedding → 向量库检索 → Top-K 文档 → LLM 生成答案
```

**工具**: LangChain、LlamaIndex、Milvus、Chroma

**优点**: 
- 无需训练，部署快
- 适合知识库文档（README、issues、解决方案）

### 方案 B: Intent Detection + 规则映射

```
用户问题 → 分类模型 → 预设意图类别 → 映射到对应知识库
```

**工具**: BERT/Transformer 分类器、Rasa、Dialogflow

**优点**:
- 可控性强，适合意图明确的场景

### 方案 C: 混合检索 (BM25 + Embedding)

```
BM25: 关键词精确匹配 (如错误码 "TS-999")
Embedding: 语义相似度检索
→ 融合结果
```

Anthropic 推荐：BM25 处理精确匹配，Embedding 处理语义理解。

---

## 3. 最佳实践参考

| 场景 | 推荐方案 |
|------|----------|
| 开源项目文档问答 | RAG + 向量检索 |
| GitHub Issues 解决方案 | 混合检索 (BM25 + Embedding) |
| 意图明确的工具使用问题 | Intent Detection + 模板映射 |
| 需要可解释性 | Knowledge Graph + 实体关系 |

### 关键洞见

1. **从用户问题出发，而非从知识出发** — 先收集真实用户问题，再反推需要什么知识
2. **错误码/特定术语用 BM25，通用描述用 Embedding** — 混合检索效果最佳
3. **小知识库可用全文搜索 + LLM 重排** — 不需要向量库
4. **持续迭代** — 用户问题会不断出现新模式，需要定期更新检索策略

---

## 4. Doramagic 可行的轻量实现

1. **收集阶段**: 抓取开源项目的 issues、FAQ、文档
2. **索引阶段**: 用 Embedding 模型 (text-embedding-3-small) 向量化，存入向量库
3. **查询阶段**: 用户问题 → 向量检索 → Top-5 结果 → LLM 总结输出

**技术栈**: LangChain + OpenAI (或本地 embedding 模型) + Chroma/Qdrant

---

*核心一句话: 用 RAG 做语义检索，用混合检索处理精确匹配，用 LLM 做答案生成。*
