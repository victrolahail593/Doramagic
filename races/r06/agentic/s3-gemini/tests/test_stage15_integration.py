import sys
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import json
import os
import shutil

# 添加必要的路径
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "packages" / "contracts"))
sys.path.insert(0, str(project_root / "packages" / "shared_utils"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from doramagic_contracts.base import RepoRef
from doramagic_contracts.extraction import (
    Stage15AgenticInput,
    Stage15Budget,
    Stage15Toolset,
    RepoFacts,
    Stage1ScanOutput,
    Hypothesis,
    Stage1Coverage
)
from doramagic_shared_utils.llm_adapter import LLMAdapter, LLMResponse, LLMMessage
from doramagic_shared_utils.capability_router import CapabilityRouter, RoutingResult
from stage15_agentic import run_stage15_agentic

class TestStage15Integration(unittest.TestCase):
    def setUp(self):
        # 创建一个真实的临时仓库 fixture
        self.repo_path = Path("/tmp/dm_integration_repo")
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)
        self.repo_path.mkdir(parents=True)
        
        # 模拟一个带有多种文件的仓库
        (self.repo_path / "README.md").write_text("# Test Repo\nThis is a test.")
        (self.repo_path / "src").mkdir()
        (self.repo_path / "src/main.py").write_text("def start():\n    print('app started')\n\nif __name__ == '__main__':\n    start()")
        (self.repo_path / "config.json").write_text('{"version": "1.0.0", "debug": true}')
        
        self.repo_ref = RepoRef(
            repo_id="integration_repo",
            full_name="test/integration",
            url="https://github.com/test/integration",
            default_branch="main",
            commit_sha="init_sha",
            local_path=str(self.repo_path)
        )
        
        self.repo_facts = RepoFacts(
            repo=self.repo_ref,
            languages=["Python"],
            frameworks=[],
            entrypoints=["src/main.py"],
            commands=[],
            storage_paths=["config.json"],
            dependencies=[],
            repo_summary="Integration test repository."
        )
        
        self.hypotheses = [
            Hypothesis(
                hypothesis_id="H-ENTRY",
                statement="The application starts via src/main.py start() function.",
                reason="Standard entrypoint pattern.",
                priority="high",
                search_hints=["start", "main"]
            )
        ]
        
        self.stage1_output = Stage1ScanOutput(
            repo=self.repo_ref,
            findings=[],
            hypotheses=self.hypotheses,
            coverage=Stage1Coverage(answered_questions=[], partial_questions=[], uncovered_questions=[]),
            recommended_for_stage15=True
        )
        
        self.input_data = Stage15AgenticInput(
            repo=self.repo_ref,
            repo_facts=self.repo_facts,
            stage1_output=self.stage1_output,
            budget=Stage15Budget(max_rounds=3, max_tool_calls=10),
            toolset=Stage15Toolset()
        )

    def tearDown(self):
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)

    def test_integration_agent_loop(self):
        # 准备 Mock Adapter，模拟一个探索过程
        adapter = MagicMock(spec=LLMAdapter)
        adapter.generate_with_tools = AsyncMock()
        
        # 步骤 1: 列出目录
        resp1 = LLMResponse(
            content="I'll list the tree to see the structure.",
            model_id="gemini-2.5-pro",
            finish_reason="tool_use",
            tool_calls=[{"id": "c1", "name": "list_tree", "arguments": {"path": "."}}]
        )
        
        # 步骤 2: 读取文件内容
        resp2 = LLMResponse(
            content="Found src/main.py. Reading it.",
            model_id="gemini-2.5-pro",
            finish_reason="tool_use",
            tool_calls=[{"id": "c2", "name": "read_file", "arguments": {"file_path": "src/main.py"}}]
        )
        
        # 步骤 3: 提交 Claim
        resp3 = LLMResponse(
            content="Verified. It starts via start().",
            model_id="gemini-2.5-pro",
            finish_reason="tool_use",
            tool_calls=[{
                "id": "c3",
                "name": "append_finding",
                "arguments": {
                    "hypothesis_id": "H-ENTRY",
                    "status": "confirmed",
                    "statement": "The app indeed starts from src/main.py:start().",
                    "confidence": "high",
                    "evidence_refs": [{"path": "src/main.py", "start_line": 1, "end_line": 2}]
                }
            }]
        )
        
        adapter.generate_with_tools.side_effect = [resp1, resp2, resp3]
        
        # 准备 Mock Router
        router = MagicMock(spec=CapabilityRouter)
        router.route_for_stage.return_value = RoutingResult(model_id="gemini-2.5-pro", provider="google")
        
        # 执行
        envelope = run_stage15_agentic(self.input_data, adapter=adapter, router=router)
        
        # 验证
        self.assertEqual(envelope.status, "ok")
        self.assertEqual(len(envelope.data.promoted_claims), 1)
        self.assertEqual(envelope.data.summary.resolved_hypotheses, ["H-ENTRY"])
        
        # 验证 Exploration Log 写入了
        log_path = self.repo_path / "artifacts/stage15/exploration_log.jsonl"
        self.assertTrue(log_path.exists())
        with log_path.open() as f:
            logs = [json.loads(line) for line in f]
            self.assertEqual(len(logs), 3)
            self.assertEqual(logs[0]["tool_name"], "list_tree")
            self.assertEqual(logs[1]["tool_name"], "read_file")
            self.assertEqual(logs[2]["tool_name"], "append_finding")

if __name__ == "__main__":
    unittest.main()
