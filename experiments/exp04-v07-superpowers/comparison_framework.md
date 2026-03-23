# v0.6 vs v0.7 横向对比框架

> 目标项目：obra/superpowers
> 日期：2026-03-09

## 对比设计

### 控制变量
- 同一目标项目（obra/superpowers）
- 同一模型（远程 OpenClaw 默认模型 MiniMax-M2.5）
- 同一 prepare-repo.sh（代码打包 + 社区信号采集不变）

### 实验变量
- v0.6：Stage 1 → 2 → 3 → 4（无验证）
- v0.7：Stage 1 → 2 → 3 → **3.5** → 4（有验证+审查）

## 对比维度

| # | 维度 | 数据来源 | v0.6 基线 | v0.7 结果 |
|---|------|---------|----------|----------|
| 1 | 卡片总数 | ls cards/ | 14 | |
| 2 | 格式合规率 | validation_report.json | 100% | |
| 3 | 引用 warnings | validation_summary.md | 1 | |
| 4 | 代码规则数 | DR-00x count | 5 | |
| 5 | 社区陷阱数 | DR-10x count | 3 | |
| 6 | 社区信号利用率 | validation metrics | 60% | |
| 7 | 内容质量（具体性） | 人工对比 | 未审查 | |
| 8 | 内容质量（真实性） | 人工对比 | 未审查 | |
| 9 | .cursorrules 差异 | diff | 基线 | |

## v0.6 基线数据

### 验证报告（追溯运行）
- 总卡片：14（3 CC + 3 WF + 5 DR + 3 DR-10x）
- 格式合规：14/14 pass
- Errors：0
- Warnings：1（DR-001 引用 `skills/using-superpowers/SK-20ILL.md` 不存在）
- 社区信号利用率：60%（3/5 signals used）

### 产出路径
- `experiments/exp03-v06-superpowers/superpowers/`

## v0.7 实验数据

### 产出路径
- `experiments/exp04-v07-superpowers/superpowers/`

### 验证报告
（待填写）

### 软审查结果
（待填写）

## 结论
（待填写）
