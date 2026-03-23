# WHY 提取报告：funNLP（Sonnet v3 — Stage 0 v2）

> 分析范围：README.md（1056行）、data/目录下所有静态文件、data/中文分词词库整理/thirtyw.py、.github/FUNDING.yml
>
> 本报告为 v3 版本，在 v2（7条）基础上提取新角度，不重复 v2 已覆盖的设计决策。
> v2 已覆盖：README-as-product、THUOCL词频格式、无统一加载API、谣言result字段、古诗按主题分类、正则内嵌代码、注释历史保留。

```yaml
- why_id: W001
  type: selection
  claim: "停用词以四个机构独立文件并存，而不是合并去重成单一标准停用词表"
  reasoning_chain: >
    data/停用词/ 目录下存在四个独立文件：百度停用词表.txt、哈工大停用词表.txt、
    四川大学停用词表.txt、中文停用词库.txt。
    这四个文件来自不同机构，覆盖不同领域的停用词策略（百度偏搜索，哈工大偏学术NLP）。
    项目没有将它们合并成一个 merged_stopwords.txt。
    原因：停用词的选择本身是一个领域决策，不同任务（情感分析 vs 信息检索 vs 文本分类）
    对停用词的定义不同；哈工大的"的"可能在某些任务中不该被过滤。
    如果合并，用户就只能接受一套标准，失去选择的自由。
    保持四份独立文件让用户根据自己的任务语境自行选择或组合。
  evidence:
    - type: CODE
      source: "data/停用词/百度停用词表.txt、data/停用词/哈工大停用词表.txt、data/停用词/四川大学停用词表.txt、data/停用词/中文停用词库.txt（四文件并存于同一目录，无合并文件，无 README 说明差异）"
    - type: DOC
      source: "README.md:L23（定位为'NLP民工的乐园：几乎最全的中文NLP资源库'——'最全'意味着宁可冗余也不删减；合并停用词会损失来源多样性信息，与'最全'定位相悖）"
    - type: INFERENCE
      source: "停用词领域中百度/哈工大/四川大学的词表在学术界已是公认的不同流派（百度偏通用搜索，哈工大偏语言学分析），合并会掩盖这个领域知识，保留原始分发形式让用户能追溯来源"
  contrast: >
    如果合并成单一停用词表，维护更简单，用户也更省事。
    但合并意味着主张"这是正确的停用词集合"——而停用词没有通用标准答案。
    四川大学的词表在金融文本任务上可能效果更差，哈工大的词表在社交媒体上可能过于激进。
    保留四份独立来源，让用户自己做这个领域决策，符合项目"给工具不给方法"的核心定位。

- why_id: W002
  type: architecture
  claim: "README 采用双层并列目录结构，将 LLM/ChatGPT 内容与传统NLP内容物理隔离，而不是按功能统一排序"
  reasoning_chain: >
    README.md L31-39 的导航区包含两个并列的 Markdown 表格：
    - 第一个表格（L31-33）只有一列，全部是 LLM 相关节：类ChatGPT模型评测/资料/框架、
      LLM训练推理、提示工程、文档问答、行业应用、课程、安全、多模态、数据集
    - 第二个表格（L36-39）分两列，是传统NLP工具节：语料库、词库、预训练模型、抽取、
      知识图谱、文本生成、文本摘要...
    两个表格在视觉上是分开的块，第一个用 fire emoji 标记（热门/新兴）。
    这种分离意味着作者识别到"LLM时代内容"与"传统NLP工具"是两种不同性质的资源：
    前者时效性强、迭代快、更受关注；后者相对稳定、面向基础工程需求。
    将它们混在一个统一的字母序或功能序目录中，会导致新用户无法快速定位到当下最热门的内容。
  evidence:
    - type: CODE
      source: "README.md:L31-33（第一个单列表格，全部条目是'类ChatGPT的模型评测对比'、'类ChatGPT的资料'等LLM专区节，用 fire emoji 标注热度）"
    - type: CODE
      source: "README.md:L36-39（第二个双列表格，条目是'语料库'、'词库及词法工具'、'预训练语言模型'等传统NLP内容，与第一个表格物理隔离）"
  contrast: >
    统一目录（如按功能字母序或发布时间序）是 awesome-lists 的通用做法，
    比如 awesome-python 或 awesome-deep-learning 都是单一线性列表。
    funNLP 的双层目录隐含了一个时代判断：LLM是"这个时代的新武器"，
    需要专区置顶；传统NLP工具是"基础设施"，维持原有组织不变。
    这是一个关于内容权重的架构决策，而不仅是排版偏好。

- why_id: W003
  type: selection
  claim: "名字库按中/英/日三个语种独立存放子目录，并各自保留语种内部细分（古代名、性别字段），而不是按功能（人名识别用途）统一整合"
  reasoning_chain: >
    data/中英日文名字库/ 下有三个子目录：
    - Chinese_Names_Corpus/：包含古代名（25W）、家族姓名（1k xlsx）、性别标注（120W）、无标注（120W）、亲属关系（4.8k xlsx）
    - English_Names_Corpus/：英文名+中文译名（48W）、无译名（2W）
    - Japanese_Names_Corpus/：日文名假名（18W txt）、xlsx版（1W）
    三个语种没有合并成一个 names_all.txt，甚至英文名额外保留了中文译名字段。
    中文名内部还按"古代/现代/性别"细分，反映了不同下游任务（古代文本NER vs 现代社交媒体NER vs 性别预测）的差异化需求。
    这种细粒度保留比合并更有价值：古代名（25W）的分布与现代名（120W）完全不同，
    混用会污染各自的训练数据。
  evidence:
    - type: CODE
      source: "data/中英日文名字库/Chinese_Names_Corpus/Ancient_Names_Corpus（25W）.txt + Chinese_Names_Corpus_Gender（120W）.txt（同一语种内两个独立文件，古代名与现代名分开，未合并；Gender版本保留性别标注字段）"
    - type: CODE
      source: "data/中英日文名字库/English_Names_Corpus/English_Cn_Name_Corpus_Gender（48W）.txt（英文名+中文译名+性别三字段并存，而非仅保留英文名——这个字段设计只有在英中翻译任务中才有价值，说明作者为特定用途保留了字段）"
    - type: DOC
      source: "README.md:L401（'中文（现代、古代）名字、日文名字、中文的姓和名、称呼...英文->中文名字（李约翰）'——README 条目描述直接说明了不同细分的用途差异，这是刻意维度分割而非懒于合并）"
  contrast: >
    合并成单一人名词库（如 names_all.txt）操作简单，用于 jieba 自定义词典时也更方便。
    但会丢失关键元数据：古代名和现代名的统计分布不同（现代名集中于常见字），
    用于 NER 训练数据时混用会导致模型对古代文本表现变差。
    保留细粒度分割让用户能选择最适合自己任务分布的子集。

- why_id: W004
  type: negation
  claim: "项目没有为停用词、词库等数据文件提供版本号或最后更新日期标注，但对谣言数据集例外"
  reasoning_chain: >
    data/ 目录下绝大多数文件名不含日期或版本号（如 THUOCL_it.txt、同义词库.txt、professions.txt），
    文件内部也没有版本注释行。
    但 data/中文谣言数据/rumors_v170613.json 文件名包含 v170613（2017年6月13日），
    且该目录有独立的 README.md 要求学术引用。
    这种不一致揭示了一个隐含规则：
    - 词库类文件（工程辅助资源）不需要版本控制，因为"词语本身不会过期"，
      用户不需要知道词库是否更新，直接拿最新版本用即可
    - 数据集类文件（谣言数据）需要版本号，因为学术论文引用时需要精确的数据集版本，
      才能保证可复现性
    这是对两类资源不同使命的精确区分，而不是偶然遗漏。
  evidence:
    - type: CODE
      source: "data/中文谣言数据/rumors_v170613.json（文件名包含 v170613 版本日期标记）vs data/停用词/百度停用词表.txt（无任何版本标记）——同一 data/ 目录下存在两种截然不同的命名策略"
    - type: DOC
      source: "data/中文谣言数据/README.md:L21-49（要求引用论文 'Detecting Rumors from Microblogs with Recurrent Neural Networks'，精确到作者/年份/会议——学术引用需求驱动了版本号的必要性；词库没有对应的引用要求）"
  contrast: >
    如果统一给所有文件加版本号，管理成本极高（每次词库微调都要改文件名）。
    如果统一不加版本号，学术用户无法确认使用的谣言数据集是否与论文中一致。
    这个"差异化版本策略"精确地将工程用途资源（词库）与学术用途资源（标注数据集）区分开来，
    是信息架构层面的最小化复杂度决策。

- why_id: W005
  type: implementation
  claim: "中文缩写库保留了原始 NLP 任务的 train/dev/test 三分法，而不是合并成单一词库文件"
  reasoning_chain: >
    data/中文缩写库/ 包含三个文件：dev_set.txt、test_set.txt、train_set.txt。
    这三个文件的命名直接来自机器学习数据集划分惯例（训练/验证/测试集）。
    文件内容是"缩写: 原文分词结果"格式（如'全国人大: 全国 人民 代表大会'），
    这是缩写消歧（abbreviation expansion）监督学习任务的标准数据格式。
    项目没有将三个文件合并成一个 abbreviation_dict.txt——
    因为这个数据集的主要用途不是"查词典"，而是"训练/测试模型的能力"；
    如果合并，用户就无法直接用于标准的 train/val/test 评估流程，
    需要重新切分，引入额外的随机性（不同切分会导致不同的评估结果，影响论文可比性）。
  evidence:
    - type: CODE
      source: "data/中文缩写库/train_set.txt + dev_set.txt + test_set.txt（三文件并存，命名直接对应机器学习评估流程三阶段；内容格式为'史地: 历史/n 和/cc 地理/n'——分词标注格式，不是简单的缩写:全称映射）"
    - type: DOC
      source: "README.md:L402（描述为'全国人大: 全国 人民 代表大会; 中国: 中华人民共和国;女网赛: 女子/n 网球/n 比赛/vn'——示例中包含词性标注（/n, /cc, /vn），说明这是为序列标注任务准备的训练数据，而非查询词典）"
  contrast: >
    简单词典用途只需要一个缩写→全称的映射文件，不需要 train/dev/test 分割。
    保留三分法意味着作者将其定位为"可复现的学术基准数据集"而非"工程用词典"。
    如果合并，下游使用者要么随机切分（引入不可复现性），
    要么用全量数据训练（无法评估泛化性）——两种选择都会降低数据集的学术价值。

- why_id: W006
  type: negation
  claim: "项目没有为 README 中的 497 个 GitHub 链接提供时效性说明或死链检测，即使部分资源明确标注了时间敏感性"
  reasoning_chain: >
    README.md 包含 497 个 GitHub 链接（repo_facts 链接统计数据），
    其中部分条目明确包含时间标注，如：
    - L197：'截止2023年5月3日'（Chatbot Arena Elo 排名）
    - L169：'大型语言文献综述--中文版'（论文 PDF 直接推送到本 repo data/paper/）
    但没有任何条目被标记为"已过时"或"链接可能失效"，
    也没有 CI/CD 脚本定期检查链接有效性（.github 目录下只有 FUNDING.yml）。
    这不是遗忘，而是一种信息策略：
    "快照"而非"实时维护"——README 记录的是"某个时间点的最佳资源集合"，
    不追求永远最新，而追求历史完整性。
    LLM 评测排名（如 Elo 截止 2023-05-03）保留时间标注，
    但不删除，说明作者认为历史数据也有参考价值。
  evidence:
    - type: CODE
      source: "README.md:L197（'[截止2023年5月3日](https://lmsys.org/blog/2023-05-03-arena/)'——直接在链接文字中标注截止日期，而非在正文中警告'此链接可能已过期'）"
    - type: DOC
      source: ".github/FUNDING.yml（.github 目录下只有打赏配置文件，完全没有 link-checker.yml 或任何 CI 配置；项目没有 requirements.txt 也就没有自动化运行环境可言）"
    - type: CODE
      source: "README.md:L372（链接统计：外部链接 642 个，GitHub 链接 497 个——规模如此庞大的链接库完全依赖人工维护，不设死链检测是有意为之的低成本策略）"
  contrast: >
    awesome-lists 社区有 awesome-lint 等工具可以检查链接有效性，
    许多类似项目会设置 GitHub Actions 定期做 link check。
    但 link check 对于快照型知识库会产生大量误报（被删的 GitHub repo 不代表知识失效），
    且维护 CI 配置本身需要时间成本。
    funNLP 的隐含判断是：NLP 领域迭代快，链接过期是正常现象，
    "显示快照状态的历史" 比 "维护一个随时可用的最新列表" 更诚实也更可持续。

- why_id: W007
  type: architecture
  claim: "有趣搞笑工具被设立为独立的一级分类节（而非并入'综合工具'或'其他'），且排序在金融/医疗/法律领域NLP之前"
  reasoning_chain: >
    README.md L920 是 '# 有趣搞笑工具' 节，包含汪峰歌词生成器、女友情感波动分析、
    NLP太难了系列、变量命名神器、CoupletAI 对联生成等条目。
    这一节被安排在 L890 综合工具之后、L939 课程报告之前。
    将"娱乐性"工具独立成节有两个效果：
    (1) 宣告这个资源库不是纯粹的学术/工程工具集，它也包含"好玩的东西"，
        这与作者在 README 开头写的"很多包非常有趣，值得收藏，满足大家的收集癖"完全对应
    (2) 把娱乐工具和严肃工具物理隔开，让专业用户不会被"娱乐噪声"干扰，
        但同时也给娱乐爱好者一个专门的入口
    这是一个受众分层的架构决策：同一个 README 同时服务"NLP工程师找工具"和"NLP学生找乐子"两种用途。
  evidence:
    - type: CODE
      source: "README.md:L920（'# 有趣搞笑工具'作为独立一级标题，与'# 综合工具'（L890）、'# 课程报告面试等'（L939）并列——而非作为综合工具的子节）"
    - type: DOC
      source: "README.md:L26-27（'很多包非常有趣，值得收藏，满足大家的收集癖！'——开场白直接表达了'趣味收藏'作为独立价值维度，与工程实用价值并列；有趣工具独立成节是对这个声明的架构实现）"
  contrast: >
    大多数技术资源列表（如 awesome-python）没有"有趣工具"分类，
    娱乐性项目要么进入 Miscellaneous，要么被排除在外。
    funNLP 设立独立"有趣搞笑"节，隐含了一个价值判断：
    降低 NLP 学习门槛的娱乐化工具（汪峰歌词生成、对联生成）
    与生产用工具（jieba、BERT）具有同等的分类地位，
    因为吸引入门者也是这个项目的使命之一。

- why_id: W008
  type: implementation
  claim: "thirtyw.py 的输出文件（30wdict.txt / 30wdict_utf8.txt）与脚本本身一同提交到 git，而不是在 .gitignore 中排除"
  reasoning_chain: >
    data/中文分词词库整理/ 目录同时包含：
    - thirtyw.py（14行Python2脚本，读取30wChinsesSeqDic.txt，过滤并写入30wdict.txt）
    - 30wdict.txt（脚本的输出文件）
    - 30wdict_utf8.txt（UTF-8编码的输出文件）
    - 30wChinsesSeqDic.txt（输入文件）
    即：输入文件 + 脚本 + 输出文件三者都在仓库中。
    通常的工程实践是将可由代码生成的文件加入 .gitignore（生成物不提交），
    但 funNLP 选择将输出文件一同提交。
    原因：项目不假设用户有 Python 2 运行环境（脚本使用 Python 2 print 语法），
    也不要求用户理解脚本逻辑才能使用词库。
    提交输出文件意味着用户可以"零运行"直接使用——
    git 在这里被用作内容分发平台，而不是重现工程流程的版本控制系统。
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py:L11（'print temp_sublist[1]'——Python 2 print 语句，无括号；同目录下 30wdict.txt 是该脚本生成的输出文件，二者同时存在于仓库）"
    - type: CODE
      source: "data/中文分词词库整理/30wdict.txt + 30wdict_utf8.txt（生成物文件与源脚本并存，且项目无 .gitignore 文件——说明不存在任何排除生成物的配置，这是刻意包含而非遗漏）"
  contrast: >
    标准工程实践（如 Python 项目的 .gitignore 模板）会将 *.pyc 和生成文件排除在 git 之外，
    通过 Makefile 或 CI 重新生成。
    但重新生成需要：Python 2 环境、理解脚本参数、了解输入文件格式——
    这些对于"只想用词库的 NLP 从业者"都是不必要的摩擦。
    提交生成物把 git 变成了一个"下载站"（clone 即可用），
    而不是一个"开发环境"（需要先跑脚本才能用）。
```
