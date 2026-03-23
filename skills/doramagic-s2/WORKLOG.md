# Doramagic S2 工作日志

日期：2026-03-20
负责人：S2-Codex
任务：按 `docs/supplementary-dev-brief.md` 将 Doramagic 从 CLI 形态补充开发为 OpenClaw Skill，并完成真实数据验证。

## 本次完成项

1. 创建产品主入口 [SKILL.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/SKILL.md)
   - 以 OpenClaw Skill 形态重写 Doramagic 主入口
   - 明确 Phase A-H
   - 明确 AI 自身智能与 `exec` 脚本职责边界
   - 明确输出必须包含 `WHY` 和 `UNSAID`

2. 创建脚本目录 [scripts/](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts)
   - [extract_facts.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/extract_facts.py)
     - 包装现有 `packages/extraction/doramagic_extraction/stage0.py`
     - 生成 repo facts、top-level entries、focus files、README 摘要、license files
     - 修复了 Pydantic v2 `dict()` 警告
     - 补充了 Android/Gradle 仓库的 focus file 检测
   - [validate_skill.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/validate_skill.py)
     - 包装现有 `packages/platform_openclaw/doramagic_platform_openclaw/validator.py`
     - 支持读取 `need_profile.json` 和 `synthesis_report.json`
     - 修复了 Pydantic v2 `json()` 序列化兼容问题
   - [assemble_output.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/assemble_output.py)
     - 从 `assembly-context.json` 组装 `SKILL.md`、`PROVENANCE.md`、`LIMITATIONS.md`
     - 同时落盘 `need_profile.json`、`synthesis_report.json`、`bundle_manifest.json`

3. 创建安装说明 [README.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/README.md)
   - 说明本地使用方式
   - 说明 OpenClaw 安装建议
   - 说明运行目录和脚本职责

## 真实验证过程

验证输入：
- `/dora 我想做一个管理家庭菜谱的 skill`

真实搜索与下载：
- 复用 [github_search.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic/scripts/github_search.py) 直连 GitHub API
- 搜索到并下载了真实项目：
  - `mealie-recipes/mealie`
  - `TheSpaceOfRiri/My.Chef`

真实代码与社区分析依据：
- `mealie`：README、`mealie/app.py`、`mealie/core/settings/settings.py`、`mealie/db/init_db.py`
- `My.Chef`：`PantryManager.java`、`MainActivity.java`、`RecipeSuggestionsActivity.java`、`PantryActivity.java`、`AndroidManifest.xml`
- 社区信号：真实抓取 `mealie` 的 GitHub issues，提取导入、权限、翻译 seed、解析器边界等问题

真实产物目录：
- [run output](/Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output)
- [生成的 SKILL.md](/Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/SKILL.md)
- [生成的 PROVENANCE.md](/Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/PROVENANCE.md)
- [生成的 LIMITATIONS.md](/Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/LIMITATIONS.md)

验证结论：
- 已真实调 GitHub API
- 已真实下载和分析仓库
- 最终输出明确包含 `WHY` 和 `UNSAID`
- 未使用 mock
- 未使用 fallback

## 校验结果

校验命令：

```bash
python3 skills/doramagic-s2/scripts/validate_skill.py \
  --skill-dir /Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output \
  --need-profile /Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/artifacts/need_profile.json \
  --synthesis-report /Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/artifacts/synthesis_report.json \
  --output /Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/artifacts/validation_report.json
```

结果：
- [validation_report.json](/Users/tang/clawd/doramagic/runs/test-20260320-123739-recipe/output/artifacts/validation_report.json)
- `report_status=PASS`
- 仅有一个 warning：次级样本 `TheSpaceOfRiri/My.Chef` 的 license 未声明

## 过程中遇到的问题

1. GitHub API 在沙箱内首次调用失败
   - 原因：DNS/网络受限
   - 处理：按要求申请放行后，继续走真实网络路径

2. `extract_facts.py` 初版对 Android 样本提取不足
   - 原因：focus file 候选列表偏向 Python/Web 项目
   - 处理：补充 `build.gradle`、`AndroidManifest.xml`、`Activity`/`Fragment` 文件识别

3. `validate_skill.py` 初版写报告时触发 Pydantic v2 兼容错误
   - 原因：`json(indent=2, ensure_ascii=False)` 在当前环境不兼容
   - 处理：改为优先使用 `model_dump_json(indent=2)`，保留旧接口 fallback

## 当前结论

本次补充开发已经把 S2 交付从“CLI 为主”调整为“Skill 为主”：

- 主入口现在是 [SKILL.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/SKILL.md)
- Python 脚本只承担确定性提取、组装和校验
- 真实数据验证已经通过
- 当前交付可继续进入 OpenClaw/Mac mini 环境做下一步部署验证

---

## 全量研究集成补充

日期：2026-03-20
任务：按 `docs/full-integration-dev-brief.md` 将 8 项研究成果一次性集成到 `skills/doramagic-s2/`，并用 `/dora 我想做一个管理 WiFi 密码的工具` 做真实验证。

### 本轮新增/升级

