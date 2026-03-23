"""Agent 工具集 — 5 个工具的定义和实现。

工具列表:
1. read_artifact: 读取 Stage 0/1 产出的 artifact 文件
2. list_tree: 列出目录结构
3. search_repo: 在仓库中搜索内容
4. read_file: 读取具体文件内容
5. append_finding: 追加发现到 claim ledger
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Sequence
from dataclasses import dataclass, field

# 动态导入 contracts
import sys
_CONTRACTS_PATH = Path(__file__).parent.parent.parent.parent / "packages" / "contracts"
if str(_CONTRACTS_PATH) not in sys.path:
    sys.path.insert(0, str(_CONTRACTS_PATH))

from doramagic_contracts.base import EvidenceRef
from doramagic_contracts.extraction import (
    Stage1Finding,
    Hypothesis,
    ExplorationLogEntry,
    ClaimRecord,
)


@dataclass
class ToolSchema:
    """工具 Schema 定义。"""
    name: str
    description: str
    parameters: dict
    required: list[str] = field(default_factory=list)

    def to_openai_format(self) -> dict:
        """转换为 OpenAI function calling 格式。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                }
            }
        }

    def to_anthropic_format(self) -> dict:
        """转换为 Anthropic tool use 格式。"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required,
            }
        }


# 工具 Schema 定义
READ_ARTIFACT_SCHEMA = ToolSchema(
    name="read_artifact",
    description="读取 Stage 0/1 产出的 artifact 文件，如 findings、hypotheses、repo_facts 等。",
    parameters={
        "artifact_type": {
            "type": "string",
            "enum": ["stage1_findings", "repo_facts", "hypotheses", "context_digest"],
            "description": "要读取的 artifact 类型"
        },
        "filter": {
            "type": "object",
            "description": "可选的过滤条件，如 finding_ids 或 hypothesis_ids",
            "properties": {
                "finding_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要筛选的 finding ID 列表"
                },
                "hypothesis_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要筛选的 hypothesis ID 列表"
                }
            }
        }
    },
    required=["artifact_type"]
)

LIST_TREE_SCHEMA = ToolSchema(
    name="list_tree",
    description="列出仓库中指定路径下的目录结构，支持递归深度控制。",
    parameters={
        "path": {
            "type": "string",
            "description": "要列出的目录路径，相对于仓库根目录"
        },
        "max_depth": {
            "type": "integer",
            "description": "递归深度，默认 2",
            "default": 2
        },
        "include_files": {
            "type": "boolean",
            "description": "是否包含文件，默认 true",
            "default": True
        }
    },
    required=["path"]
)

SEARCH_REPO_SCHEMA = ToolSchema(
    name="search_repo",
    description="在仓库中搜索指定的关键词或模式，支持文件名和内容搜索。",
    parameters={
        "query": {
            "type": "string",
            "description": "搜索关键词或正则表达式"
        },
        "scope": {
            "type": "string",
            "enum": ["filename", "content", "both"],
            "description": "搜索范围：文件名、内容或两者",
            "default": "both"
        },
        "file_pattern": {
            "type": "string",
            "description": "文件过滤模式，如 *.py 或 src/**",
            "default": "*"
        },
        "max_results": {
            "type": "integer",
            "description": "最大返回结果数",
            "default": 20
        }
    },
    required=["query"]
)

READ_FILE_SCHEMA = ToolSchema(
    name="read_file",
    description="读取指定文件的完整内容或指定行范围。",
    parameters={
        "path": {
            "type": "string",
            "description": "文件路径，相对于仓库根目录"
        },
        "start_line": {
            "type": "integer",
            "description": "起始行号（可选），默认从第 1 行开始",
            "default": 1
        },
        "end_line": {
            "type": "integer",
            "description": "结束行号（可选），默认读取到文件末尾"
        },
        "include_context": {
            "type": "boolean",
            "description": "是否包含周围上下文（前后各 5 行）",
            "default": False
        }
    },
    required=["path"]
)

APPEND_FINDING_SCHEMA = ToolSchema(
    name="append_finding",
    description="追加一个发现到 claim ledger，用于记录 Agent 探索过程中的发现。",
    parameters={
        "hypothesis_id": {
            "type": "string",
            "description": "相关的 hypothesis ID"
        },
        "claim_statement": {
            "type": "string",
            "description": "发现声明，描述 Agent 发现的知识"
        },
        "status": {
            "type": "string",
            "enum": ["confirmed", "rejected", "pending", "inference"],
            "description": "发现状态：confirmed（已确认）、rejected（已反驳）、pending（待验证）、inference（推断）"
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "置信度"
        },
        "evidence_snippet": {
            "type": "string",
            "description": "支撑该发现的代码片段或文件路径"
        },
        "evidence_path": {
            "type": "string",
            "description": "证据文件路径"
        },
        "evidence_lines": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "证据行号 [start_line, end_line]"
        }
    },
    required=["hypothesis_id", "claim_statement", "status", "confidence"]
)


ALL_TOOL_SCHEMAS = [
    READ_ARTIFACT_SCHEMA,
    LIST_TREE_SCHEMA,
    SEARCH_REPO_SCHEMA,
    READ_FILE_SCHEMA,
    APPEND_FINDING_SCHEMA,
]


@dataclass
class AgentContext:
    """Agent 执行上下文。"""
    repo_root: Path
    repo_id: str
    stage1_findings: list[Stage1Finding]
    hypotheses: list[Hypothesis]
    repo_facts: dict[str, Any]
    exploration_log: list[ExplorationLogEntry]
    claim_ledger: list[ClaimRecord]
    step_counter: int = 0
    round_index: int = 0

    def next_step_id(self) -> str:
        """生成下一个 step ID。"""
        self.step_counter += 1
        return f"S-{self.step_counter:03d}"


@dataclass
class ToolResult:
    """工具执行结果。"""
    success: bool
    observation: str
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    error_message: Optional[str] = None


class ToolExecutor:
    """工具执行器 — 实现所有工具的实际逻辑。"""

    def __init__(self, context: AgentContext):
        self.ctx = context

    def execute(self, tool_name: str, tool_input: dict) -> ToolResult:
        """执行工具并返回结果。"""
        if tool_name == "read_artifact":
            return self._read_artifact(tool_input)
        elif tool_name == "list_tree":
            return self._list_tree(tool_input)
        elif tool_name == "search_repo":
            return self._search_repo(tool_input)
        elif tool_name == "read_file":
            return self._read_file(tool_input)
        elif tool_name == "append_finding":
            return self._append_finding(tool_input)
        else:
            return ToolResult(
                success=False,
                observation="",
                error_message=f"Unknown tool: {tool_name}"
            )

    def _read_artifact(self, params: dict) -> ToolResult:
        """读取 Stage 0/1 产出的 artifact。"""
        artifact_type = params.get("artifact_type")
        filter_obj = params.get("filter", {})

        if artifact_type == "stage1_findings":
            findings = self.ctx.stage1_findings
            finding_ids = filter_obj.get("finding_ids")
            if finding_ids:
                findings = [f for f in findings if f.finding_id in finding_ids]

            summary_lines = []
            for f in findings[:10]:  # 限制输出
                summary_lines.append(
                    f"- [{f.finding_id}] {f.knowledge_type}: {f.title}"
                )

            return ToolResult(
                success=True,
                observation=f"Stage 1 Findings ({len(findings)} items):\n" + "\n".join(summary_lines),
                evidence_refs=self._extract_evidence_from_findings(findings)
            )

        elif artifact_type == "repo_facts":
            facts = self.ctx.repo_facts
            return ToolResult(
                success=True,
                observation=f"Repo Facts:\n- Languages: {facts.get('languages', [])}\n"
                           f"- Frameworks: {facts.get('frameworks', [])}\n"
                           f"- Entrypoints: {facts.get('entrypoints', [])}"
            )

        elif artifact_type == "hypotheses":
            hypotheses = self.ctx.hypotheses
            hypothesis_ids = filter_obj.get("hypothesis_ids")
            if hypothesis_ids:
                hypotheses = [h for h in hypotheses if h.hypothesis_id in hypothesis_ids]

            lines = []
            for h in hypotheses:
                lines.append(f"- [{h.hypothesis_id}] ({h.priority}): {h.statement}")
                lines.append(f"  Reason: {h.reason}")
                lines.append(f"  Search hints: {', '.join(h.search_hints)}")

            return ToolResult(
                success=True,
                observation="Hypotheses to explore:\n" + "\n".join(lines)
            )

        elif artifact_type == "context_digest":
            digest_path = self.ctx.repo_root / "artifacts" / "stage15" / "context_digest.md"
            if digest_path.exists():
                return ToolResult(
                    success=True,
                    observation=digest_path.read_text(encoding="utf-8")
                )
            else:
                return ToolResult(
                    success=True,
                    observation="No context digest available yet. This is the first round."
                )

        return ToolResult(
            success=False,
            observation="",
            error_message=f"Unknown artifact type: {artifact_type}"
        )

    def _list_tree(self, params: dict) -> ToolResult:
        """列出目录结构。"""
        path = params.get("path", "")
        max_depth = params.get("max_depth", 2)
        include_files = params.get("include_files", True)

        target_path = self.ctx.repo_root / path if path else self.ctx.repo_root

        if not target_path.exists():
            return ToolResult(
                success=False,
                observation="",
                error_message=f"Path not found: {path}"
            )

        lines = []
        evidence_refs = []

        def walk_dir(current: Path, depth: int, prefix: str = ""):
            if depth > max_depth:
                return
            try:
                items = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return

            # 跳过隐藏目录和常见的忽略目录
            ignore_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}

            for item in items[:50]:  # 限制输出
                if item.name.startswith(".") or item.name in ignore_dirs:
                    continue

                rel_path = str(item.relative_to(self.ctx.repo_root))
                is_dir = item.is_dir()

                if is_dir:
                    lines.append(f"{prefix}{item.name}/")
                    if depth < max_depth:
                        walk_dir(item, depth + 1, prefix + "  ")
                elif include_files:
                    lines.append(f"{prefix}{item.name}")

        walk_dir(target_path, 0)

        return ToolResult(
            success=True,
            observation=f"Directory tree for {path or 'root'}:\n" + "\n".join(lines[:100])
        )

    def _search_repo(self, params: dict) -> ToolResult:
        """在仓库中搜索。"""
        query = params.get("query", "")
        scope = params.get("scope", "both")
        file_pattern = params.get("file_pattern", "*")
        max_results = params.get("max_results", 20)

        import fnmatch
        import re

        results = []
        evidence_refs = []

        # 编译搜索模式
        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error:
            pattern = re.compile(re.escape(query), re.IGNORECASE)

        for file_path in self.ctx.repo_root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.name.startswith("."):
                continue
            if any(part.startswith(".") for part in file_path.relative_to(self.ctx.repo_root).parts):
                continue

            rel_path = str(file_path.relative_to(self.ctx.repo_root))

            # 文件名匹配
            if scope in ("filename", "both"):
                if pattern.search(file_path.name):
                    results.append(f"[FILE] {rel_path}")
                    if len(results) >= max_results:
                        break

            # 内容匹配
            if scope in ("content", "both") and len(results) < max_results:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(content.splitlines()[:500], 1):
                        if pattern.search(line):
                            results.append(f"[CONTENT] {rel_path}:{i}: {line.strip()[:80]}")
                            evidence_refs.append(EvidenceRef(
                                kind="file_line",
                                path=rel_path,
                                start_line=i,
                                end_line=i,
                                snippet=line.strip()[:200]
                            ))
                            if len(results) >= max_results:
                                break
                except Exception:
                    pass

            if len(results) >= max_results:
                break

        return ToolResult(
            success=True,
            observation=f"Search results for '{query}':\n" + "\n".join(results[:max_results]),
            evidence_refs=evidence_refs[:max_results]
        )

    def _read_file(self, params: dict) -> ToolResult:
        """读取文件内容。"""
        path = params.get("path", "")
        start_line = params.get("start_line", 1)
        end_line = params.get("end_line")
        include_context = params.get("include_context", False)

        file_path = self.ctx.repo_root / path

        if not file_path.exists():
            return ToolResult(
                success=False,
                observation="",
                error_message=f"File not found: {path}"
            )

        if not file_path.is_file():
            return ToolResult(
                success=False,
                observation="",
                error_message=f"Not a file: {path}"
            )

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            if end_line is None:
                end_line = len(lines)

            # 提取指定范围
            selected_lines = lines[start_line - 1:end_line]
            result_text = "\n".join(f"{i + start_line:4d}: {line}" for i, line in enumerate(selected_lines))

            # 包含上下文
            if include_context:
                context_start = max(1, start_line - 5)
                context_end = min(len(lines), end_line + 5)
                context_lines = lines[context_start - 1:context_end]
                result_text = "\n".join(f"{i + context_start:4d}: {line}" for i, line in enumerate(context_lines))

            evidence_ref = EvidenceRef(
                kind="file_line",
                path=path,
                start_line=start_line,
                end_line=min(end_line, len(lines)),
                snippet="\n".join(selected_lines[:20])  # 限制 snippet 长度
            )

            return ToolResult(
                success=True,
                observation=f"File: {path} (lines {start_line}-{end_line})\n\n{result_text}",
                evidence_refs=[evidence_ref]
            )

        except Exception as e:
            return ToolResult(
                success=False,
                observation="",
                error_message=f"Error reading file: {e}"
            )

    def _append_finding(self, params: dict) -> ToolResult:
        """追加发现到 claim ledger。"""
        hypothesis_id = params.get("hypothesis_id")
        claim_statement = params.get("claim_statement")
        status = params.get("status", "pending")
        confidence = params.get("confidence", "medium")
        evidence_snippet = params.get("evidence_snippet", "")
        evidence_path = params.get("evidence_path", "")
        evidence_lines = params.get("evidence_lines", [])

        # 生成 claim ID
        claim_id = f"C-{self.ctx.repo_id[:8]}-{len(self.ctx.claim_ledger) + 1:03d}"

        # 构建证据引用
        evidence_refs = []
        if evidence_path:
            start_line = evidence_lines[0] if len(evidence_lines) >= 2 else 1
            end_line = evidence_lines[1] if len(evidence_lines) >= 2 else start_line
            evidence_refs.append(EvidenceRef(
                kind="file_line",
                path=evidence_path,
                start_line=start_line,
                end_line=end_line,
                snippet=evidence_snippet[:500] if evidence_snippet else None
            ))

        # 创建 Claim Record
        claim = ClaimRecord(
            claim_id=claim_id,
            statement=claim_statement,
            status=status,
            confidence=confidence,
            hypothesis_id=hypothesis_id,
            supporting_step_ids=[self.ctx.next_step_id()],
            evidence_refs=evidence_refs
        )

        self.ctx.claim_ledger.append(claim)

        return ToolResult(
            success=True,
            observation=f"Claim {claim_id} appended with status: {status}",
            evidence_refs=evidence_refs
        )

    def _extract_evidence_from_findings(self, findings: list[Stage1Finding]) -> list[EvidenceRef]:
        """从 findings 中提取证据引用。"""
        evidence_refs = []
        for finding in findings:
            for ref in finding.evidence_refs:
                if ref.kind == "file_line" and ref.start_line and ref.end_line:
                    evidence_refs.append(ref)
        return evidence_refs[:20]  # 限制数量


def get_tool_schemas(format: str = "openai") -> list[dict]:
    """获取所有工具的 Schema。

    Args:
        format: "openai" 或 "anthropic"
    """
    if format == "anthropic":
        return [s.to_anthropic_format() for s in ALL_TOOL_SCHEMAS]
    return [s.to_openai_format() for s in ALL_TOOL_SCHEMAS]