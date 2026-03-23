# WHY 提取报告：funNLP（Sonnet v2）

> 分析范围：README.md（1056行）、data/目录下所有静态文件、data/中文分词词库整理/thirtyw.py、.github/FUNDING.yml

**排除项说明**：thirtyw.py 使用 Python 2 print 语法（L10）被初步识别为候选，但经过历史遗留判断排除——该脚本已预先运行完毕（输出文件已提交），无新旧写法混合迹象，改成 Python 3 语法不改变行为，属历史遗留而非刻意选择。

```yaml
- why_id: W001
  type: architecture
  claim: "项目以单一 README.md 作为唯一的可执行产出物，而不是 Python 包或 CLI 工具"
  reasoning_chain: >
    整个 repo 的唯一 Python 文件（thirtyw.py）只有 14 行，功能是一次性文件转换脚本，
    且已生成了输出文件（30wdict.txt / 30wdict_utf8.txt）一同提交。
    整个项目没有 setup.py、requirements.txt、Makefile、任何测试或 CI 配置。
    唯一的 .github 文件是 FUNDING.yml（打赏入口）。
    README.md 本身是 1056 行的超长文档，包含所有分类索引和正则表达式示例。
    这表明作者有意识地将"知识索引"本身作为产品交付，而不是可安装的工具库。
    受众是"要找资源的 NLP 从业者"，不是"要导入一个 package 的开发者"——
    因此 README-as-product 是刻意选择，而非懒得写 setup.py。
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py:L1-14（唯一 Python 文件，14 行一次性脚本，已产生输出文件 30wdict.txt 并一同提交）"
    - type: CODE
      source: "README.md:L22（'The Most Powerful NLP-Weapon Arsenal'——自定位为武器库/兵工厂，不是框架）"
    - type: DOC
      source: ".github/FUNDING.yml:L12（custom 字段指向打赏页面，而非 PyPI 或 conda 发布链接；完全没有 CI/CD 配置文件）"
  contrast: >
    如果目标是可复用工具库，通常会有 setup.py、__init__.py、tests/、pip install 说明。
    spaCy、HanLP 等同类项目都有完整 package 结构。
    funNLP 的价值在于"帮你找到工具"，而不是"成为工具"，
    因此单 README 架构是最低摩擦的实现方式。

- why_id: W002
  type: selection
  claim: "域名词库统一采用 THUOCL 格式（词+Tab+频率）而不是纯词列表，即使本项目并不做词频计算"
  reasoning_chain: >
    IT词库、动物词库、医学词库、法律词库、地名词库、财经词库、历史名人词库等七个领域词库
    全部使用同一格式：词语\t词频。
    但项目本身没有任何加载或处理这些词频的代码（唯一的 thirtyw.py 处理的是不同格式的文件）。
    这表明这批文件直接来自清华大学 THUOCL（开放中文词库）原始分发格式，
    作者选择原封不动地嵌入而不是剥离词频列——
    因为保留词频让下游用户能直接用于 jieba 自定义词典（jieba add_word 支持频率参数），
    同时也保留了来源信息的完整性（可追溯原始分布）。
  evidence:
    - type: CODE
      source: "data/IT词库/THUOCL_it.txt:L1-10（'字符串\t395499'，词+Tab+频率格式）"
    - type: CODE
      source: "data/动物词库/THUOCL_animal.txt、data/医学词库/THUOCL_medical.txt、data/法律词库/THUOCL_law.txt（同一格式，跨七个领域一致）"
    - type: DOC
      source: "README.md:L412（'THU整理的词库 IT词库、财经词库、成语词库…'——明确标注来源为清华 THUCTC，保留格式是对来源的尊重和追溯）"
  contrast: >
    纯词列表（每行一个词）是更简单的格式，方便人工浏览。
    但 jieba 自定义词典格式恰好是"词 词频 词性"三列，
    保留 THUOCL 的词频列让用户可以零处理直接 import，
    而剥离词频则会破坏这个"即插即用"的价值。

- why_id: W003
  type: negation
  claim: "项目没有提供统一的数据加载 API，所有词库以原始文件形式分发，让用户自己决定如何加载"
  reasoning_chain: >
    data/ 目录下有近百个 .txt 和 1 个 .json 文件，格式各异：
    - THUOCL 词频格式（tab 分隔）
    - 纯词列表（每行一词）
    - JSON 结构（谣言数据）
    - 分词对照格式（缩写库：词 词性/词 词性）
    - 繁简索引格式（单字对照）
    没有任何 Python module、__init__.py 或统一的 load() 函数。
    README 中也没有"如何加载这些文件"的代码示例。
    这是刻意的"不封装"决策——与 README-as-product 架构一致：
    工具箱的价值是"有什么"，如何用由用户决定。
    强行统一格式会破坏下游灵活性（有人用 jieba，有人用 HanLP，
    有人只需要纯 set 集合）。
  evidence:
    - type: CODE
      source: "data/中文缩写库/train_set.txt:L1-5（格式为'史地: 历史/n 和/cc 地理/n'，分词标注格式）vs data/IT词库/THUOCL_it.txt:L1（'字符串\t395499'，频率格式）——同一 data/ 目录下两种完全不同的格式，无统一抽象层"
    - type: CODE
      source: "data/中文谣言数据/rumors_v170613.json:L1（JSON 格式，含 rumorCode/title/informerName 等11个字段）——与其他 txt 词库完全不同的结构，无统一加载接口"
    - type: DOC
      source: "README.md:L22-23（定位为'NLP民工的乐园：几乎最全的中文NLP资源库'——明确是资源库而非工具库；README 中没有任何'pip install'或'import'代码示例）"
  contrast: >
    如果提供统一 API，需要为每种格式写 parser，
    且会引入版本兼容负担（pandas vs 纯 Python，Python 2 vs 3 等）。
    更重要的是：统一 API 意味着主张"正确用法"，
    而这与项目"给工具，不教用法"的定位矛盾。
    直接分发原始文件让用户保留最大灵活度。

- why_id: W004
  type: selection
  claim: "谣言数据以完整 JSON 对象形式（含审查结论字段 result）分发，而不是只分发谣言文本"
  reasoning_chain: >
    rumors_v170613.json 每条记录包含 rumorCode、举报者、被举报者、谣言原文、
    visitTimes、result（审查结论）、publishTime 共11个字段。
    其中 result 字段包含微博官方的辟谣理由和处置决定——
    这意味着数据集天然带有"负标签"（不实信息的判定依据）。
    data/README.md 明确要求引用原始学术论文（刘知远等人 2015 年发表的中文社交媒体谣言论文），
    说明这个数据集来自学术研究，保留 result 字段是为了支持谣言检测的监督学习任务
    （谣言文本+官方辟谣=正负样本对）。
    如果只保留谣言文本，数据集就退化成无监督语料。
  evidence:
    - type: CODE
      source: "data/中文谣言数据/rumors_v170613.json:L1（完整 JSON 结构：'result':'经查，该微博称...不实...根据《微博社区管理规定》第19条予以标识处理'——result 字段包含判定依据和处置结论）"
    - type: DOC
      source: "data/中文谣言数据/README.md:L7-18（字段释义表，明确解释每个字段的含义；L21-49 要求引用学术论文——数据集设计目标是支持学术研究，result 字段是谣言检测任务的 ground truth）"
  contrast: >
    如果只关心谣言内容挖掘（话题模型、词频统计），
    只需要 rumorText 字段即可。
    保留 result 字段的代价是数据集更复杂，
    但好处是支持分类任务：给定谣言文本，预测是否不实及原因。
    这是学术研究所需的标注数据，而不是内容挖掘所需的纯语料。

- why_id: W005
  type: architecture
  claim: "古诗词库按主题（月、雪、离别、爱情等）而不是按朝代或作者拆分成独立文件"
  reasoning_chain: >
    data/古诗词库/ 下有 25 个文件，文件名均为英文主题词：
    moon.txt、snow.txt、farewell.txt、love.txt、miss.txt、
    patriotic.txt、friendship.txt、landscape.txt 等。
    没有 tangshi_all.txt 或 author_libai.txt 这样的朝代/作者维度文件。
    主题维度的分割意味着目标用途是：
    给定应用场景（如"生成离别主题的诗词"或"检索月亮意象"），
    直接取对应主题文件作为语料——
    而不是按朝代或作者做学术研究（那样应该保留元数据字段）。
    这对生成式应用（自动对联、诗词生成）比学术分析更实用。
  evidence:
    - type: CODE
      source: "data/古诗词库/（目录结构：moon.txt、snow.txt、farewell.txt、love.txt 等25个主题文件，无作者/朝代维度文件）"
    - type: DOC
      source: "README.md:L565（'自动对联数据及机器人'）、L929（'CoupletAI - 对联生成'）、L574（'新词生成及造句'）——README 中文本生成类工具占主要篇幅，与诗词库按主题切割的用途对齐"
  contrast: >
    按朝代切分（唐诗、宋词）是学术惯例，如项目链接的
    'chinese-poetry' 开源库（README.md:L359）就是按朝代+作者+体裁组织的。
    funNLP 的古诗词库选择主题维度，
    是因为生成式 NLP 场景（文本生成、风格迁移）需要按语义主题检索，
    而不是按历史年代检索。

- why_id: W006
  type: implementation
  claim: "README 直接内嵌了身份证、IP 等正则表达式的代码，而不是仅提供外链，形成'可直接抄用'的效果"
  reasoning_chain: >
    README.md L751-756 的"常用正则表达式"章节中，
    身份证号正则（IDCards_pattern = r'^([1-9]\d{5}...）和
    IP 地址正则直接作为表格内容嵌入 Markdown，
    包含完整的可运行 Python 代码片段。
    而同页面其他资源（如工具库、数据集）都是"名称+描述+github链接"三列格式，
    不内嵌代码。
    正则表达式是极少数"完整性只有几行"且"每个项目都要重写一遍"的基础组件——
    内嵌代码的边际成本（占用 README 空间）远小于用户点击外链、阅读文档的成本。
    这是刻意的"零跳转"设计：最常用的正则直接可以复制粘贴。
  evidence:
    - type: CODE
      source: "README.md:L751（'IDCards_pattern = r\"^([1-9]\\d{5}[12]\\d{3}(0[1-9]|1[012])...\"——完整 Python 变量赋值代码直接嵌入 Markdown 表格单元格）"
    - type: CODE
      source: "README.md:L752-756（IP 地址、QQ 号、固话、用户名正则均以代码片段内嵌，与同文件其他条目'名称+描述+外链'格式形成明显对比）"
  contrast: >
    只提供外链（如 github.com/VincentSit/ChinaMobilePhoneNumberRegex）
    要求用户跳转→阅读另一个 README→复制代码，三步变一步。
    对于只有一两行的正则表达式，内嵌比外链提供了更高的即用性。
    而对于更复杂的工具（如 jieba、BERT），README 只给外链，
    因为完整代码无法有意义地内嵌。

- why_id: W007
  type: negation
  claim: "项目没有删除 README 中已注释掉的旧版目录结构（<!--ts-->块），而是保留了完整的注释历史"
  reasoning_chain: >
    README.md L41-125 包含一个大块 HTML 注释（<!-- ... -->），
    其中有完整的旧版目录生成标记（<!--ts-->、<!--te-->）和注释掉的目录条目。
    这段注释代码在渲染后不可见，对用户没有价值，
    但作者没有删除它。
    README.md L1031-1033 中还有另一段更大的 HTML 注释，
    包含超过1000字的历史内容列表。
    这种保留行为在 Markdown 文件中不常见（通常直接删除），
    说明作者用注释作为版本历史/草稿机制——
    而不是依赖 git history 来找回删除的内容。
    这反映了一种"个人维护项目"的工作方式：
    宁可注释掉也不敢删，因为可能以后要找回来。
  evidence:
    - type: CODE
      source: "README.md:L41-125（完整 HTML 注释块，包含旧版 <!--ts--><!--te-->目录生成标记和注释掉的目录条目列表，总计 84 行对用户不可见的注释代码）"
    - type: CODE
      source: "README.md:L1031-1033（第二段超大 HTML 注释，包含超过1000字的历史资源列表：'涉及内容包括但不限于：中英文敏感词、语言检测...'——已在正文中删除但保留在注释中）"
  contrast: >
    专业维护的开源项目通常依赖 git history 保存删除内容，
    直接在文件中删除过期代码，保持文件整洁。
    funNLP 的注释保留策略暴露了项目的个人工具/日记性质：
    作者用注释作为草稿区，这对个人使用高效，
    但对贡献者来说增加了理解文件结构的认知负担。
```
