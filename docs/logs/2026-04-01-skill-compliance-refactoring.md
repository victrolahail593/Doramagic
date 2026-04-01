# 2026-04-01 Skill 合规改造 — pip 包架构

## 概述

将 Doramagic skill 包从 215 文件 / 5.6MB 的臃肿包，改造为 12 文件 / 96KB 的薄壳 + pip 包后端，达到 OpenClaw 规范（≤15 文件 / <12MB / SKILL.md ≤80 行）。

## 改造前后对比

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 文件数 | 215 | 12 |
| 大小 | 5.6MB | 96KB |
| SKILL.md 行数 | 80 | 69 |
| Python 代码分发 | 手动 rsync 副本 | pip install |
| 知识文件 | 物理副本 | package_data |
| 子 Skill | 4 个 SKILL-*.md | 1 个 + references/ |

## 关键决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 包命名空间 | 保持扁平 doramagic_* | 零 import 改动 |
| 分发方式 | Git URL (kind: uv) | 利用现有 GitHub 发布流 |
| 知识文件 | pip package_data | ~5MB，importlib.resources 定位 |
| 子 Skill | 保留 extract，其余合并 | 只保留用户直接调用的 |

## 主要代码变更

1. **pyproject.toml** — hatchling 打包 12 个 doramagic_* 包 + knowledge force-include + CLI 入口 + 版本 13.1.0
2. **doramagic_product/cli.py** — 新建 CLI 入口点，`doramagic` 命令
3. **flow_controller.py** — Path(__file__).parents[2] 硬编码 → 标准 import
4. **runtime_paths.py** — 添加 importlib.resources fallback 定位 bricks
5. **doramagic_product/__init__.py** — 改为 lazy import 避免 pipeline.py 断裂依赖
6. **SKILL.md** — 重写 frontmatter，声明 metadata.openclaw.install
7. **skills/doramagic/** — 删除 packages/ 副本、knowledge/ 副本、多余 scripts，合并子 Skill

## 代码审查发现（3 轮并行审查）

| 严重性 | 数量 | 关键问题 |
|--------|------|----------|
| CRITICAL | 1 | os.fork() 在 Windows 崩溃 → 已修复 |
| HIGH | 4 | 版本不一致、缺少 LLM 依赖、exec 声明、fork 子进程泄漏 → 全部已修复 |
| MEDIUM | 4 | run_id 路径遍历、editable install、shell 转义、brick_catalog_dir → 部分修复 |

## 踩坑

- hatchling 多路径 packages 的 editable install 不支持 → 只能用 wheel install
- doramagic_product.__init__ 在模块级 import pipeline.py 导致整个包 import 失败 → lazy import 解决
- flow_controller.py 用 Path 相对路径加载 brick_stitcher → pip install 后路径断裂 → 改标准 import
- pyproject.toml 版本忘记和 SKILL.md 同步 → 代码审查发现

## 下一步

1. 知识库 V1/V2 格式统一（已记录到 TODOS.md P2）
2. 发布 v13.1.0 到 GitHub + ClawHub
3. OpenClaw 实际安装验证
