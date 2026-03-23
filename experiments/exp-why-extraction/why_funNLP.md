# WHY 提取报告：funNLP

> 项目：funNLP（NLP民工的乐园）
> 类型：中文NLP资源汇总库
> 提取日期：2026-03-13
> 提取人：Claude Sonnet 4.6（代码考古学家模式）

---

## WHY 列表

```yaml
- why_id: W001
  type: architecture
  claim: "选择单一 README 而非多页 Wiki/网站，将所有内容压进一个文件"
  reasoning_chain: >
    项目包含 1056 行 README，几乎是整个仓库的唯一入口 →
    没有独立文档站、没有子页面，仅有 data/ 目录下的词库文件 →
    这是一个「个人整理笔记外置化」而非「正式项目文档化」的产物 →
    单文件极大降低了维护摩擦：不需要管理链接跳转、版本同步、构建流程 →
    因此选择用 GitHub Markdown 渲染能力（anchor 跳转、表格、emoji）作为唯一 UI，
    把整个 README 当成一个「可交互的知识地图」
  evidence:
    - type: DOC
      source: "funNLP/README.md, L1-1056（全文 1056 行，无独立子文档）"
    - type: DOC
      source: "funNLP/README.md, L31-39（双表格目录实现多栏导航）"
    - type: CODE
      source: "funNLP/（目录结构：仅 README.md + data/，无 docs/ 无 wiki/）"
  contrast: >
    标准开源项目通常用 GitHub Wiki 或 MkDocs 拆成多页，
    便于搜索和贡献。funNLP 不这样做是因为它的目标不是「协作项目」，
    而是「一个人的工具箱对外共享」——维护单一文件的成本远低于维护
    一个文档站，且 GitHub 的 anchor 跳转已经足够满足导航需求。

- why_id: W002
  type: selection
  claim: "把 LLM/ChatGPT 类资源独立成置顶区块，放在所有传统 NLP 资源之前"
  reasoning_chain: >
    README L31-33：最顶部的大号 :fire: 表情区块，专门列出「类ChatGPT的模型评测」
    「LLM训练推理」「提示工程」等 11 个类别 →
    该区块用 :fire: 标记，视觉权重明显高于下方的传统 NLP 分类表格 →
    而传统 NLP 目录（语料库、词库、预训练模型等）被放在后面的双栏表格里 →
    这不是内容重要性的判断，而是时效性的判断：
    LLM 浪潮使这部分资源时效性极强，用户查阅频率急剧上升 →
    置顶实现「热点资源快速访问」，传统资源仍保留但降低位置权重
  evidence:
    - type: DOC
      source: "funNLP/README.md, L31-33（:fire: 区块，11个LLM子类目）"
    - type: DOC
      source: "funNLP/README.md, L36-39（传统NLP目录用双栏表格，位置靠后）"
    - type: DOC
      source: "funNLP/README.md, L128-337（LLM区块内容远比传统分类条目密集）"
  contrast: >
    按字母顺序或「任务难度」排序是更中性的组织方式。
    funNLP 不这样做，因为它本质上是个人实用工具清单：
    「现在最需要什么」决定了排列顺序，而非「逻辑上哪个应该在前面」。
    时效性优先于分类严谨性。

- why_id: W003
  type: implementation
  claim: "thirtyw.py 用 Python 2 语法（print 语句）且过滤逻辑硬编码 len > 2，不做参数化"
  reasoning_chain: >
    thirtyw.py L11：`print temp_sublist[1]`（Python 2 print 语句，非函数）→
    thirtyw.py L8-9：解析逻辑直接 split(' ') 再 split('\t')，字段顺序硬编码 →
    thirtyw.py L9：过滤条件 `len(temp_sublist[1]) > 2` 是魔数，无注释解释 →
    这是一次性的数据清洗脚本，目的是把「30万词序列词典」转换成 jieba 可用格式 →
    脚本只需运行一次（输出 30wdict.txt 已存在于目录中）→
    因此没有任何工程化投入的动机：不需要重用性，不需要可维护性，
    写完即丢的脚本不值得参数化
  evidence:
    - type: CODE
      source: "funNLP/data/中文分词词库整理/thirtyw.py, L1-14（完整脚本，14行）"
    - type: CODE
      source: "funNLP/data/中文分词词库整理/（同目录有 30wdict.txt 输出结果，证明脚本已执行完毕）"
    - type: CODE
      source: "funNLP/data/中文分词词库整理/thirtyw.pyc（编译缓存存在，说明曾执行）"
  contrast: >
    生产级数据处理脚本会封装成 CLI 工具，参数化输入路径和过滤阈值，
    并用 Python 3 和 argparse。这里不这样做，因为脚本的生命周期
    就是「跑一次得到数据」，工程化的代价远大于收益。
    Python 2 的使用也暗示脚本写于 2018 年前后（Python 3 迁移窗口期前）。

- why_id: W004
  type: selection
  claim: "停用词目录同时收录四个版本（百度、哈工大、四川大学、通用），而非选一个推荐版本"
  reasoning_chain: >
    data/停用词/ 下有四个不同机构的停用词表，行数分别为：
    百度 1403 行、哈工大 766 行、四川大学 975 行、通用 745 行 →
    四个版本覆盖范围差异显著（百度版几乎是哈工大版的 2 倍）→
    项目没有提供「推荐使用哪个」的说明 →
    这体现了资源库的核心哲学：「提供工具，不教你怎么用」——
    停用词的选择依赖具体任务（情感分析 vs 信息检索对停用词敏感度不同）→
    强制推荐一个版本反而限制了使用者的选择
  evidence:
    - type: CODE
      source: "funNLP/data/停用词/（目录包含：百度停用词表.txt, 哈工大停用词表.txt, 四川大学停用词表.txt, 中文停用词库.txt）"
    - type: INFERENCE
      source: "四个文件行数对比：百度1403行 vs 哈工大766行，差异明显，无法合并为单一版本"
  contrast: >
    大多数 NLP 工具库（如 jieba）只内置一个停用词表，用户修改需要替换文件。
    funNLP 提供多版本是因为它定位为「资源库」而非「工具库」：
    不做工程决策，把选择权交给用户。代价是用户需要自己判断哪个更适合。

- why_id: W005
  type: architecture
  claim: "词库文件直接以原始 .txt 格式存储，而非打包成 Python 包或提供 API"
  reasoning_chain: >
    data/ 目录下的词库（医学 18749 行、法律词库、古诗词库等）
    全部以纯文本 .txt 存储，无索引、无元数据、无包装代码 →
    项目只有一个 14 行的处理脚本，没有提供任何查询接口 →
    .txt 格式可以被任何语言直接读取，不依赖特定运行时 →
    这降低了使用门槛：不需要安装 Python 包，不需要理解 API，
    git clone 后即可直接使用 →
    同时 .txt 也是 grep/awk 等文本工具的天然格式，
    与中文 NLP 工具链（jieba 的用户词典也是 .txt）高度兼容
  evidence:
    - type: CODE
      source: "funNLP/data/医学词库/THUOCL_medical.txt（18749行纯文本，格式：词语\t频率）"
    - type: CODE
      source: "funNLP/data/同义词库、反义词库、否定词库/同义词库.txt（17817行纯文本）"
    - type: CODE
      source: "funNLP/data/拆字词库/chaizi-jt.txt（字符\t拆分方式，纯文本格式）"
    - type: INFERENCE
      source: "整个 data/ 目录无 __init__.py，无 setup.py，无任何包管理文件"
  contrast: >
    NLTK、spaCy 等工具将数据打包为带索引的二进制格式或 Python 包。
    funNLP 不这样做是因为它不是一个库，是一个「数据仓库」。
    打包反而增加维护负担，且 .txt 的通用性满足了最广泛的用户群。

- why_id: W006
  type: negation
  claim: "没有构建任何搜索/过滤功能，用户只能通过浏览器 Ctrl+F 或 GitHub 内置搜索"
  reasoning_chain: >
    README 有 1056 行，包含数百个资源条目，无搜索框、无标签系统、无过滤器 →
    目录仅靠 anchor 跳转到分类标题，分类内部无二级索引 →
    页面最底部有一个被注释掉的超长 `<!-- 备注 -->` 块（L1031-1033），
    内容是所有词条的纯文本列表——这是作者给搜索引擎爬虫准备的 SEO 文本，
    而非给用户看的 →
    这说明作者意识到可发现性问题，但选择用 SEO 而非搜索 UI 来解决 →
    为什么不做搜索：维护一个搜索 UI 需要持续成本，
    而 GitHub 原生的 Ctrl+F 和代码搜索对目标用户（开发者）已经足够
  evidence:
    - type: DOC
      source: "funNLP/README.md, L1031-1033（注释掉的长备注块，包含所有词条的SEO文本）"
    - type: DOC
      source: "funNLP/README.md, L31-39（目录只有 anchor 跳转，无搜索）"
    - type: INFERENCE
      source: "整个仓库无任何 JavaScript、无 GitHub Pages 配置，排除了动态搜索的可能"
  contrast: >
    awesome-* 系列的一些仓库会部署 algolia 搜索或 GitHub Pages 站点。
    funNLP 不这样做，因为这会把一个「个人工具箱」变成一个需要运维的产品，
    增加维护复杂度。SEO 注释块是一个零成本的替代方案。

- why_id: W007
  type: selection
  claim: "古诗词库按情感/主题分成 30+ 个子文件（farewell.txt, homesick.txt 等），而非合并为单个文件"
  reasoning_chain: >
    data/古诗词库/ 包含 30 个按主题分类的 .txt 文件
    （bird, boudoirripinings, farewell, friendship, love, moon 等）→
    每个文件按诗歌情感主题分类，而非按朝代、作者、体裁分类 →
    情感分类是 NLP 任务中最常见的使用场景（情感分析语料、文本生成条件控制）→
    如果合并为单文件，用户需要自己做主题过滤才能得到特定情感的诗歌子集 →
    预分类直接降低了「拿来就用」的成本
  evidence:
    - type: CODE
      source: "funNLP/data/古诗词库/（目录结构：bird.txt, farewell.txt, homesick.txt, love.txt, moon.txt 等30+文件）"
    - type: CODE
      source: "funNLP/data/古诗词库/tangshi.txt（唐诗合集 298 行，与主题文件并存）"
  contrast: >
    按朝代（唐/宋/元）或按体裁（律诗/词）分类是更学术的做法。
    按情感分类是工程导向的选择：NLP 实践者需要「给定情感条件的诗歌样本」，
    而不是「给定朝代的诗歌样本」。这个分类决策暗示了主要用户群体的使用姿势。

- why_id: W008
  type: constraint
  claim: "中文谣言数据集内置了完整的学术引用格式（BibTeX），而词库数据没有"
  reasoning_chain: >
    data/中文谣言数据/README.md 包含完整的中英文 BibTeX 引用格式，
    指向清华大学刘知远团队的论文 →
    而 data/医学词库/、data/法律词库/ 等目录只有数据文件，无引用说明 →
    区别在于：谣言数据集来自一篇已发表的学术论文（需要被引用才能被正当使用），
    而词库来自开放的 THU 语言技术平台（THUOCL），用户无需引用 →
    BibTeX 的存在是因为学术合规要求，而非作者的内容偏好
  evidence:
    - type: DOC
      source: "funNLP/data/中文谣言数据/README.md, L22-50（完整BibTeX格式，中英文双版本）"
    - type: CODE
      source: "funNLP/data/医学词库/THUOCL_medical.txt（无任何引用说明，仅有数据）"
    - type: CODE
      source: "funNLP/data/法律词库/THUOCL_law.txt（无任何引用说明，仅有数据）"
  contrast: >
    如果完全不要求引用，谣言数据集只需放 .json 文件即可。
    BibTeX 的出现是对原始数据协议的遵守（研究数据集通常要求引用论文），
    而不是对所有数据一视同仁的处理方式。
    这也反映了仓库内数据来源的异质性：部分是研究产出，部分是工程产物。
```

---

## 元分析：funNLP 的核心设计逻辑

funNLP 最突出的设计哲学是**零工程化的最大覆盖**：用最少的维护成本，覆盖最多的用户需求。

具体表现为：
1. 单文件架构（W001）—— 避免文档站维护成本
2. 原始 .txt 格式（W005）—— 避免 API 维护成本
3. 无搜索功能（W006）—— 避免动态功能维护成本
4. 一次性脚本（W003）—— 避免代码复用设计成本

这一切都指向同一个约束：**这是一个个人项目，维护者只有一个人，时间是稀缺资源**。
所有「不做」的决策都是在降低持续维护的负担，而非技术能力限制。

另一条线索是**用户导向的分类**（W004, W007）：
停用词提供多版本而非推荐一个，古诗按情感而非朝代分类——
这些都是「把选择权给用户」的体现，与项目名「乐园」（playground）的定位一致。
