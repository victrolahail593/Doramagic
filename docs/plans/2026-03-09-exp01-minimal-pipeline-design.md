# AllInOne exp01 最小灵魂提取实验设计

**日期**：2026-03-09
**目标受众**：技术负责人 / 架构师 / 执行实验的工程人员
**文档类型**：实验设计文档

---

## 1. 实验定位

`exp01` 不是产品功能开发任务，而是 AllInOne 的第一次正式工程验证。它的目标不是“把 AllInOne 做完”，而是验证以下核心命题是否成立：

1. 针对一个小型真实仓库，能否提取出结构化的“灵魂资产”；
2. 将这些灵魂资产装配进 LLM 上下文后，回答质量是否比无灵魂基线更好；
3. 这个过程的成本、耗时、失败点是否在可接受范围内。

## 2. 设计原则

- 先验证价值，再扩展架构
- 先代码半魂，再考虑社区半魂
- 先小仓库，再大仓库
- 先标准化记录方式，再写更多提取代码
- 先用最小文件骨架固定实验方法，再逐步填写执行结果

## 3. 交付形式

本次交付不是实验结果，而是实验的“落地骨架版”，包括：

- 主实验文档：`docs/experiments/exp01-minimal-pipeline-report.md`
- 实验目录说明：`docs/experiments/README.md`
- 问题集模板：`docs/experiments/templates/exp01-question-set-template.md`
- 评估标准模板：`docs/experiments/templates/exp01-judge-rubric.md`
- 运行记录模板：`docs/experiments/templates/exp01-run-log-template.md`
- 结果目录：`docs/experiments/runs/`
- 产物目录：`docs/experiments/artifacts/`

## 4. 主实验文档结构

主文档应同时承担“实验方案”和“实验报告”的作用，结构建议如下：

1. 实验目标
2. 核心假设
3. 成功标准与失败标准
4. 范围与非目标
5. 验证仓库选择标准
6. 实验输入与输出
7. 最小实验流程
8. 问题集设计
9. A/B 评估方法
10. 记录字段
11. 风险与偏差控制
12. 执行结果（预留）
13. 结论与下一步（预留）

## 5. 模板职责设计

### 5.1 问题集模板
用于统一 A/B 实验问题的组织方式，至少覆盖：
- 领域概念理解
- 工作流理解
- 规则/边界条件
- 风险/坑点识别
- 方案建议/迁移建议

### 5.2 Judge Rubric 模板
用于统一对回答进行离散维度评价，重点包含：
- Groundedness
- Specificity
- Usefulness
- Risk
- Uncertainty Handling

### 5.3 Run Log 模板
用于记录单次实验运行事实，包括：
- 目标仓库
- 模型/版本
- 上下文模式
- 灵魂卡片列表
- token / latency / cost
- 异常与人工修正
- 结果路径

## 6. 目录结构设计

```text
docs/experiments/
├── README.md
├── exp01-minimal-pipeline-report.md
├── templates/
│   ├── exp01-question-set-template.md
│   ├── exp01-judge-rubric.md
│   └── exp01-run-log-template.md
├── runs/
└── artifacts/
```

## 7. 当前不做的事情

为防止实验前置过重，本次骨架明确不包含：

- 实际执行脚本
- provider 绑定实现
- 数据库存储设计
- 向量索引设计
- MCP Server 实现
- DeepWiki 集成
- 社区半魂采集实现

## 8. 预期作用

本骨架完成后，AllInOne 将首次具备：

- 统一的实验记录方式
- 可复用的问题集与评分标准
- 可持续追加的实验目录结构
- 从“继续讨论”转向“开始实验”的执行入口

