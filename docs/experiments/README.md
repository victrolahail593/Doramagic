# Experiments

本目录用于承载 AllInOne 的正式实验资产，目标是把“研究判断”转换为“可重复验证的实验记录”。

## 目录职责

- `exp01-minimal-pipeline-report.md`：最小灵魂提取闭环验证的主实验文档
- `exp01-repo-selection-guide.md`：`exp01` 的候选验证仓库筛选指南与首批推荐样本
- `templates/`：问题集、评分标准、运行记录、仓库评分卡等可复用模板
- `runs/`：每次实验执行后的记录副本或结果文档
- `artifacts/`：中间产物、截图、卡片样例、导出上下文等辅助证据

## 命名约定

- `exp01`：第一次正式实验，目标是验证“灵魂提取是否有用”
- 后续实验沿用 `exp02`、`exp03` 命名
- 每个实验主文档应同时包含：实验设计、执行结果、结论与后续动作

## 当前实验策略

当前阶段优先：

1. 小型真实仓库
2. 代码半魂优先
3. A/B 对比验证
4. 记录成本、耗时、失败点和人工修正点
5. 用明确的仓库筛选方法决定首个验证样本

当前阶段暂不优先：

- 大仓库处理
- 社区半魂全量采集
- 图数据库 / 向量数据库
- 深度平台化建设

## 当前默认样本路线

根据 `exp01-repo-selection-guide.md`，当前默认首个验证仓库为：

- **Primary**：`python-dotenv/python-dotenv`
- **Secondary**：`jpadilla/pyjwt`、`pallets/itsdangerous`
- **Stretch**：`psf/requests`

## 使用方式

1. 先阅读 `exp01-repo-selection-guide.md`，确认首个验证仓库
2. 填写 `templates/exp01-repo-scorecard-template.md`（如需比较多个候选）
3. 复制并填写问题集、Judge Rubric 和 Run Log 模板
4. 在主实验文档中记录设计与结论
5. 将每次实际执行的运行记录或结果放入 `runs/`
6. 将中间产物、截图、导出文件等放入 `artifacts/`
