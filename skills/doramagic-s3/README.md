# Doramagic S3 (V2: 全量研究集成)

本目录包含了 Doramagic Skill 的最终集成形态。我们成功将 8 项顶尖研究成果落地，构建了一个能够在复杂开源环境中提取高质量知识的智能体流程。

## 核心特性集成

1. **WHY 可恢复性判断**: `validate_skill.py` 强制检查 WHY 证据的充分性，拒绝凭空编造设计哲学。
2. **Deceptive Source Detection (暗雷检测)**: `SKILL.md` 内置了 8 项暗雷指标，`LIMITATIONS.md` 中强制呈现暗雷评估结果。
3. **暗雷叠加效应**: AI 被指引在叠加 2+ 暗雷时标记项目为高危。
4. **Soul Extractor Stage 1-4**: `SKILL.md` 完整集成了从广度扫描到规则提取的 4 个阶段，要求 AI 读取 `STAGE-*.md` 框架。
5. **5 类知识卡片体系**: 抽取结果沉淀为结构化的 `cards/` (概念、工作流、决策、陷阱、特征)，最终由脚本编译为文档。
6. **跨项目综合**: 要求至少下载 2 个项目，通过对比寻找共识、冲突。
7. **社区信号采集**: 提供 `scripts/community_signals.py`，从 GitHub Issues 自动提取痛点，作为 UNSAID 的基础。
8. **预提取 API 集成**: `SKILL.md` 的 Phase A 优先尝试请求领域知识库 API（Domain Bricks）进行预热。

## 验证结果 (WiFi Password Manager)
- **搜索与下载**: 成功调取 GitHub API 检索并下载了 `Khh-vu/wifi-password-manager` 与 `muelli/network-manager-qrcode` 两个仓库。
- **事实与信号**: 使用 `extract_facts.py` 抽取代码结构，使用 `community_signals.py` 获取社区讨论（如密码截断、SSID 误配）。
- **知识卡片**: 成功提炼 3 个概念卡、2 个决策卡、2 个陷阱卡，验证了结构化提取的可行性。
- **质量门控**: `runs/wifi-run/` 下的合成文档成功通过 `validate_skill.py`，确保了来源追溯（PROVENANCE）与局限声明（LIMITATIONS）合规。

## 目录结构
- `SKILL.md`: 主流程指令。
- `scripts/`: 工具链。
- `cards/`: 结构化知识碎片。
- `runs/wifi-run/`: 验证输出成果。
