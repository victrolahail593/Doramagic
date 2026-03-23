# WHY 提取报告：funNLP（Gemini）

> 项目：funNLP（NLP民工的乐园）
> 类型：中文NLP资源汇总库
> 提取日期：2026-03-13
> 提取模型：Gemini

---

```yaml
- why_id: W001
  type: architecture
  claim: "采用'以目录为索引'的扁平化资源仓库架构，而非构建统一的代码库或库文件。"
  reasoning_chain: "项目目标是成为'武器库'（Weapon Arsenal） → 资源种类极其繁杂（从词库到LLM资料） → 统一抽象 API 的开发成本过高且不灵活 → 选择以文件系统（目录）作为天然的分类器。"
  evidence:
    - type: DOC
      source: "README.md: '幾乎最全的中文NLP資源庫'，以及庞大的目录分类表"
    - type: INFERENCE
      source: "目录结构显示存在几十个独立的 data 子文件夹，每个文件夹对应一个垂直领域"
  contrast: "对比 NLTK 或 spaCy 等代码库，后者通过代码逻辑组织资源，而 funNLP 通过文件系统组织资源，极大降低了贡献和查找的门槛。"

- why_id: W002
  type: implementation
  claim: "使用极其原始的（Minimalist）脚本进行数据预处理，优先考虑可读性和执行速度而非工程化。"
  reasoning_chain: "数据清理是'一次性'或'低频'任务 → 不需要复杂的类封装或依赖管理 → 编写简单的过程式脚本直接处理文本文件 → 降低了'民工'（初级开发者）阅读和修改的负担。"
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py: 使用最基础的 open(), split() 和 print，无任何外部库依赖"
  contrast: "不使用 Pandas 或专门的 ETL 框架，避免了环境配置的复杂性，确保任何环境下只要有 Python 就能运行。"

- why_id: W003
  type: constraint
  claim: "数据存储优先采用纯文本（Plain Text）格式，以保证最大的兼容性和透明度。"
  reasoning_chain: "NLP 任务的输入输出多为文本 → 专有二进制格式（如 Pickle/HDF5）虽然读取快但不可见且易碎 → 选择 .txt/MD 格式 → 方便用户直接用 grep/cat 或文本编辑器快速预览。"
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py: 读写均为 .txt 结尾的文件"
    - type: INFERENCE
      source: "目录中包含大量词库文件夹，通常此类项目内部均为 txt 或 csv 格式"
  contrast: "不使用数据库（如 SQLite）存储词库，牺牲了检索性能，但换取了跨平台和'零安装'的易用性。"

- why_id: W004
  type: selection
  claim: "按业务领域（Vertical Domains）而非技术栈对数据进行物理切分。"
  reasoning_chain: "NLP 开发者通常是带着具体业务问题（如法律、医学）找资源 → 按'分词'、'聚类'等技术分类会导致相关资源散落在各处 → 按领域建模（data/法律词库, data/医学词库） → 符合'民工'按需搜索的直觉。"
  evidence:
    - type: DOC
      source: "目录结构: data/职业词库, data/法律词库, data/财经词库 等"
  contrast: "许多 NLP 教程按 'Tokenization', 'Embedding', 'Parsing' 分类，这在教学上正确但在生产找资源时低效。"

- why_id: W005
  type: negation
  claim: "刻意不提供统一的入口函数或 Python 包安装方式（__init__.py 的缺失）。"
  reasoning_chain: "提供 pip install 会产生版本维护负担 → 资源库的核心价值在内容而非代码逻辑 → 鼓励用户通过 git clone 或直接下载特定文件来使用 → 保持了仓库作为'资料库'的纯粹性。"
  evidence:
    - type: INFERENCE
      source: "根目录下没有 setup.py，子目录下多为独立的脚本，缺乏包结构的初始化文件"
  contrast: "对比那些试图将所有词库封装进一个 Python package 的项目，funNLP 避免了因为某个词库更新导致整个包体积过大的问题。"

- why_id: W006
  type: implementation
  claim: "保留对旧版本环境（如 Python 2）的兼容或习惯，反映了实用主义至上的原则。"
  reasoning_chain: "许多工业界存量系统仍运行在老旧环境 → 编写不依赖 Python 3 特性的简单代码 → 确保代码在任何年代的服务器上都能直接跑通。"
  evidence:
    - type: CODE
      source: "data/中文分词词库整理/thirtyw.py: 即使在 2026 年（或近期更新），代码仍使用 print 语句而非函数，显示出极强的向后兼容性或对简单语法的偏好。"
  contrast: "不追求现代 Python 的语法糖（如 Type Hints, async），专注于'跑通并拿到结果'。"
```
