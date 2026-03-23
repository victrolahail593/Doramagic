# r06-agentic S2 工作日志

日期：2026-03-20  
负责人：S2-Codex  
任务：按 `races/r06/agentic/BRIEF.md` 将 `Stage 1.5` 从 deterministic mock 升级为真实 Agent Loop，并输出到 `races/r06/agentic/s2-codex/`。

## 本轮完成项

1. 升级主实现 [stage15_agentic.py](/Users/tang/Documents/vibecoding/Doramagic/packages/extraction/doramagic_extraction/stage15_agentic.py)
   - 保留原 deterministic mock 作为硬回退路径
   - 新增真实 live loop：`CapabilityRouter` 路由 + `LLMAdapter.generate_with_tools(...)`
   - 实现真实工具：
     - `tool_list_tree`
     - `tool_search_repo`
     - `tool_read_file`
     - `tool_read_artifact`
     - `tool_append_finding`
   - 产出固定 5 个中间文件：
     - `hypotheses.jsonl`
     - `exploration_log.jsonl`
     - `claim_ledger.jsonl`
     - `evidence_index.json`
     - `context_digest.md`
   - 保持 `ModuleResultEnvelope` / `ClaimRecord` / `Stage15Summary` 契约不变

2. 补充单元测试 [test_stage15_agentic.py](/Users/tang/Documents/vibecoding/Doramagic/packages/extraction/tests/test_stage15_agentic.py)
   - 保留原 fallback/mock 测试面
   - 新增 fake adapter + real repo file 的 live loop 单测
   - 验证 `search_repo -> read_file -> append_finding` 路径
   - 验证 confirmed claim 的 `file:line` evidence 绑定

3. 新增集成测试 [test_stage15_integration.py](/Users/tang/Documents/vibecoding/Doramagic/packages/extraction/tests/test_stage15_integration.py)
   - 使用真实小仓库 fixture 跑完整 live loop
   - 覆盖 5 个工具：
     - `list_tree`
     - `read_artifact`
     - `search_repo`
     - `read_file`
     - `append_finding`
   - 验证 summary、artifact、evidence traceability

4. 新增测试仓库 fixture [stage15_wifi_repo](/Users/tang/Documents/vibecoding/Doramagic/data/fixtures/stage15_wifi_repo)
   - [README.md](/Users/tang/Documents/vibecoding/Doramagic/data/fixtures/stage15_wifi_repo/README.md)
   - [wifi_store.py](/Users/tang/Documents/vibecoding/Doramagic/data/fixtures/stage15_wifi_repo/src/wifi_store.py)
   - 仓库内容刻意保留“明文写入 WiFi 密码到 JSON”的可验证风险，方便 Stage 1.5 产出强证据 claim

5. 补充 race 目录交付
   - [stage15_agentic.py](/Users/tang/Documents/vibecoding/Doramagic/races/r06/agentic/s2-codex/stage15_agentic.py)
   - [DECISIONS.md](/Users/tang/Documents/vibecoding/Doramagic/races/r06/agentic/s2-codex/DECISIONS.md)
   - [README.md](/Users/tang/Documents/vibecoding/Doramagic/races/r06/agentic/s2-codex/README.md)
   - [tests/README.md](/Users/tang/Documents/vibecoding/Doramagic/races/r06/agentic/s2-codex/tests/README.md)
   - [fixtures/README.md](/Users/tang/Documents/vibecoding/Doramagic/races/r06/agentic/s2-codex/fixtures/README.md)

## 关键设计选择

1. 包内实现作为 canonical 版本
   - 真实运行时和 orchestration 都引用 `packages/extraction/...`
   - race 目录只放 wrapper 与文档，不复制一份实现代码长期分叉

2. mock 路径保留不动
   - 满足 brief 的 `adapter=None` / `router=None` / 全工具禁用回退要求
   - 避免破坏现有 Stage 1.5 测试语义

3. 信息增益判断保守化
   - 新 evidence key
   - resolved claim
   - append_finding 写入了新证据
   以上任一成立才算 gain

4. race 测试不在 race 目录重复落 `test_stage15_agentic.py`
   - 原因：仓库里已经有同名测试模块
   - 若再在 `races/...` 下创建同 basename 文件，`pytest` 容易出现 import-mismatch
   - 所以 canonical 测试放在 `packages/extraction/tests/`

## 验证结果

已通过：

```bash
python3 -m py_compile \
  packages/extraction/doramagic_extraction/stage15_agentic.py \
  packages/extraction/tests/test_stage15_agentic.py \
  packages/extraction/tests/test_stage15_integration.py

python3 -m pytest \
  packages/extraction/tests/test_stage15_agentic.py \
  packages/extraction/tests/test_stage15_integration.py

python3 -m pytest packages/extraction/tests
```

结果：

- `packages/extraction/tests/test_stage15_agentic.py` + `test_stage15_integration.py`：`8 passed`
- `packages/extraction/tests`：`89 passed`

## 未完全确认项

我额外启动了仓库级：

```bash
python3 -m pytest
```

这次会话中它在输出到 `tests/test_doramagic_pipeline.py` 后长时间没有返回最终退出状态，因此我没有把“全仓库测试通过”记为已确认结果。

## 当前结论

- Stage 1.5 已具备真实 agentic 提取闭环，不再只是 Stage 1 finding 的确定性重放
- 模块满足“模型无关”约束：未在实现中直接 import `anthropic/openai/google.generativeai`
- 交付已落到 `races/r06/agentic/s2-codex/`
- 当前剩余风险不在 Stage 1.5 功能本身，而在仓库级 `pytest` 尚未拿到最终退出码
