"""Phase A executor: build a NeedProfile with confidence and clarification hints."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from pydantic import BaseModel

from doramagic_contracts.base import NeedProfile, SearchDirection
from doramagic_contracts.envelope import ErrorCodes, ModuleResultEnvelope, RunMetrics, WarningItem
from doramagic_contracts.executor import ExecutorConfig
from doramagic_shared_utils.llm_adapter import LLMMessage

_SYSTEM = """You normalize Doramagic user input into a JSON profile.

Return JSON only with:
{
  "domain": "english domain label",
  "intent_en": "1 sentence",
  "github_queries": ["query 1", "query 2", "query 3"],
  "relevance_terms": ["term1", "term2", "term3", "term4"],
  "confidence": 0.0,
  "questions": ["clarifying question 1", "clarifying question 2"]
}
"""

_CN_HINTS: dict[str, tuple[list[str], str]] = {
    "记账": (["expense tracker", "personal finance", "bookkeeping"], "personal finance"),
    "菜谱": (["recipe manager", "cookbook app", "meal planner"], "recipe management"),
    "密码": (["password manager", "credential vault", "secret storage"], "password management"),
    "wifi": (["wifi manager", "network credential", "wireless config"], "wifi tooling"),
    "阅读": (["reading tracker", "book notes", "library app"], "reading workflow"),
}
_STOPWORDS = {"帮我", "做", "一个", "工具", "app", "skill", "系统", "东西"}
_URL_PATTERN = re.compile(r"https?://(?:github|gitlab|gitee)\.com/[\w.-]+/[\w.-]+/?")
_SLUG_PATTERN = re.compile(r"\b[\w.-]+/[\w.-]+\b")


class NeedProfileBuilder:
    async def execute(
        self, input: BaseModel, adapter: object, config: ExecutorConfig
    ) -> ModuleResultEnvelope[NeedProfile]:
        started = time.monotonic()
        raw = input.raw_input if hasattr(input, "raw_input") else str(input)
        raw = re.sub(r"^/?dora(?:-status)?\s*", "", raw, flags=re.IGNORECASE).strip()
        if not raw:
            return self._error(ErrorCodes.INPUT_INVALID, "Empty input", started)

        profile: NeedProfile | None = None
        if adapter is not None:
            try:
                profile = await self._build_with_llm(raw, adapter)
            except Exception:  # noqa: BLE001
                profile = None
        if profile is None:
            profile = self._build_heuristic(raw)

        status = "ok" if profile.confidence >= 0.7 else "degraded"
        warnings = []
        if status == "degraded":
            warnings.append(
                WarningItem(
                    code="CLARIFY",
                    message="CLARIFY:" + (profile.questions[0] if profile.questions else "你想分析具体项目，还是先找这个领域的最佳开源项目？"),
                )
            )

        return ModuleResultEnvelope(
            module_name="NeedProfileBuilder",
            status=status,
            warnings=warnings,
            data=profile,
            metrics=RunMetrics(
                wall_time_ms=int((time.monotonic() - started) * 1000),
                llm_calls=1 if adapter is not None else 0,
                prompt_tokens=0,
                completion_tokens=0,
                estimated_cost_usd=0.0,
            ),
        )

    async def _build_with_llm(self, raw: str, adapter: object) -> NeedProfile:
        messages = [
            LLMMessage(role="system", content=_SYSTEM),
            LLMMessage(role="user", content=raw),
        ]
        if not hasattr(adapter, "generate"):
            raise RuntimeError("adapter has no generate()")
        response = await adapter.generate(getattr(adapter, "_default_model", "default"), messages)
        payload = json.loads(response.content.strip())
        keywords = []
        seen = set()
        for query in payload.get("github_queries", []):
            for word in query.split():
                lowered = word.lower()
                if lowered not in seen and len(lowered) >= 2:
                    keywords.append(lowered)
                    seen.add(lowered)
        return NeedProfile(
            raw_input=raw,
            keywords=keywords[:8] or self._fallback_keywords(raw),
            intent=raw,
            intent_en=payload.get("intent_en", raw),
            domain=payload.get("domain", "general"),
            search_directions=[
                SearchDirection(direction=query, priority="high" if index < 2 else "medium")
                for index, query in enumerate(payload.get("github_queries", [])[:5])
            ],
            constraints=["openclaw_compatible"],
            quality_expectations={},
            github_queries=payload.get("github_queries", [])[:3],
            relevance_terms=payload.get("relevance_terms", [])[:5],
            confidence=float(payload.get("confidence", 0.75)),
            questions=payload.get("questions", [])[:2],
            max_projects=3,
        )

    def _build_heuristic(self, raw: str) -> NeedProfile:
        lowered = raw.lower()
        keywords = self._fallback_keywords(raw)
        matched_domains = []
        for term, (_, domain) in _CN_HINTS.items():
            if term in lowered or term in raw:
                matched_domains.append(domain)
        has_url = bool(_URL_PATTERN.search(raw))
        has_slug = bool(_SLUG_PATTERN.search(raw))
        confidence = 0.85 if has_url or has_slug else 0.78 if len(keywords) >= 3 else 0.58
        questions: list[str] = []
        if confidence < 0.7:
            questions = [
                "你是想让我直接分析某个现有项目，还是先帮你找这个领域里最值得参考的开源项目？",
                "如果有目标项目，请直接给 GitHub URL 或项目名。",
            ]

        domain = matched_domains[0] if matched_domains else ("named project" if has_slug else "general")
        github_queries = keywords[:3]
        return NeedProfile(
            raw_input=raw,
            keywords=keywords[:8],
            intent=raw,
            intent_en=raw,
            domain=domain,
            search_directions=[
                SearchDirection(direction=direction, priority="high" if index < 2 else "medium")
                for index, direction in enumerate(github_queries[:5])
            ],
            constraints=["openclaw_compatible"],
            quality_expectations={},
            github_queries=github_queries[:3],
            relevance_terms=keywords[:5],
            confidence=confidence,
            questions=questions,
            max_projects=1 if has_url else 3,
        )

    def _fallback_keywords(self, raw: str) -> list[str]:
        keywords: list[str] = []
        seen = set()
        lowered = raw.lower()
        for needle, (translations, _) in _CN_HINTS.items():
            if needle in raw or needle in lowered:
                for item in translations:
                    if item not in seen:
                        keywords.append(item)
                        seen.add(item)
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", lowered):
            if token not in seen and token not in _STOPWORDS:
                keywords.append(token)
                seen.add(token)
        for token in re.findall(r"[\u4e00-\u9fff]{2,}", raw):
            if token not in seen and token not in _STOPWORDS:
                keywords.append(token)
                seen.add(token)
        return keywords or ["open source tool"]

    def _error(self, code: str, message: str, started: float) -> ModuleResultEnvelope[NeedProfile]:
        return ModuleResultEnvelope(
            module_name="NeedProfileBuilder",
            status="error",
            error_code=code,
            warnings=[WarningItem(code=code, message=message)],
            data=None,
            metrics=RunMetrics(
                wall_time_ms=int((time.monotonic() - started) * 1000),
                llm_calls=0,
                prompt_tokens=0,
                completion_tokens=0,
                estimated_cost_usd=0.0,
            ),
        )

    def validate_input(self, input: BaseModel) -> list[str]:
        if not hasattr(input, "raw_input") and not isinstance(input, str):
            return ["NeedProfileBuilder expects raw_input"]
        return []

    def can_degrade(self) -> bool:
        return True
