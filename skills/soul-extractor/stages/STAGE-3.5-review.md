# Stage 3.5: 验证与硬阻断

## 前置条件
Stage 3 规则卡提取已完成。

## 步骤 1: 运行硬校验

运行验证脚本：

```bash
python3 {baseDir}/scripts/validate_extraction.py --output-dir "<output>"
```

### 如果 RESULT: PASS
继续下一步。

### 如果 RESULT: BLOCKED（第一次）

1. 读取 `<output>/soul/structured_feedback.json`
2. 逐条修复：
   - rule 缺条件语句 → 改写 rule 为 IF/THEN 格式
   - CRITICAL/HIGH 缺代码示例 → 在 do 列表中添加具体命令或代码（用反引号包裹）
   - 社区卡缺 Issue 引用 → 核实 community_signals.md 补上 Issue #
   - 其他格式错误 → 按错误信息修复对应卡片文件
3. 修复后**重新运行验证脚本**

### 如果 RESULT: BLOCKED（第二次）

1. 再次读取 structured_feedback.json
2. 修复剩余问题
3. 重新运行验证脚本

### 如果 RESULT: BLOCKED（第三次）

停止。告诉用户："验证 3 次未通过，剩余问题：[列出错误]。请人工检查规则卡后重试。"
不要继续后续阶段。

## ⛔ Hard Gate
- 验证必须 RESULT: PASS 才能继续
- 最多重试 2 次（共最多运行 3 次脚本）
- 第三次仍失败则终止流程，不继续 Stage 4

## 完成后
告诉用户："验证通过，X/Y 张卡片合格。正在合成专家叙事..."

**下一步：读取并执行 STAGE-4-synthesis.md 中的专家叙事合成指令。**
