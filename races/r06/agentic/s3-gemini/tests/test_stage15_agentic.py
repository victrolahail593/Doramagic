import sys
import unittest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

# 添加必要的路径
# 针对 Documents/vibecoding/Doramagic/races/r06/agentic/s3-gemini/tests/test_stage15_agentic.py
# parent 1: tests
# parent 2: s3-gemini
# parent 3: agentic
# parent 4: r06
# parent 5: races
# parent 6: Doramagic (project root)
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "packages" / "contracts"))
sys.path.insert(0, str(project_root / "packages" / "shared_utils"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from doramagic_contracts.base import RepoRef, Confidence, Priority
from doramagic_contracts.extraction import (
    Stage15AgenticInput,
    Stage15Budget,
    Stage15Toolset,
    RepoFacts,
    Stage1ScanOutput,
    Hypothesis,
    Stage1Coverage
)
from doramagic_shared_utils.llm_adapter import LLMAdapter, LLMResponse
from doramagic_shared_utils.capability_router import CapabilityRouter, RoutingResult
from stage15_agentic import run_stage15_agentic

class TestStage15Agentic(unittest.TestCase):
    def setUp(self):
        # 创建一个模拟仓库目录
        self.temp_repo = Path("/tmp/doramagic_test_repo")
        self.temp_repo.mkdir(parents=True, exist_ok=True)
        (self.temp_repo / "main.py").write_text("print('hello world')")
        
        self.repo_ref = RepoRef(
            repo_id="test_repo",
            full_name="test/repo",
            url="https://github.com/test/repo",
            default_branch="main",
            commit_sha="abcdef123456",
            local_path=str(self.temp_repo)
        )
        
        self.repo_facts = RepoFacts(
            repo=self.repo_ref,
            languages=["Python"],
            frameworks=[],
            entrypoints=["main.py"],
            commands=[],
            storage_paths=[],
            dependencies=[],
            repo_summary="A simple test repository."
        )
        
        self.hypothesis = Hypothesis(
            hypothesis_id="H-001",
            statement="The project uses basic Python printing.",
            reason="Found main.py with print statement.",
            priority="high",
            search_hints=["print"]
        )
        
        self.stage1_output = Stage1ScanOutput(
            repo=self.repo_ref,
            findings=[],
            hypotheses=[self.hypothesis],
            coverage=Stage1Coverage(answered_questions=[], partial_questions=[], uncovered_questions=[]),
            recommended_for_stage15=True
        )
        
        self.input_data = Stage15AgenticInput(
            repo=self.repo_ref,
            repo_facts=self.repo_facts,
            stage1_output=self.stage1_output,
            budget=Stage15Budget(),
            toolset=Stage15Toolset()
        )

    def tearDown(self):
        import shutil
        if self.temp_repo.exists():
            shutil.rmtree(self.temp_repo)

    def test_run_stage15_agentic_mock_loop(self):
        # 准备 Mock Adapter
        adapter = MagicMock(spec=LLMAdapter)
        adapter.generate_with_tools = AsyncMock()
        
        # 模拟模型响应：先调用工具，再结束
        resp1 = LLMResponse(
            content="I'll check the main.py file.",
            model_id="test-model",
            finish_reason="tool_use",
            tool_calls=[{"id": "call1", "name": "read_file", "arguments": {"file_path": "main.py"}}]
        )
        
        resp2 = LLMResponse(
            content="Confirmed. The file exists and has the print statement.",
            model_id="test-model",
            finish_reason="tool_use",
            tool_calls=[{
                "id": "call2",
                "name": "append_finding",
                "arguments": {
                    "hypothesis_id": "H-001",
                    "status": "confirmed",
                    "statement": "Successfully verified Python printing.",
                    "confidence": "high",
                    "evidence_refs": [{"path": "main.py", "start_line": 1, "end_line": 1}]
                }
            }]
        )
        
        adapter.generate_with_tools.side_effect = [resp1, resp2]
        
        # 准备 Mock Router
        router = MagicMock(spec=CapabilityRouter)
        router.route_for_stage.return_value = RoutingResult(model_id="test-model", provider="mock")
        
        # 执行
        envelope = run_stage15_agentic(self.input_data, adapter=adapter, router=router)
        
        # 验证
        self.assertEqual(envelope.status, "ok")
        self.assertEqual(len(envelope.data.promoted_claims), 1)
        self.assertEqual(envelope.data.promoted_claims[0].status, "confirmed")
        self.assertTrue((self.temp_repo / "artifacts/stage15/claim_ledger.jsonl").exists())

if __name__ == "__main__":
    unittest.main()