1. 产品主入口升级为完整研究版 [SKILL.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/SKILL.md)
   - 增加 WHY 可恢复性判断
   - 增加 8 项 DSD 暗雷检测与叠加升级规则
   - 明确必须读取 Soul Extractor Stage 1-4 指令
   - 增加预提取 Domain API 查询、社区采集、跨项目综合、卡片编译和研究型校验

2. 组装脚本重写为卡片中心 [assemble_output.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/assemble_output.py)
   - 生成 5 类卡片：concept / workflow / decision / trap / signature
   - 输出 `cards/`、`soul/00-soul.md`、`soul/expert_narrative.md`
   - 将 WHY Recoverability、DSD、Cross-project synthesis、Domain API 状态编译进最终 bundle
   - 输出 `cards_index.json` 和新的 `bundle_manifest.json`

3. 校验脚本扩展为双层校验 [validate_skill.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/validate_skill.py)
   - 先跑 `platform_openclaw.validator`
   - 再追加研究型硬检查：WHY/UNSAID、卡片数量、卡片 ID provenance、8 项 DSD、暗雷高危标注

4. 交付骨架补齐 [cards/](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/cards)
   - `concept/`
   - `workflow/`
   - `decision/`
   - `trap/`
   - `signature/`

5. 安装说明更新 [README.md](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/README.md)
   - 改为完整研究集成版说明
   - 明确 AI 自身智能 vs `exec` 脚本边界
   - 明确运行目录与产物布局

### 真实 WiFi 验证

验证输入：
- `/dora 我想做一个管理 WiFi 密码的工具`

真实 GitHub 搜索：
- 首轮组合词 `wifi password manager qr share backup` 返回 0 个候选
- 扩展搜索方向后得到真实候选：
  - `sdushantha/wifi-password`
  - `bndw/wifi-card`
  - `seemoo-lab/openwifipass`

真实下载与分析：
- [sdushantha/wifi-password](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/downloads/sdushantha-wifi-password/wifi-password-master)
  - 价值：OS 凭据取回 + QR 导出
  - 暗雷：WHY 不可恢复、行为高度依赖 OS 命令和 NetworkManager
- [bndw/wifi-card](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/downloads/bndw-wifi-card/wifi-card-master)
  - 价值：本地无跟踪、打印式分享、隐藏 SSID / WPA2-EAP / QR 编码
  - 暗雷：不同扫码器兼容性与密码显示语义
- [seemoo-lab/openwifipass](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/downloads/seemoo-lab-openwifipass/openwifipass-main)
  - 价值：附近共享协议与 trust boundary
  - 暗雷：README 明确写明 untested / incomplete / 不验证 requestor identity

社区采集：
- [sdushantha-wifi-password-community.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/artifacts/sdushantha-wifi-password-community.md)
- [bndw-wifi-card-community.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/artifacts/bndw-wifi-card-community.md)
- [seemoo-lab-openwifipass-community.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/artifacts/seemoo-lab-openwifipass-community.md)

预提取 API：
- 本机 `http://192.168.1.104:8420/domains` 无响应
- SSH 到 Mac mini 后查询 `127.0.0.1:8420` 也无响应
- 本次验证在 `assembly-context.json.analysis.domain_api` 中标注为 `unavailable`

真实产物目录：
- [assembly-context.json](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/artifacts/assembly-context.json)
- [输出目录](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output)
- [最终 SKILL.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/SKILL.md)
- [最终 PROVENANCE.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/PROVENANCE.md)
- [最终 LIMITATIONS.md](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/LIMITATIONS.md)

知识卡片：
- 3 张 concept
- 3 张 workflow
- 3 张 decision
- 3 张 trap
- 1 张 signature

### 本轮校验结果

校验命令：

```bash
python3 skills/doramagic-s2/scripts/validate_skill.py \
  --skill-dir /Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output \
  --need-profile /Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/artifacts/need_profile.json \
  --synthesis-report /Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/artifacts/synthesis_report.json \
  --output /Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/artifacts/validation_report.json
```

结果：
- [validation_report.json](/Users/tang/clawd/doramagic/runs/test-20260320-154440-wifi/output/artifacts/validation_report.json)
- `base_report_status=PASS`
- `research_status=PASS`
- `final_status=PASS`

### 额外验证

- `python3 -m py_compile` 已通过：
  - [assemble_output.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/assemble_output.py)
  - [validate_skill.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/validate_skill.py)
  - [community_signals.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/community_signals.py)
  - [extract_facts.py](/Users/tang/Documents/vibecoding/Doramagic/skills/doramagic-s2/scripts/extract_facts.py)
- `python3 -m pytest` 已启动，但在当前工具会话中长时间无进一步输出，未拿到最终退出结果

### 本轮结论

- `skills/doramagic-s2/` 已完成 full-integration brief 要求的 8 项研究成果接入
- 真实 `/dora` WiFi 场景已跑通，且最终 validator 为 `PASS`
- Domain API 当前不可用，但产品已具备诚实降级路径
- 当前最大剩余风险不是功能链路，而是仓库级 `pytest` 在本轮工具会话中未返回最终结果
