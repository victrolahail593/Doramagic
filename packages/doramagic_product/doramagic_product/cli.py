"""Doramagic CLI entry point.

Provides the `doramagic` command after `pip install doramagic`.
Delegates to the same logic used by SKILL.md scripts.

Note: This module deliberately avoids importing doramagic_product.pipeline
at module level because pipeline.py has heavy dependencies that may not be
available in all contexts (e.g., run_skill_compiler).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def _resolve_knowledge_dir() -> None:
    """Set DORAMAGIC_BRICKS_DIR from pip-installed package data if not already set."""
    if os.environ.get("DORAMAGIC_BRICKS_DIR"):
        return
    try:
        from importlib.resources import files

        knowledge_root = files("doramagic_knowledge")
        bricks_dir = knowledge_root / "bricks"
        if bricks_dir.is_dir():
            os.environ["DORAMAGIC_BRICKS_DIR"] = str(bricks_dir)
    except (ImportError, TypeError, FileNotFoundError):
        pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Doramagic — Knowledge extraction and skill forging",
    )
    parser.add_argument("--input", "-i", type=str, default="", help="User input text")
    parser.add_argument(
        "--continue",
        dest="continue_run",
        type=str,
        default=None,
        help="Resume a previous run by run_id",
    )
    parser.add_argument(
        "--run-dir", type=str, default=None, help="Run directory (default: ~/.doramagic/runs/)"
    )
    parser.add_argument("--cli", action="store_true", help="Use CLI adapter instead of OpenClaw")
    parser.add_argument(
        "--platform-rules", type=str, default=None, help="Path to platform_rules.json"
    )
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls, use mock data")
    parser.add_argument(
        "--status", type=str, default=None, help="Show status for latest run or the given run_id"
    )
    parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Run pipeline in background, return immediately with run_id",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    args = parser.parse_args()

    if args.version:
        print(f"doramagic {_get_version()}")
        return

    _is_forked_child = False

    # Resolve knowledge directory from package data
    _resolve_knowledge_dir()

    from doramagic_contracts.budget import BudgetPolicy
    from doramagic_controller.flow_controller import FlowController

    if args.cli:
        from doramagic_controller.adapters.cli import CLIAdapter

        adapter = CLIAdapter(
            storage_root=Path(args.run_dir).expanduser() if args.run_dir else None,
            platform_rules_path=Path(args.platform_rules) if args.platform_rules else None,
        )
    else:
        from doramagic_controller.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter(
            storage_root=Path(args.run_dir).expanduser() if args.run_dir else None,
            platform_rules_path=Path(args.platform_rules) if args.platform_rules else None,
        )

    if args.status is not None or args.input.strip() == "/dora-status":
        run_base = Path(args.run_dir).expanduser() if args.run_dir else adapter.get_storage_root()
        payload = _build_status_payload(run_base, args.status)
        print(json.dumps(payload, ensure_ascii=False))
        return

    run_base = Path(args.run_dir).expanduser() if args.run_dir else adapter.get_storage_root()

    if args.continue_run:
        run_dir = run_base / args.continue_run
    else:
        run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_dir = run_base / run_id

    if args.async_mode:
        run_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            print(
                json.dumps(
                    {
                        "message": "Async mode is not supported on Windows.",
                        "error": True,
                    }
                )
            )
            sys.exit(1)
        pid = os.fork()
        if pid > 0:
            print(
                json.dumps(
                    {
                        "message": (
                            f"✨ 正在后台分析中，预计需要 1-3 分钟。\n\n"
                            f"运行编号: `{run_dir.name}`\n\n"
                            f"完成后可用 `/dora-status` 查看结果。"
                        ),
                        "run_id": run_dir.name,
                        "async": True,
                    },
                    ensure_ascii=False,
                )
            )
            return
        else:
            sys.stdout = open(os.devnull, "w")  # noqa: SIM115
            sys.stderr = open(run_dir / "stderr.log", "w")  # noqa: SIM115
            os.setsid()
            _is_forked_child = True

    from doramagic_executors import ALL_EXECUTORS

    executors = {name: cls() for name, cls in ALL_EXECUTORS.items()}

    controller = FlowController(
        adapter=adapter,
        run_dir=run_dir,
        executors=executors,
        budget_policy=BudgetPolicy(),
    )

    try:
        result = asyncio.run(
            controller.run(
                user_input=args.input,
                resume_run_id=args.continue_run,
            )
        )
    except KeyboardInterrupt:
        print(json.dumps({"message": "Interrupted", "error": True}))
        if _is_forked_child:
            os._exit(1)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"message": f"Fatal error: {e}", "error": True}))
        if _is_forked_child:
            os._exit(1)
        sys.exit(1)

    if result.phase.value in ("DONE", "DEGRADED"):
        delivery_dir = run_dir / "delivery"
        msg = _build_rich_message(result, delivery_dir)
        artifacts = {}
        if delivery_dir.exists():
            for f in delivery_dir.iterdir():
                artifacts[f.name] = f
        asyncio.run(adapter.send_output(msg, artifacts))
    elif result.phase.value == "PHASE_A_CLARIFY":
        pass
    else:
        print(
            json.dumps(
                {
                    "message": (
                        f"Pipeline failed: {', '.join(result.degradation_log) or 'unknown error'}"
                    ),
                    "error": True,
                }
            )
        )
        if _is_forked_child:
            os._exit(1)
        sys.exit(1)

    if _is_forked_child:
        os._exit(0)


def _get_version() -> str:
    try:
        from importlib.metadata import version

        return version("doramagic")
    except Exception:
        return "unknown"


def _build_rich_message(result, delivery_dir: Path) -> str:
    arts = result.phase_artifacts
    lines = ["## Doramagic 道具锻造完成！", ""]

    np = arts.get("need_profile", {})
    topic = np.get("intent", "") if isinstance(np, dict) else ""
    if topic:
        lines.append(f"**主题**: {topic}")
        lines.append("")

    discovery = arts.get("discovery_result", {})
    extraction = arts.get("extraction_aggregate", {})
    candidates = discovery.get("candidates", []) if isinstance(discovery, dict) else []
    envelopes = extraction.get("repo_envelopes", []) if isinstance(extraction, dict) else []
    successful = [
        env.get("repo_name", "?")
        for env in envelopes
        if isinstance(env, dict) and env.get("status") != "failed"
    ]

    github_count = sum(
        1 for c in candidates if isinstance(c, dict) and c.get("type") == "github_repo"
    )
    skill_count = sum(
        1 for c in candidates if isinstance(c, dict) and c.get("type") == "community_skill"
    )

    lines.append(
        f"**来源**: {len(successful)} 个项目分析完成 "
        f"({github_count} GitHub, {skill_count} ClawHub/本地)"
    )
    lines.append("")

    if successful:
        lines.append("**分析项目**:")
        for repo_id in successful[:5]:
            lines.append(f"  - {repo_id}")
        lines.append("")

    synthesis = arts.get("synthesis_bundle", {})
    consensus = (
        synthesis.get("selected_knowledge", synthesis.get("consensus", []))
        if isinstance(synthesis, dict)
        else []
    )
    whys = [
        d.get("statement", "") if isinstance(d, dict) else str(d)
        for d in consensus
        if isinstance(d, dict) and "[TRAP]" not in d.get("statement", "")
    ]
    if whys:
        lines.append("**WHY — 设计智慧**:")
        for w in whys[:3]:
            lines.append(f"  - {w}")
        lines.append("")

    traps = [
        d.get("statement", "").replace("[TRAP] ", "") if isinstance(d, dict) else str(d)
        for d in consensus
        if isinstance(d, dict) and "[TRAP]" in d.get("statement", "")
    ]
    if traps:
        lines.append("**UNSAID — 隐藏陷阱**:")
        for t in traps[:3]:
            lines.append(f"  - {t}")
        lines.append("")

    if delivery_dir.exists():
        lines.append(f"**交付物**: `{delivery_dir}`")
        lines.append("")

    if result.degradation_log:
        lines.append("**注意** (降级模式):")
        for d in result.degradation_log[:3]:
            lines.append(f"  - {d}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by Doramagic v{_get_version()} — 不教用户做事，给他工具。*")

    return "\n".join(lines)


def _build_status_payload(run_base: Path, run_id: str | None) -> dict:
    import re as _re

    if run_id and run_id.strip():
        clean_id = run_id.strip()
        if not _re.match(r"^run-[\d-]+$", clean_id):
            return {"message": f"Invalid run ID format: {clean_id}", "error": True}
        target = run_base / clean_id
    else:
        runs = sorted(run_base.glob("run-*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not runs:
            return {"message": "没有找到任何运行记录。", "status": "empty"}
        target = runs[0]

    state_file = target / "state.json"
    if not state_file.exists():
        return {"message": f"运行 `{target.name}` 没有状态文件。", "status": "unknown"}

    import json as _json

    state = _json.loads(state_file.read_text(encoding="utf-8"))
    phase = state.get("phase", "unknown")
    return {
        "run_id": target.name,
        "phase": phase,
        "message": f"运行 `{target.name}` 当前阶段: {phase}",
        "status": "done" if phase in ("DONE", "DEGRADED") else "running",
    }


if __name__ == "__main__":
    main()
