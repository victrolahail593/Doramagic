# WHY 提取报告：funNLP（Gemini v3 — Stage 0 v2）
- why_id: W001
  type: architecture
  claim: "项目选择单一、巨型的 README.md 文件作为核心导航和信息分发中心，而非建立专门的网站或文档系统。"
  reasoning_chain: "项目的核心价值是“几乎最全的中文NLP资源库”的聚合与呈现 → 目标用户是需要快速查找资源的“NLP民工” → 单一Markdown文件在GitHub上具有最佳的可访问性、可搜索性（Ctrl+F）和零维护成本的特点 → 因此，采用一个包罗万象的 README.md 是最高效、直接地服务于目标用户和核心价值的架构选择。"
  evidence:
    - type: DOC
      source: "README.md:L23 - 项目副标题明确宣告其定位：'NLP民工的乐园: 几乎最全的中文NLP资源库'"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - README 结构分析显示其长达1056行，包含642个外部链接，证明其作为信息中心的体量。"
    - type: INFERENCE
      source: "选择Markdown而非静态网站（如Jekyll/Hugo）或数据库，是为了最大限度地降低维护复杂性，使作者能专注于内容聚合而非技术实现。"
  contrast: "替代方案是创建一个静态网站或wiki。但这种方案会引入开发、部署和托管的额外工作，违背了项目作为轻量级、易于维护的资源集合的初衷。一个简单的README文件足以满足核心需求。"
- why_id: W002
  type: architecture
  claim: "项目直接提供原始的、按主题分类的 .txt 词库文件，而非将其封装在数据库或API之后。"
  reasoning_chain: "项目的目的是提供即插即用的数据资源 → .txt是最通用、最无依赖的文本格式，任何编程语言都能轻松处理 → 将词库按主题（如财经、IT、医学）分文件夹存放，方便用户按需查找 → 这种“原始数据+语义化目录”的架构，最大化了数据的可用性和易用性。"
  evidence:
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 文件类型分布显示项目包含82个.txt文件，是数量最多的文件类型。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 目录结构显示了 `data/IT词库`, `data/财经词库`, `data/医学词库` 等清晰的主题分类。"
    - type: CODE
      source: "data/IT词库/THUOCL_it.txt - 文件内容为简单的'词语	词频'格式，易于任何脚本解析。"
  contrast: "可以将数据存储在SQLite数据库中。但这会增加用户的访问门槛，需要用户了解SQL或使用特定库来读取数据。提供原始.txt文件则无此障碍，用户甚至无需编程知识即可查看和使用。"
- why_id: W003
  type: negation
  claim: "项目刻意避免了任何形式的软件工程化，没有提供可安装的包、API或命令行工具。"
  reasoning_chain: "项目的定位是“资源库”，而非一个“工具”→ 提供软件（如Python包）会带来API设计、依赖管理、版本控制、测试、打包发布等巨大开销 → 这会分散作者维护核心内容（资源链接和词库）的精力 → 因此，项目通过完全放弃软件化的方式，确保其可以长期、低成本地维持其信息聚合的核心价值。"
  evidence:
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 项目类型被明确标识为 'non-code'，代码文件仅占1/112。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 项目缺少`setup.py`或`requirements.txt`等定义可安装软件包的元文件。"
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py - 唯一的Python文件是一个简单的、一次性的数据处理脚本，而非一个可复用的库或应用的一部分。"
  contrast: "可以创建一个`funnlp`的Python包，提供如`funnlp.get_stopwords()`之类的函数。但这将使项目从一个“数据与链接的集合”转变为一个需要持续软件维护的“工具库”，增加了维护负担，也限制了非Python用户的使用。"
- why_id: W004
  type: implementation
  claim: "README.md 广泛使用 Markdown 表格来结构化地展示外部资源列表，以提升信息的可扫描性和可比性。"
  reasoning_chain: "项目包含了数百个外部资源链接 → 用户需要在海量信息中快速找到所需内容 → Markdown表格以其'名称 | 描述 | 链接'的固定列格式，提供了一种比纯列表或段落更高效的视觉扫描路径 → 用户可以快速横向比较不同资源的特性，从而做出选择。这种格式是对海量链接进行有效组织的关键实现手段。"
  evidence:
    - type: DOC
      source: "README.md:L128-140 - '类ChatGPT的模型评测对比'部分使用表格清晰地列出了资源、描述和链接。"
    - type: DOC
      source: "README.md:L176-206 - '类ChatGPT的开源框架'部分同样采用表格，方便用户对比不同的开源框架。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 'README 结构分析'部分显示，从头到尾的每个资源分类都使用了表格结构。"
  contrast: "替代方案是使用简单的嵌套无序列表。但对于每个条目包含多个属性（名称、描述、链接）的情况，表格提供了更强的对齐和结构化，使得快速定位特定信息（如所有项目的描述）变得更加容易，而列表则显得松散且难以比较。"
- why_id: W005
  type: selection
  claim: "项目选择成为一个“宽而全”的资源索引，而非深入研究或开发某一个特定的NLP功能。"
  reasoning_chain: "NLP领域工具和研究迭代迅速，个人开发者难以在所有领域都做出顶尖工作 → 对于普通开发者（“民工”）而言，最大的痛点之一是信息过载，难以找到合适的现有工具 → 项目作者选择解决这个信息发现的痛点，通过人工筛选和分类，提供一个高质量的“导航页”→ 这种“策展人”的角色，其价值在于节省社区其他人的时间和精力，而非创造新工具。"
  evidence:
    - type: DOC
      source: "README.md:L24 - 口号 '在入门到熟悉NLP的过程中，用到了很多github上的包，遂整理了一下，分享在这里。' 表明了项目的策展和分享初衷。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 'README 链接统计'显示项目包含497个指向其他GitHub仓库的链接，证明其作为索引的本质。"
    - type: INFERENCE
      source: "项目的star数和影响力证明了社区对此类高质量、人工整理的资源索引有强烈需求。"
  contrast: "作者本可以利用这些词库资源，开发一个自己的中文NLP工具包。但相比于从零开始与现有成熟的工具（如Jieba, spaCy, HanLP）竞争，成为一个全面的资源导航者，为社区提供了独特且差异化的价值。"
- why_id: W006
  type: architecture
  claim: "项目在单一Repo中混合了两种不同形态的资源：外部链接集合（README）和内部原始数据（data/目录）。"
  reasoning_chain: "NLP任务通常需要算法（工具）和数据（语料）两部分 → README.md通过链接解决了“去哪里找工具”的问题 → data/ 目录通过内建词库解决了“去哪里找基础数据”的问题 → 将两者置于同一仓库，为用户提供了一个一站式的解决方案，既能找到外部的先进工具，也能获得本地可用的基础数据，满足了NLP实践的两种核心需求。"
  evidence:
    - type: DOC
      source: "README.md:L396 - 章节'# 词库及词法工具'，既有对本地词库的介绍，也有指向外部工具的链接。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 目录结构同时存在一个巨大的README.md文件和庞大的data/目录，两者并存。"
    - type: DOC
      source: "repo_facts_funNLP_v2.md - 数据文件列表和README链接统计共同证明了这两种资源形态的同时存在。"
  contrast: "作者可以创建两个独立的项目：一个`awesome-nlp-links`项目专门收集链接，另一个`chinese-lexicons`项目专门存放数据。但将两者合并，更能体现“NLP民工的乐园”这一站式服务理念，方便用户在一个地方同时获取工具信息和原始数据。"
