# WHY 提取报告：funNLP（Gemini v2）

```yaml
- why_id: W001
  type: architecture
  claim: "采用『原子化平铺文件』而非『中心化数据库』或『统一 API』来组织海量资源"
  reasoning_chain: "海量异构 NLP 数据 → 统一数据库会带来极高的 Schema 维护成本 → 采用 Git 目录结构平铺 → 用户可以通过 `git clone` 或直接下载单个文件实现『即取即用』，降低了『NLP 民工』的使用门槛"
  evidence:
    - type: CODE
      source: "funNLP/:L1-100 (目录结构展示了数十个平行文件夹)"
    - type: DOC
      source: "README.md:L46 (提到：几乎最全的中文NLP资源库，满足大家的收集癖)"
  contrast: "对比 NLTK 或 SpaCy 的数据加载器，它们需要通过特定的 Python API 下载并加载。funNLP 选择了最原始的文件组织，换取了跨语言（Java/C++/Python均可直接读文本）的极致通用性。"

- why_id: W002
  type: selection
  claim: "优先存储原始文本（Plain Text）和压缩包，而非结构化 JSON/Parquet 格式"
  reasoning_chain: "NLP 基础任务（分词、词性标注）对速度极度敏感 → 原始文本可以通过 grep/awk 快速检索和处理 → 减少序列化/反序列化的计算开销 → 符合项目『武器库』的定位"
  evidence:
    - type: CODE
      source: "data/IT词库/THUOCL_it.txt:L1-10"
    - type: CODE
      source: "data/公司名字词库/Company-Names-Corpus（480W）.rar"
  contrast: "不选择 JSON 格式是因为在处理百万级词库（如 480W 公司名）时，JSON 的冗余字段会占用过多内存和磁盘空间，且不方便在 Linux Shell 下直接预览。"

- why_id: W003
  type: implementation
  claim: "处理脚本采用极其简化的指令式逻辑，拒绝抽象化和工程化封装"
  reasoning_chain: "项目定位为『民工的乐园』 → 核心受众是需要快速解决具体问题的开发者 → 脚本必须『一眼看透』逻辑以便用户根据自己的数据格式微调 → 采用最简单的 string.split 拆分"
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py:L1-12"
  contrast: "没有使用泛化的 CSV 解析库或正则提取框架。这种『硬编码』的脚本虽然不具备通用性，但对特定文件的处理是透明且零依赖的，用户可以直接复制逻辑到自己的生产脚本中。"

- why_id: W004
  type: constraint
  claim: "数据分类逻辑遵循『业务领域』维度而非『语言学』维度"
  reasoning_chain: "学术界按分词、语义、语法分类 → 工业界需求通常是『我需要金融词库』或『我需要医疗词库』 → 目录按行业（财经、法律、医学、汽车）划分 → 实现精准的生产力对接"
  evidence:
    - type: CODE
      source: "funNLP/data/ (目录名包含：财经词库、法律词库、医学词库、食物词库)"
    - type: DOC
      source: "README.md:L55-65 (分类表格中包含了行业应用分类)"
  contrast: "为什么不按『名词/动词』或『实体/关系』分类？因为在实际业务中，特定行业的专有名词（如医学词库）是解决分词错误最有效的武器。"

- why_id: W005
  type: negation
  claim: "刻意不对数据进行『强一致性校验』和『标准化清洗』"
  reasoning_chain: "中文 NLP 数据来源极其碎片化（爬虫、第三方公开数据集、手动整理） → 强制标准化会导致大量贡献者因为格式问题被拒 → 接受『脏数据』的存在 → 依靠社区的『多样性』覆盖『准确性』的不足"
  evidence:
    - type: CODE
      source: "data/繁简体转换词库/fanjian_suoyin.txt (简单的索引映射)"
    - type: INFERENCE
      source: "项目中缺乏任何形式的 CI (GitHub Actions) 来验证数据格式的正确性，仅保留 README 作为索引"
  contrast: "相比 HuggingFace Datasets 严格的格式检查，funNLP 选择做『脏、乱、快』的集散地，这种低门槛策略使其成为了中文 NLP 领域 Star 数最高的资源库。"

- why_id: W006
  type: architecture
  claim: "将 README.md 作为项目的『动态路由表』而非简单的文档"
  reasoning_chain: "项目包含数千个外部链接和本地文件 → Git 目录无法展现外部链接的价值 → README 承载了大部分『HOW』和链接索引 → 项目本质上是一个以 README 为核心的知识图谱，文件库只是其附庸"
  evidence:
    - type: DOC
      source: "README.md:L70-150 (长达数千行的分类链接列表)"
  contrast: "没有选择建立一个专门的 Wiki 或文档网站。这种『文档即仓库』的设计让用户在通过浏览器访问 GitHub 时，能瞬间获得搜索和定位资源的能力，符合开发者在 GitHub 搜索资源的直觉。"
```
