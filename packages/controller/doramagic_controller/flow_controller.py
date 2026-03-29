"""Flow controller for the Doramagic v12.1.1 deterministic DAG."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from doramagic_contracts.adapter import ClarificationRequest, PlatformAdapter, ProgressUpdate
from doramagic_contracts.base import NeedProfile, NeedProfileContract, RoutingDecision
from doramagic_contracts.budget import BudgetPolicy
from doramagic_contracts.cross_project import (
    CommunityKnowledge,
    CompareMetrics,
    CompareOutput,
    DiscoveryConfig,
    DiscoveryInput,
    DiscoveryResult,
    ExtractedProjectSummary,
    SynthesisInput,
    SynthesisReportData,
)
from doramagic_contracts.envelope import ModuleResultEnvelope, RunMetrics, WarningItem
from doramagic_contracts.executor import ExecutorConfig, PhaseExecutor
from doramagic_contracts.skill import (
    CompileBundleContract,
    SkillBundlePaths,
    SkillCompilerInput,
    ValidationInput,
)
from pydantic import BaseModel

from .budget_manager import BudgetManager
from .event_bus import EventBus
from .input_router import InputRouter
from .lease_manager import LeaseManager
from .state_definitions import (
    CONDITIONAL_EDGES,
    MAX_REVISE_LOOPS,
    PHASE_EXECUTOR_MAP,
    TRANSITIONS,
    Phase,
)

logger = logging.getLogger("doramagic.controller")

try:
    from doramagic_shared_utils.capability_router import (
        TASK_CLAIM_SYNTHESIS,
        TASK_EVIDENCE_EXTRACTION,
        TASK_GENERAL,
        CapabilityRouter,
        reset_routing_log,
    )
except Exception:
    CapabilityRouter = None
    TASK_GENERAL = "general"
    TASK_EVIDENCE_EXTRACTION = "evidence_extraction"
    TASK_CLAIM_SYNTHESIS = "claim_synthesis"


class ControllerState:
    """Serializable controller state for re-entrant execution."""

    def __init__(
        self,
        run_id: str,
        phase: Phase = Phase.INIT,
        raw_input: str = "",
        lease_token: str = "",
        revise_count: int = 0,
        clarification_round: int = 0,
        degraded_mode: bool = False,
        delivery_tier: str = "full_skill",
        phase_artifacts: dict[str, Any] | None = None,
        degradation_log: list[str] | None = None,
    ) -> None:
        self.run_id = run_id
        self.phase = phase
        self.raw_input = raw_input
        self.lease_token = lease_token
        self.revise_count = revise_count
        self.clarification_round = clarification_round
        self.degraded_mode = degraded_mode
        self.delivery_tier = delivery_tier
        self.phase_artifacts: dict[str, Any] = phase_artifacts or {}
        self.degradation_log: list[str] = degradation_log or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "phase": self.phase.value,
            "raw_input": self.raw_input,
            "lease_token": self.lease_token,
            "revise_count": self.revise_count,
            "clarification_round": self.clarification_round,
            "degraded_mode": self.degraded_mode,
            "delivery_tier": self.delivery_tier,
            "phase_artifacts": self.phase_artifacts,
            "degradation_log": self.degradation_log,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ControllerState:
        return cls(
            run_id=data["run_id"],
            phase=Phase(data["phase"]),
            raw_input=data.get("raw_input", ""),
            lease_token=data.get("lease_token", ""),
            revise_count=data.get("revise_count", 0),
            clarification_round=data.get("clarification_round", 0),
            degraded_mode=data.get("degraded_mode", False),
            delivery_tier=data.get("delivery_tier", "full_skill"),
            phase_artifacts=data.get("phase_artifacts", {}),
            degradation_log=data.get("degradation_log", []),
        )

    @property
    def routing(self) -> RoutingDecision | None:
        raw = self.phase_artifacts.get("routing_decision")
        if isinstance(raw, RoutingDecision):
            return raw
        if isinstance(raw, dict):
            try:
                return RoutingDecision(**raw)
            except Exception:
                return None
        return None

    @property
    def candidate_count(self) -> int:
        discovery = self.phase_artifacts.get("discovery_result", {})
        if isinstance(discovery, dict):
            return int(discovery.get("candidate_count") or len(discovery.get("candidates", [])))
        return 0

    @property
    def successful_extractions(self) -> int:
        extraction = self.phase_artifacts.get("extraction_aggregate", {})
        if isinstance(extraction, dict):
            return int(extraction.get("success_count", 0))
        return 0

    @property
    def synthesis_ok(self) -> bool:
        synthesis = self.phase_artifacts.get("synthesis_bundle", {})
        if isinstance(synthesis, dict):
            return bool(
                synthesis.get("selected_knowledge")
                or synthesis.get("consensus")
                or synthesis.get("global_theses")
            )
        return False

    @property
    def compile_ready(self) -> bool:
        synthesis = self.phase_artifacts.get("synthesis_bundle", {})
        if isinstance(synthesis, dict):
            return bool(synthesis.get("compile_ready", False))
        return False

    @property
    def compile_ok(self) -> bool:
        compile_bundle = self.phase_artifacts.get("compile_bundle", {})
        if isinstance(compile_bundle, dict):
            return bool(compile_bundle.get("full_draft")) or bool(
                compile_bundle.get("artifact_paths", {}).get("SKILL.md")
            )
        return False

    @property
    def quality_score(self) -> float:
        validation = self.phase_artifacts.get("validation_report", {})
        if isinstance(validation, dict):
            return float(validation.get("overall_score", 0.0))
        return 0.0

    @property
    def blockers(self) -> bool:
        validation = self.phase_artifacts.get("validation_report", {})
        if not isinstance(validation, dict):
            return False
        if validation.get("status") == "BLOCKED":
            return True
        for check in validation.get("checks", []):
            if (
                isinstance(check, dict)
                and not check.get("passed", True)
                and check.get("severity") == "blocking"
            ):
                return True
        return False

    @property
    def weakest_section(self) -> str | None:
        validation = self.phase_artifacts.get("validation_report", {})
        if isinstance(validation, dict):
            return validation.get("weakest_section")
        return None

    @property
    def routing_route(self) -> str:
        routing = self.routing
        if routing is not None:
            return routing.route
        return ""

    @property
    def has_clawhub(self) -> bool:
        extraction = self.phase_artifacts.get("extraction_aggregate", {})
        if isinstance(extraction, dict):
            for env in extraction.get("repo_envelopes", []):
                if isinstance(env, dict) and "clawhub" in (env.get("repo_url", "") or "").lower():
                    return True
        return False

    @property
    def budget_exceeded(self) -> bool:
        return False  # Budget check handled separately in _run_executor


class FlowController:
    """Deterministic controller with conditional routing, fan-out and degraded delivery."""

    def __init__(
        self,
        adapter: PlatformAdapter,
        run_dir: Path,
        executors: dict[str, PhaseExecutor] | None = None,
        budget_policy: BudgetPolicy | None = None,
        lease_ttl: int = 300,
    ) -> None:
        self._adapter = adapter
        self._run_dir = run_dir
        self._run_dir.mkdir(parents=True, exist_ok=True)
        self._executors = executors or {}
        self._lease = LeaseManager(run_dir / "leases", default_ttl_seconds=lease_ttl)
        self._budget = BudgetManager(budget_policy)
        self._router = InputRouter()
        # run_id 从 run_dir 目录名提取, 确保每条事件都有非空的 run_id
        self._event_bus = EventBus(run_dir, run_id=run_dir.name)
        self._state: ControllerState | None = None
        self._run_log: list[dict[str, Any]] = []
        self._capability_router = self._build_capability_router()

    async def run(self, user_input: str = "", resume_run_id: str | None = None) -> ControllerState:
        if resume_run_id:
            self._state = self._load_state(resume_run_id)
            if self._state is None:
                self._state = self._create_error_state(
                    f"No saved state found for run_id={resume_run_id}"
                )
                return self._state
            if self._state.phase == Phase.PHASE_A_CLARIFY and user_input.strip():
                self._state.clarification_round += 1
                self._state.raw_input = f"{self._state.raw_input}\n补充说明: {user_input.strip()}"
                self._state.phase = Phase.PHASE_A
        else:
            self._state = ControllerState(run_id=self._run_dir.name, raw_input=user_input)

        self._budget.start()
        self._setup_directories()
        if self._capability_router is not None:
            with contextlib.suppress(Exception):
                reset_routing_log()

        self._emit_event(
            "run_started",
            "run started",
            phase=self._state.phase.value,
            meta={"run_id": self._state.run_id},
        )
        if not resume_run_id:
            await self._send_progress(
                phase=self._state.phase.value,
                status="started",
                message=self._build_plan_preview(),
                percent=self._phase_progress_pct(self._state.phase),
            )

        while self._state.phase not in (
            Phase.DONE,
            Phase.DEGRADED,
            Phase.ERROR,
            Phase.PHASE_A_CLARIFY,
        ):
            current = self._state.phase
            await self._step()
            if self._state.phase == current:
                self._state.phase = Phase.ERROR
                self._state.degradation_log.append(f"Phase stuck at {current.value}")
                break

        self._save_state()
        self._write_run_log()
        if self._state.phase in (Phase.DONE, Phase.DEGRADED):
            self._persist_accumulated_knowledge()
            self._emit_event(
                "run_completed",
                "run completed",
                phase=self._state.phase.value,
                status=self._state.phase.value.lower(),
                meta={"delivery_tier": self._state.delivery_tier},
            )
        elif self._state.phase == Phase.ERROR:
            self._emit_event(
                "run_failed", "run failed", phase=self._state.phase.value, status="error"
            )
        return self._state

    async def _step(self) -> None:
        phase = self._state.phase
        self._log_event("phase_started", {"phase": phase.value})
        self._emit_event(
            "phase_started", f"{phase.value} started", phase=phase.value, status="started"
        )
        await self._send_progress(
            phase=phase.value,
            status="started",
            message=self._phase_start_message(phase),
            percent=self._phase_progress_pct(phase),
        )

        if phase == Phase.INIT:
            self._transition(self._evaluate_edge(Phase.INIT))
        elif phase == Phase.PHASE_A:
            await self._handle_phase_a()
        else:
            await self._dispatch_executor(phase)

        if self._state.phase != phase:
            self._emit_event(
                "phase_completed", f"{phase.value} completed", phase=phase.value, status="completed"
            )
            await self._send_progress(
                phase=phase.value,
                status="completed",
                message=self._phase_complete_message(phase),
                percent=self._phase_progress_pct(self._state.phase),
            )

    async def _handle_phase_a(self) -> None:
        executor = self._executors.get("NeedProfileBuilder")
        if executor is None:
            self._state.phase = Phase.ERROR
            self._state.degradation_log.append("NeedProfileBuilder not registered")
            return

        result = await self._run_executor("NeedProfileBuilder", executor)
        if result is None or result.data is None:
            self._state.phase = Phase.ERROR
            self._state.degradation_log.append("NeedProfileBuilder returned no profile")
            return

        profile = (
            result.data if isinstance(result.data, NeedProfile) else NeedProfile(**result.data)
        )
        routing = self._router.route(profile)
        if routing.route == "LOW_CONFIDENCE" and self._state.clarification_round >= 2:
            routing = RoutingDecision(
                route="DOMAIN_EXPLORE",
                skip_discovery=False,
                max_repos=profile.max_projects,
                repo_urls=[],
                project_names=[],
                confidence=max(profile.confidence, 0.55),
                reasoning="best-guess fallback after 2 clarification rounds",
            )

        self._state.phase_artifacts["routing_decision"] = routing.model_dump()
        self._state.phase_artifacts["need_profile_contract"] = self._build_need_profile_contract(
            profile, routing
        ).model_dump()
        self._state.phase_artifacts["accumulated_knowledge"] = self._load_accumulated_knowledge(
            profile.domain
        )

        if routing.route == "LOW_CONFIDENCE" and self._state.clarification_round < 2:
            question = self._clarification_question(profile, result)
            await self._adapter.ask_clarification(
                ClarificationRequest(
                    question=question, round_number=self._state.clarification_round + 1
                )
            )
            self._emit_event(
                "degraded",
                "clarification requested",
                phase=Phase.PHASE_A_CLARIFY.value,
                status="clarify",
            )
            self._state.phase = Phase.PHASE_A_CLARIFY
            self._save_state()
            return

        next_phase = self._evaluate_edge(Phase.PHASE_A)
        self._transition(next_phase)

    async def _dispatch_executor(self, phase: Phase) -> None:
        executor_name = PHASE_EXECUTOR_MAP.get(phase)
        if not executor_name:
            self._state.phase = Phase.ERROR
            self._state.degradation_log.append(f"No executor mapped for {phase.value}")
            return

        executor = self._executors.get(executor_name)
        if executor is None:
            if phase == Phase.PHASE_G:
                self._state.phase = Phase.ERROR
                self._state.degradation_log.append(f"{executor_name} not registered")
            else:
                self._enter_degraded(
                    f"{executor_name} not registered", self._infer_delivery_tier(phase)
                )
            return

        result = await self._run_executor(executor_name, executor)
        if result is None:
            if phase == Phase.PHASE_G:
                self._state.phase = Phase.ERROR
            else:
                self._enter_degraded(
                    f"{executor_name} returned no result", self._infer_delivery_tier(phase)
                )
            return

        if result.status == "error":
            if phase == Phase.PHASE_G:
                self._state.phase = Phase.ERROR
                self._state.degradation_log.append(f"{executor_name} failed during packaging")
            else:
                self._enter_degraded(
                    f"{executor_name} failed: {result.error_code or 'unknown'}",
                    self._infer_delivery_tier(phase),
                )
            return

        if phase == Phase.PHASE_C and result.status == "degraded":
            reason = "WorkerSupervisor partial failure; best-effort delivery enabled"
            self._state.degraded_mode = True
            self._state.degradation_log.append(reason)
            self._emit_event(
                "degraded",
                reason,
                phase=phase.value,
                status="degraded",
                meta={"delivery_tier": self._state.delivery_tier or "full_skill"},
            )

        if phase == Phase.PHASE_F:
            self._emit_event(
                "quality_scored",
                f"quality score={self._state.quality_score:.1f}",
                phase=phase.value,
                status=result.status,
                meta={
                    "overall_score": self._state.quality_score,
                    "weakest_section": self._state.weakest_section,
                    "revise_count": self._state.revise_count,
                },
            )

        next_phase = self._evaluate_edge(phase)
        if phase == Phase.PHASE_F and next_phase == Phase.PHASE_E:
            self._state.revise_count += 1
            self._emit_event(
                "revise_triggered",
                f"quality repair loop triggered ({self._state.revise_count}/{MAX_REVISE_LOOPS})",
                phase=phase.value,
                status="revise",
                meta={"weakest_section": self._state.weakest_section},
            )
        if next_phase == Phase.DEGRADED:
            self._enter_degraded(f"{executor_name} degraded", self._infer_delivery_tier(phase))
            return
        self._transition(next_phase)

    async def _run_executor(
        self, name: str, executor: PhaseExecutor
    ) -> ModuleResultEnvelope | None:
        if self._budget.is_exceeded():
            self._enter_degraded(
                f"Budget exceeded before {name}", self._infer_delivery_tier(self._state.phase)
            )
            return None

        if self._state.lease_token:
            self._lease.renew(self._state.lease_token, ttl_seconds=600)

        config = ExecutorConfig(
            run_dir=self._run_dir,
            budget_remaining=self._budget.snapshot(),
            concurrency_limit=self._adapter.get_concurrency_limit(),
            platform_rules=self._adapter.get_platform_rules(),
            event_bus=self._event_bus,
        )

        input_data = self._build_executor_input(name)
        llm_adapter = self._build_llm_adapter(name)
        started = time.monotonic()

        try:
            result = await executor.execute(input_data, llm_adapter, config)
        except Exception as exc:
            logger.exception("Executor %s raised", name)
            result = ModuleResultEnvelope(
                module_name=name,
                status="error",
                error_code="E_EXECUTOR_EXCEPTION",
                warnings=[WarningItem(code="EXCEPTION", message=str(exc))],
                data=None,
                metrics=RunMetrics(
                    wall_time_ms=int((time.monotonic() - started) * 1000),
                    llm_calls=0,
                    prompt_tokens=0,
                    completion_tokens=0,
                    estimated_cost_usd=0.0,
                ),
            )

        self._budget.record_phase(self._state.phase.value, result.metrics)
        self._store_result(name, result)
        self._log_event(
            "executor_done",
            {
                "executor": name,
                "status": result.status,
                "wall_time_ms": result.metrics.wall_time_ms,
            },
        )
        return result

    def _evaluate_edge(self, phase: Phase) -> Phase:
        for predicate, target in CONDITIONAL_EDGES.get(phase, []):
            if predicate(self._state):
                return target
        return Phase.ERROR

    def _transition(self, target: Phase) -> None:
        current = self._state.phase
        allowed = TRANSITIONS.get(current, set())
        if target not in allowed:
            self._state.phase = Phase.ERROR
            self._state.degradation_log.append(
                f"Invalid transition: {current.value} -> {target.value}"
            )
            return
        self._log_event("transition", {"from": current.value, "to": target.value})
        self._state.phase = target

    def _enter_degraded(self, reason: str, delivery_tier: str) -> None:
        self._state.degraded_mode = True
        self._state.delivery_tier = delivery_tier
        self._state.degradation_log.append(reason)
        self._emit_event(
            "degraded",
            reason,
            phase=self._state.phase.value,
            status="degraded",
            meta={"delivery_tier": delivery_tier},
        )

        # 即使进入降级模式, 也必须先执行 PHASE_G (交付打包), 确保用户始终收到产出。
        # 直接赋值绕过 TRANSITIONS 合法性校验, 因为任何阶段都应允许跳至打包兜底。
        # PHASE_G 执行后会通过 _evaluate_edge 自行转入 DEGRADED, 符合状态机语义。
        if self._state.phase != Phase.PHASE_G:
            self._state.phase = Phase.PHASE_G
        else:
            # 已在 PHASE_G 中出错, 直接降级, 避免无限循环
            if Phase.DEGRADED in TRANSITIONS.get(self._state.phase, set()):
                self._transition(Phase.DEGRADED)
            else:
                self._state.phase = Phase.DEGRADED

    def _store_result(self, executor_name: str, result: ModuleResultEnvelope) -> None:
        key_map = {
            "NeedProfileBuilder": "need_profile",
            "DiscoveryRunner": "discovery_result",
            "WorkerSupervisor": "extraction_aggregate",
            "SynthesisRunner": "synthesis_bundle",
            "SkillCompiler": "compile_bundle",
            "Validator": "validation_report",
            "DeliveryPackager": "delivery_manifest",
        }
        key = key_map.get(executor_name, executor_name)
        if result.data is None:
            self._state.phase_artifacts[key] = None
        elif hasattr(result.data, "model_dump"):
            self._state.phase_artifacts[key] = result.data.model_dump()
        else:
            self._state.phase_artifacts[key] = result.data
        self._state.phase_artifacts[f"_{executor_name}_status"] = result.status

    def _build_executor_input(self, executor_name: str) -> BaseModel:
        arts = self._state.phase_artifacts

        if executor_name == "NeedProfileBuilder":

            class RawInput(BaseModel):
                raw_input: str

            return RawInput(raw_input=self._state.raw_input)

        if executor_name == "DiscoveryRunner":
            routing = RoutingDecision(**arts.get("routing_decision", {}))
            need_profile = NeedProfile(**arts["need_profile"])
            return DiscoveryInput(
                need_profile=need_profile,
                routing=routing,
                config=DiscoveryConfig(top_k_final=routing.max_repos),
            )

        if executor_name == "WorkerSupervisor":

            class PhaseCInput(BaseModel):
                need_profile: NeedProfile
                routing: RoutingDecision
                repos: list[dict[str, Any]]
                accumulated_knowledge: list[dict[str, Any]] = []

            routing = RoutingDecision(**arts.get("routing_decision", {}))
            need_profile = NeedProfile(**arts["need_profile"])
            repos: list[dict[str, Any]] = []
            if routing.route == "DIRECT_URL":
                for index, url in enumerate(routing.repo_urls[: routing.max_repos]):
                    repos.append(
                        {
                            "candidate_id": f"url-{index}",
                            "name": url.rstrip("/").split("/")[-1],
                            "url": url,
                            "source": "direct_url",
                            "why_selected": "explicit user target",
                            "repo_type_hint": None,
                        }
                    )
            else:
                discovery = arts.get("discovery_result", {})
                for candidate in discovery.get("candidates", [])[: routing.max_repos]:
                    if not isinstance(candidate, dict):
                        continue
                    repos.append(candidate)
            return PhaseCInput(
                need_profile=need_profile,
                routing=routing,
                repos=repos[: need_profile.max_projects],
                accumulated_knowledge=arts.get("accumulated_knowledge", []),
            )

        if executor_name == "SynthesisRunner":
            need_profile = NeedProfile(**arts["need_profile"])
            discovery = DiscoveryResult(
                **arts.get("discovery_result", {"candidates": [], "search_coverage": []})
            )
            extraction = arts.get("extraction_aggregate", {})
            project_summaries: list[ExtractedProjectSummary] = []
            for envelope in extraction.get("repo_envelopes", []):
                if not isinstance(envelope, dict) or envelope.get("status") == "failed":
                    continue
                facts = envelope.get("repo_facts", {})
                repo_meta = facts.get("repo") or {}
                project_summaries.append(
                    ExtractedProjectSummary(
                        project_id=envelope.get("repo_name", "unknown"),
                        repo={
                            "repo_id": repo_meta.get(
                                "repo_id",
                                envelope.get("worker_id", envelope.get("repo_name", "unknown")),
                            ),
                            "full_name": repo_meta.get(
                                "full_name", envelope.get("repo_name", "unknown")
                            ),
                            "url": repo_meta.get(
                                "url",
                                envelope.get("repo_url", "https://github.com/unknown/unknown"),
                            ),
                            "default_branch": repo_meta.get("default_branch", "main"),
                            "commit_sha": repo_meta.get("commit_sha", "unknown"),
                            "local_path": repo_meta.get("local_path", ""),
                        },
                        top_capabilities=envelope.get("feature_inventory", [])[:5],
                        top_constraints=envelope.get("anti_patterns", [])[:3],
                        top_failures=envelope.get("anti_patterns", [])[:5],
                        evidence_refs=[],
                    )
                )
            return SynthesisInput(
                need_profile=need_profile,
                discovery_result=discovery,
                extraction_aggregate=extraction,
                project_summaries=project_summaries,
                comparison_result=CompareOutput(
                    domain_id=need_profile.domain,
                    compared_projects=[summary.project_id for summary in project_summaries],
                    signals=[],
                    metrics=CompareMetrics(
                        project_count=max(1, len(project_summaries)),
                        atom_count=0,
                        aligned_count=0,
                        missing_count=0,
                        original_count=0,
                        drifted_count=0,
                    ),
                ),
                community_knowledge=CommunityKnowledge(),
            )

        if executor_name == "SkillCompiler":
            need_profile = NeedProfile(**arts["need_profile"])
            synthesis = SynthesisReportData(**arts.get("synthesis_bundle", {}))
            validation = arts.get("validation_report", {})
            target_sections = (
                validation.get("repair_plan", []) if isinstance(validation, dict) else []
            )
            existing_sections = {}
            compile_bundle = arts.get("compile_bundle", {})
            if isinstance(compile_bundle, dict):
                existing_sections = compile_bundle.get("section_drafts", {}) or {}
            return SkillCompilerInput(
                need_profile=need_profile,
                synthesis_report=synthesis,
                platform_rules=self._adapter.get_platform_rules(),
                target_sections=target_sections,
                accumulated_knowledge=arts.get("accumulated_knowledge", []),
                existing_sections=existing_sections,
            )

        if executor_name == "Validator":
            need_profile = NeedProfile(**arts["need_profile"])
            synthesis = SynthesisReportData(**arts.get("synthesis_bundle", {}))
            compile_bundle = CompileBundleContract(**arts.get("compile_bundle", {}))
            artifact_paths = compile_bundle.artifact_paths
            return ValidationInput(
                need_profile=need_profile,
                synthesis_report=synthesis,
                compile_bundle=compile_bundle,
                skill_bundle=SkillBundlePaths(
                    skill_md_path=artifact_paths.get("SKILL.md", ""),
                    readme_md_path=artifact_paths.get("README.md", ""),
                    provenance_md_path=artifact_paths.get("PROVENANCE.md", ""),
                    limitations_md_path=artifact_paths.get("LIMITATIONS.md", ""),
                ),
                platform_rules=self._adapter.get_platform_rules(),
            )

        if executor_name == "DeliveryPackager":

            class DeliveryInput(BaseModel):
                phase_artifacts: dict[str, Any]
                degraded_mode: bool
                delivery_tier: str
                run_id: str

            return DeliveryInput(
                phase_artifacts=arts,
                degraded_mode=self._state.degraded_mode,
                delivery_tier=self._state.delivery_tier,
                run_id=self._state.run_id,
            )

        raise ValueError(f"Unsupported executor {executor_name}")

    def _build_capability_router(self):
        if CapabilityRouter is None:
            return None
        try:
            return CapabilityRouter.from_config("models.json")
        except Exception:
            return None

    def _build_llm_adapter(self, executor_name: str) -> object | None:
        if self._capability_router is None:
            return None
        task_map = {
            "NeedProfileBuilder": TASK_GENERAL,
            "WorkerSupervisor": TASK_EVIDENCE_EXTRACTION,
            "SynthesisRunner": TASK_CLAIM_SYNTHESIS,
            "SkillCompiler": TASK_CLAIM_SYNTHESIS,
        }
        task = task_map.get(executor_name)
        if not task:
            return None
        try:
            self._capability_router._current_stage = executor_name
            return self._capability_router.for_task(task)
        except Exception:
            return None

    def _build_need_profile_contract(
        self, profile: NeedProfile, routing: RoutingDecision
    ) -> NeedProfileContract:
        domain_terms = list(dict.fromkeys(profile.relevance_terms or profile.keywords[:5]))
        success_criteria = [
            "交付可注入的 SKILL.md",
            "WHY/UNSAID 足够具体",
            "用户等待后总能拿到某种产出",
        ]
        return NeedProfileContract(
            need_profile=profile,
            route_kind=routing.route,
            must_clarify=routing.route == "LOW_CONFIDENCE",
            direct_targets=routing.repo_urls,
            repo_name_candidates=routing.project_names,
            domain_terms=domain_terms[:8],
            constraints=profile.constraints,
            success_criteria=success_criteria,
            max_projects=routing.max_repos,
            delivery_expectation="full_skill"
            if routing.route != "LOW_CONFIDENCE"
            else "clarify_or_explore",
            routing=routing,
        )

    def _clarification_question(self, profile: NeedProfile, result: ModuleResultEnvelope) -> str:
        if profile.questions:
            return profile.questions[0]
        for warning in result.warnings or []:
            if warning.message.startswith("CLARIFY:"):
                return warning.message.replace("CLARIFY:", "", 1).strip()
        return "你更想分析具体项目,还是想让我先帮你找这个领域里最值得参考的项目?"

    def _load_accumulated_knowledge(self, domain: str) -> list[dict[str, Any]]:
        path = self._accumulated_file(domain)
        if not path.exists():
            return []
        items: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines()[-20:]:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return items

    def _persist_accumulated_knowledge(self) -> None:
        need_profile = self._state.phase_artifacts.get("need_profile", {})
        if not isinstance(need_profile, dict):
            return
        domain = need_profile.get("domain") or "general"
        synthesis = self._state.phase_artifacts.get("synthesis_bundle", {})
        if not isinstance(synthesis, dict):
            return
        statements: list[dict[str, Any]] = []
        for decision in synthesis.get("selected_knowledge", [])[:10]:
            if not isinstance(decision, dict):
                continue
            statement = decision.get("statement", "").strip()
            if not statement:
                continue
            statements.append(
                {
                    "statement": statement,
                    "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "source_repo": ",".join(decision.get("source_refs", [])[:3]),
                    "source_commit": "",
                    "confidence": "medium",
                }
            )
        if not statements:
            return
        path = self._accumulated_file(domain)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = set()
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    existing.add(json.loads(line).get("statement", ""))
                except json.JSONDecodeError:
                    continue
        with open(path, "a", encoding="utf-8") as handle:
            for item in statements:
                if item["statement"] in existing:
                    continue
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _accumulated_file(self, domain: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-") or "general"
        return Path.home() / ".doramagic" / "accumulated" / f"{slug}.jsonl"

    def _infer_delivery_tier(self, phase: Phase) -> str:
        mapping = {
            Phase.PHASE_B: "candidate_brief",
            Phase.PHASE_C: "repo_reports",
            Phase.PHASE_D: "repo_reports",
            Phase.PHASE_E: "synthesis_pack",
            Phase.PHASE_F: "draft_skill",
        }
        return mapping.get(phase, self._state.delivery_tier or "candidate_brief")

    def _phase_progress_pct(self, phase: Phase) -> int:
        return {
            Phase.INIT: 0,
            Phase.PHASE_A: 5,
            Phase.PHASE_A_CLARIFY: 10,
            Phase.PHASE_B: 18,
            Phase.PHASE_C: 42,
            Phase.PHASE_D: 60,
            Phase.PHASE_E: 76,
            Phase.PHASE_F: 88,
            Phase.PHASE_G: 96,
            Phase.DONE: 100,
            Phase.DEGRADED: 100,
            Phase.ERROR: 100,
        }.get(phase, 0)

    def _phase_start_message(self, phase: Phase) -> str:
        messages = {
            Phase.INIT: "准备运行计划和目录结构",
            Phase.PHASE_A: "分析输入并确定路由路径",
            Phase.PHASE_B: "执行发现阶段, 寻找候选项目",
            Phase.PHASE_C: "并行提取候选项目的设计灵魂",
            Phase.PHASE_D: "合成跨项目共识, 分歧和编译摘要",
            Phase.PHASE_E: "分 section 编译 SKILL 草稿",
            Phase.PHASE_F: "执行质量门禁并定位最弱 section",
            Phase.PHASE_G: "整理交付物并生成最终包",
        }
        return messages.get(phase, f"Starting {phase.value}")

    def _phase_complete_message(self, phase: Phase) -> str:
        if phase == Phase.PHASE_C:
            return f"提取完成: {self._state.successful_extractions} 个 repo 成功"
        if phase == Phase.PHASE_D:
            synthesis = self._state.phase_artifacts.get("synthesis_bundle", {})
            if isinstance(synthesis, dict):
                why_count = len(synthesis.get("global_theses", []))
                trap_count = len(synthesis.get("divergences", []))
                return f"合成完成: {why_count} 条 WHY, 共 {trap_count} 条风险/分歧"
        if phase == Phase.PHASE_E:
            compile_bundle = self._state.phase_artifacts.get("compile_bundle", {})
            if isinstance(compile_bundle, dict):
                return (
                    f"编译完成: {len(compile_bundle.get('section_drafts', {}))} 个 section 已生成"
                )
        if phase == Phase.PHASE_F:
            return f"质量评分: {self._state.quality_score:.1f}/100"
        return f"{phase.value} completed"

    def _build_plan_preview(self) -> str:
        return (
            "执行计划:\n"
            "1. 输入路由与必要追问\n"
            "2. 项目发现或直达提取\n"
            "3. 并行提取 WHY + UNSAID\n"
            "4. 合成并分段编译\n"
            "5. 质量门禁与打包交付\n"
            "预计耗时: 2-5 分钟"
        )

    async def _send_progress(self, *, phase: str, status: str, message: str, percent: int) -> None:
        with contextlib.suppress(Exception):
            await self._adapter.send_progress(
                ProgressUpdate(
                    phase=phase,
                    status=status,
                    message=message,
                    elapsed_ms=self._budget.elapsed_ms(),
                    percent_complete=percent,
                )
            )

    def _emit_event(
        self,
        event_type: str,
        message: str,
        *,
        phase: str,
        worker_id: str | None = None,
        status: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        self._event_bus.emit(
            event_type,
            message,
            phase=phase,
            worker_id=worker_id,
            status=status,
            meta=meta,
        )

    def _save_state(self) -> None:
        state_path = self._run_dir / "controller_state.json"
        payload = json.dumps(self._state.to_dict(), ensure_ascii=False, indent=2)
        with open(state_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

    def _load_state(self, run_id: str) -> ControllerState | None:
        state_file = self._run_dir / "controller_state.json"
        if not state_file.exists():
            return None
        try:
            return ControllerState.from_dict(json.loads(state_file.read_text(encoding="utf-8")))
        except Exception:
            return None

    def _setup_directories(self) -> None:
        for name in ("staging", "delivery", "leases", "workers", "checkpoints"):
            (self._run_dir / name).mkdir(parents=True, exist_ok=True)

    def _create_error_state(self, message: str) -> ControllerState:
        state = ControllerState(run_id="error", phase=Phase.ERROR)
        state.degradation_log.append(message)
        return state

    def _log_event(self, event_type: str, data: dict[str, Any]) -> None:
        self._run_log.append(
            {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "event": event_type,
                "phase": self._state.phase.value,
                **data,
            }
        )

    def _write_run_log(self) -> None:
        log_path = self._run_dir / "run_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as handle:
            for entry in self._run_log:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._run_log.clear()
