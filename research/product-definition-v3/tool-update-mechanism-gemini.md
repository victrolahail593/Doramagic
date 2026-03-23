# Doramagic 道具更新机制：从"静态交付"到"动态进化"

## 1. 推荐的整体更新架构：基于元数据的"影子锻造" (Shadow Forge)

**核心设计原则：影子锻造 (Shadow Forge)**

Doramagic 不应采用传统的 "下载更新" 模式，而应采用 **"重新锻造"** 模式。每个生成的道具内部都带有一份**"出生证明" (Metadata)**。Doramagic 作为母体 Skill，周期性地扫描用户 workspace 中的道具元数据。当发现母体的引擎、积木或编译逻辑有重大版本跳跃时，在后台启动一个"影子会话"，尝试用新引擎对旧道具进行重新锻造，并将差异推送到用户的待办任务中。

---

## 2. 元数据设计：道具出生证明 (Birth Certificate)

每个生成的道具在 `_meta.json` 或 `SKILL.md` 的 frontmatter 中必须包含以下**不可见元数据**：

```json
{
  "doramagic_origin": {
    "tool_id": "stock-tracker-2026-abc",
    "forge_timestamp": "2026-03-12T10:00:00Z",
    "engine_version": "v3.0.5",
    "compiler_version": "v1.2.0",
    "bricks_used": [
      {"id": "django-core", "version": "v1.0.2"},
      {"id": "akshare-mcp", "version": "v0.8.0"}
    ],
    "source_mapping": {
      "repo": "https://github.com/pythoneer/akshare",
      "commit": "a1b2c3d4",
      "user_intent_snapshot": "帮我做一个能追踪 A 股行情的东西"
    },
    "customization_hash": "h123456" // 用于检测用户是否手动修改过道具内容
  }
}
```

*   **作用**：让 Doramagic 知道这个孩子是谁、怎么生出来的、用了什么原材料、出生时的环境如何。

---

## 3. 触发与执行策略

### 3.1 触发机制：静默巡检与按需提醒
*   **静默巡检**：当用户触发 Doramagic (/dora) 时，Doramagic 自动扫描 workspace。
*   **版本差异计算**：
    *   `New Engine > Old Engine` (如增加了置信度举证系统)
    *   `New Brick > Old Brick` (如 Django 积木增加了对 5.1 版本的支持)
    *   `Source Updated` (监测到 GitHub 仓库有重大更新)
*   **触发阈值**：只有当更新预估能带来 **"显著体验提升"** (通过预演 Agent 评估) 时，才向用户发出提醒。

### 3.2 执行策略：增量进化 (Incremental Evolution)
1.  **读取 MEMORY.md**：首先读取道具在运行过程中积累的用户偏好。
2.  **影子提取**：使用新引擎对原始 source 重新提取。
3.  **知识合并 (Merge)**：
    *   `Core Knowledge`：用新提取的覆盖旧的。
    *   `User Personalization`：保留 MEMORY.md 中的用户设定。
    *   `Manual Edits`：如果 `customization_hash` 变化，提示用户存在手动修改，请求冲突解决。

---

## 4. 用户体验方案：哆啦A梦的"道具升级"

*   **视觉呈现**：Doramagic 在对话框中弹出一条轻量消息。
    > "Dora: 嘿！我学会了新的锻造法，你的 **'A股行情助手'** 可以升级得更聪明了。要不要试一下新版？"
*   **一键预览 (Side-by-Side)**：
    *   用户点击 "查看变化"，Dora 展示新旧对比。
    *   "旧版：只支持日线分析 | 新版：支持实时分钟级异动监控（基于新积木）"
*   **一键升级**：点击 "立即升级"，Doramagic 在后台完成覆盖安装。
*   **拒绝处理**：如果用户拒绝，Dora 记录 "用户偏好旧版"，并在未来 30 天内不再打扰，直到有更重大的版本更新。

---

## 5. 风险与回滚机制

### 5.1 回滚机制：快照保存
*   在执行升级前，Doramagic 自动将旧版 Skill 重命名为 `[tool-name]-v-old.bak`。
*   用户如果不满意，只需说："Dora，换回旧版的行情助手"，Dora 自动执行重命名恢复。

### 5.2 行为漂移风险
*   **风险**：新引擎生成的叙事风格不同，导致用户不习惯。
*   **缓解**：在元数据中记录旧版的 `tone_style` 偏好，并在新版锻造时作为约束条件输入。

---

## 6. 一句话总结

**Doramagic 通过"出生证明"追踪道具血脉，利用"影子锻造"在后台预演进化，最终以"哆啦A梦升级道具"的体感将技术红利无感地交付给用户。**
