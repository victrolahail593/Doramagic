# Soul Extractor 改进研究计划

## 研究目标
以 agent 技术专家 + 用户双重视角，对 soul-extractor skill 进行全面评审，提出改进建议。

## 研究日期: 2026-03-10

## 研究模块拆分

### 模块 1：流程编排研究
- 目标：评审 6 阶段流程设计是否合理
- 研究点：阶段依赖、并行可能性、失败恢复、中断续跑
- 产出：`01-workflow-orchestration.md`

### 模块 2：工具调用研究
- 目标：评审 prepare-repo.sh、validate_extraction.py、assemble-output.sh 脚本设计
- 研究点：错误处理、跨平台兼容、依赖管理、输出规范
- 产出：`02-tool-invocation.md`

### 模块 3：提示词研究
- 目标：评审各 Stage 的 prompt 设计
- 研究点：约束有效性、反合理化检查、输出质量控制
- 产出：`03-prompt-engineering.md`

### 模块 4：鲁棒性研究
- 目标：评审边界情况和错误处理
- 研究点：大仓库处理、无社区信号、重复提取、验证失败
- 产出：`04-robustness.md`

### 模块 5：用户反馈研究
- 目标：收集社区对 soul-extractor 的真实使用反馈
- 研究点：GitHub Issues、用户评价、常见问题
- 产出：`05-community-feedback.md`

### 模块 6：竞品与最佳实践研究
- 目标：调研类似的 knowledge extraction 工具和方法论
- 研究点：repomix、gptme、其他 skill 提取工具
- 产出：`06-competitor-analysis.md`

## 执行策略
- 并行 spawn 6 个子代理
- 每个子代理独立研究并产出报告
- 主代理负责整合和最终评审

## 报告规范
- 文件名：`XX-module-name.md`
- 头部包含：研究日期 | 模型 | 研究目标
- 结构：现状分析 → 问题识别 → 改进建议 → 优先级排序
