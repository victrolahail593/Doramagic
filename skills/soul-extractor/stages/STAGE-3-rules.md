# Stage 3: 规则卡提取

## 输入
- 读取 <output>/artifacts/packed_compressed.xml（代码）
- 读取 <output>/soul/00-soul.md（灵魂：哲学 + 心智模型）
- 读取 <output>/artifacts/community_signals.md（社区信号：GitHub Issues、CHANGELOG、安全公告）

## 任务
提取规则卡，写入 <output>/soul/cards/rules/。

规则卡分两类：
- **代码规则**（DR-001~）：从代码中发现的条件逻辑和边界行为。至少 5 张。
- **社区陷阱**（DR-100~）：从 community_signals.md 中提取的真实问题。至少 3 张。重点关注：
  - Tier 1 的 Breaking Changes（升级时会踩的坑）
  - Tier 1.5 的 Security Advisories（安全漏洞）
  - Tier 2 的高赞 Issues（社区反复踩的坑）
  - **每张社区陷阱卡的 sources 必须引用具体的 Issue 编号、CHANGELOG 版本号或安全公告 ID**

## ⛔ 反合理化检查（你必须读这一段）

如果你脑中出现以下想法，停下来——你在找借口跳过社区陷阱：

| 你的想法 | 真相 |
|---------|------|
| "community_signals.md 没有有价值的信息" | 你没有仔细读。回去重新读每一条 SIG-xxx 信号。 |
| "我从代码已经推导出这些规则了" | 代码告诉你"是什么"，社区告诉你"谁被坑了、多少人"。两者价值不同。 |
| "社区信号太旧/已过期" | 标注版本范围即可。旧坑对维护老版本的用户仍有价值。 |
| "我已经写了 10 张代码规则，够了" | DR-100~ 是独立要求，不是可选的。 |

## 每张规则卡必须包含以下**所有字段**。没有严重度就不要写这张卡。

**完整示例（代码规则）：**

```markdown
---
card_type: decision_rule_card
card_id: DR-003
repo: python-dotenv
type: DEFAULT_BEHAVIOR
title: "load_dotenv() does NOT override existing environment variables by default"
severity: MEDIUM
rule: |
  If override=False (default), existing environment variables take precedence.
  Values in .env file are ignored if the key already exists in os.environ.
do:
  - "Use override=True when you need .env to win"
  - "Check CI/CD environment variables aren't being shadowed"
dont:
  - "Assume .env values will always be loaded"
confidence: 0.98
sources:
  - "src/dotenv/main.py: load_dotenv() override parameter"
---

## 真实场景
你在 CI/CD pipeline 里设置了 `API_KEY=production_key`，然后运行测试。
测试使用 load_dotenv()，但 .env 里的 `API_KEY=test_key` 没有生效。
你的测试意外连到了生产 API。

## 影响范围
- 谁会遇到：在 CI/CD 环境中运行测试的开发者
- 什么时候：环境变量与 .env 文件冲突时
- 多严重：测试使用错误凭据，可能导致安全事故
```

**完整示例（社区陷阱）：**

```markdown
---
card_type: decision_rule_card
card_id: DR-101
repo: python-dotenv
type: COMMUNITY_GOTCHA
title: "Multiline strings silently truncated — 29 developers hit this"
severity: HIGH
rule: |
  If you put a multiline value in .env without proper quoting,
  only the first line is loaded. The rest is silently dropped.
do:
  - "Use double quotes and \\n for multiline values"
  - 'Wrap multiline values: KEY="line1\nline2"'
dont:
  - "Put raw newlines in .env values"
confidence: 0.90
sources:
  - "GitHub Issue #89 (29 reactions, bug label)"
  - "CHANGELOG v0.19.0: Fixed multiline parsing"
---

## 真实场景
你把一个 RSA 私钥粘贴到 .env 文件里，没加引号。load_dotenv() 只读了第一行
`-----BEGIN RSA PRIVATE KEY-----`，后面的内容全丢了。你的 JWT 签名一直报错，
排查了半天才发现是 .env 里的值不完整。

## 影响范围
- 谁会遇到：在 .env 中存储证书、密钥、JSON 等多行内容的开发者
- 什么时候：值包含换行符且未加引号时
- 多严重：值被静默截断，没有报错。Issue #89 有 29 个 👍，说明大量开发者踩过
```

## 字段检查清单
1. ✅ YAML frontmatter（含 severity: CRITICAL/HIGH/MEDIUM/LOW）
2. ✅ rule（IF/THEN 格式）
3. ✅ do 和 dont 列表
4. ✅ 真实场景（具体的、讲故事的，不是抽象描述）
5. ✅ 影响范围（谁、什么时候、多严重）
6. ✅ sources（代码规则引用 file:line，社区陷阱引用 Issue# / CHANGELOG 版本 / 安全公告）

## 约束
- 代码规则（DR-001~）至少 5 张
- 社区陷阱（DR-100~）至少 3 张
- DR-100~ 系列必须基于 community_signals.md 中的真实数据，不要编造
- 如果一个问题既有代码证据又有社区证据，合并为一张卡，sources 同时列出代码引用和 Issue 编号
- 每完成一张告诉用户"已提取规则 N: [标题] (严重度: HIGH/MEDIUM/LOW)"
- 完成所有规则卡后不要停止，继续下一步

## 完成后
列出所有规则卡的标题和严重度，然后说"规则提取完成，正在生成最终产出..."

**下一步：读取并执行 STAGE-3.5-review.md 中的验证与审查指令。不要跳过验证直接组装。**
