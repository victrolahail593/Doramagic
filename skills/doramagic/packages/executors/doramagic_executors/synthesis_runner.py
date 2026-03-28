"""Phase D executor: synthesize worker envelopes into compile-ready bundles."""

from __future__ import annotations

import time

from pydantic import BaseModel

from doramagic_contracts.cross_project import SynthesisDecision, SynthesisInput, SynthesisReportData
from doramagic_contracts.envelope import ModuleResultEnvelope, RunMetrics, WarningItem


class SynthesisRunner:
    async def execute(self, input: BaseModel, adapter: object, config) -> ModuleResultEnvelope[SynthesisReportData]:
        started = time.monotonic()
        if not isinstance(input, SynthesisInput):
            return ModuleResultEnvelope(
                module_name="SynthesisRunner",
                status="error",
                error_code="E_INPUT_INVALID",
                warnings=[WarningItem(code="TYPE", message="Expected SynthesisInput")],
                data=None,
                metrics=self._metrics(started),
            )

        aggregate = input.extraction_aggregate.model_dump() if hasattr(input.extraction_aggregate, "model_dump") else input.extraction_aggregate or {}
        envelopes = aggregate.get("repo_envelopes", [])
        decisions = []
        provenance = {}
        divergences = []
        for index, envelope in enumerate(envelopes):
            if not isinstance(envelope, dict) or envelope.get("status") == "failed":
                continue
            repo_name = envelope.get("repo_name", f"repo-{index}")
            design_philosophy = envelope.get("design_philosophy") or "[NO_DATA]"
            mental_model = envelope.get("mental_model") or "[NO_DATA]"
            why_items = envelope.get("why_hypotheses", [])[:3] or [design_philosophy]
            trap_items = envelope.get("anti_patterns", [])[:3]

            decisions.append(
                SynthesisDecision(
                    decision_id=f"why-{index:03d}",
                    statement=design_philosophy,
                    decision="include",
                    rationale=mental_model,
                    source_refs=[envelope.get("repo_url", "")],
                    demand_fit="high",
                )
            )
            for sub_index, item in enumerate(why_items[:2]):
                decisions.append(
                    SynthesisDecision(
                        decision_id=f"why-{index:03d}-{sub_index:02d}",
                        statement=item,
                        decision="include",
                        rationale=f"Derived from {repo_name}",
                        source_refs=[envelope.get("repo_url", "")],
                        demand_fit="medium",
                    )
                )
            for sub_index, trap in enumerate(trap_items[:2]):
                divergences.append(f"{repo_name}: {trap}")
                decisions.append(
                    SynthesisDecision(
                        decision_id=f"trap-{index:03d}-{sub_index:02d}",
                        statement=f"[TRAP] {trap}",
                        decision="include",
                        rationale=f"Observed risk from {repo_name}",
                        source_refs=[envelope.get("repo_url", "")],
                        demand_fit="high",
                    )
                )
            provenance[repo_name] = [envelope.get("repo_url", "")]

        # Mark repos where all key fields are placeholder as partial
        for index2, envelope2 in enumerate(envelopes):
            if not isinstance(envelope2, dict) or envelope2.get("status") == "failed":
                continue
            dp2 = envelope2.get("design_philosophy") or "[NO_DATA]"
            mm2 = envelope2.get("mental_model") or "[NO_DATA]"
            if dp2 == "[NO_DATA]" and mm2 == "[NO_DATA]" and not envelope2.get("why_hypotheses"):
                envelope2["_synthesis_status"] = "partial"

        compile_brief = {
            "role": [input.need_profile.intent],
            "knowledge": [decision.statement for decision in decisions if "[TRAP]" not in decision.statement][:8],
            "workflow": [f"Start from {input.need_profile.intent}", "Apply extracted WHY before generic advice"],
            "anti_patterns": [decision.statement for decision in decisions if "[TRAP]" in decision.statement][:6],
        }

        report = SynthesisReportData(
            consensus=decisions[:8],
            conflicts=[],
            unique_knowledge=decisions[8:12],
            selected_knowledge=decisions,
            excluded_knowledge=[],
            open_questions=[] if decisions else ["No synthesis decisions generated."],
            global_theses=[decision.statement for decision in decisions[:5]],
            common_why=[decision.statement for decision in decisions if "[TRAP]" not in decision.statement][:6],
            divergences=divergences[:6],
            source_provenance_matrix=provenance,
            unknowns=[],
            compile_ready=len(decisions) >= 2,
            compile_brief_by_section=compile_brief,
        )

        status = "ok" if report.compile_ready else "blocked"
        warnings = []
        if not report.compile_ready:
            warnings.append(WarningItem(code="COMPILE_NOT_READY", message="Synthesis did not produce enough concrete knowledge"))

        return ModuleResultEnvelope(
            module_name="SynthesisRunner",
            status=status,
            warnings=warnings,
            data=report,
            metrics=self._metrics(started),
        )

    def _metrics(self, started: float) -> RunMetrics:
        return RunMetrics(
            wall_time_ms=int((time.monotonic() - started) * 1000),
            llm_calls=0,
            prompt_tokens=0,
            completion_tokens=0,
            estimated_cost_usd=0.0,
        )

    def validate_input(self, input: BaseModel) -> list[str]:
        if not isinstance(input, SynthesisInput):
            return ["SynthesisRunner expects SynthesisInput"]
        return []

    def can_degrade(self) -> bool:
        return True
