"""Command‑line interface for the CoAct system."""

import argparse
import os
from pathlib import Path

from crewai import Process, Crew

from crew.developers_crew import DevelopersCrew
from crew.evaluation_crew import CodeEvaluationCrew


def _set_async_mode(crew: Crew, async_enabled: bool) -> None:
    """If `async_enabled` is True, mark every task as async."""
    if not async_enabled:
        return
    for t in crew.tasks:
        t.async_execution = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="coact",
        description=(
            "Co‑Act: a multi‑agent system that writes code and evaluates it.\n"
            "Choose execution strategy with --mode (sequential|parallel).\n"
            "Add --evaluate to run the CodeEvaluationCrew after the main crew."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "parallel"],
        default="sequential",
        help="How tasks are executed. 'parallel' uses async IO.",
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help=(
            "Run the CodeEvaluationCrew after the main crew has finished.\n"
            "Useful for generating a quality report."
        ),
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default="config",
        help="Directory containing agents.yaml & tasks.yaml (default: ./config)",
    )
    return parser.parse_args()


def run_cli() -> None:
    args = parse_args()

    # Turn off telemetry by default – can be overridden via env vars.
    os.environ.setdefault("OTEL_SDK_DISABLED", "true")
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

    # Resolve config dir relative to project root
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    config_dir = PROJECT_ROOT / args.config_dir

    # ---------- MAIN CREW ----------
    dev_crew = DevelopersCrew()
    crew_main = dev_crew.crew()

    crew_main.process = Process.sequential
    if args.mode == "parallel":
        _set_async_mode(crew_main, async_enabled=True)

    print("\n>>> Running DevelopersCrew ...")
    inputs_main = {"task": (
        "Write a script (role, goal, backstory) that will write best tests "
        "for the given code."
    )}
    result_main = crew_main.kickoff(inputs=inputs_main)
    print("=== MAIN RESULT ===")
    print(result_main)

    # ---------- OPTIONAL EVALUATION ----------
    if args.evaluate:
        eval_crew_obj = CodeEvaluationCrew()
        eval_crew_obj._agents_cfg_path = str(config_dir / "agents.yaml")
        eval_crew_obj._tasks_cfg_path   = str(config_dir / "tasks.yaml")

        crew_eval = eval_crew_obj.crew()

        crew_eval.process = Process.sequential

        if args.mode == "parallel":
            _set_async_mode(crew_eval, async_enabled=True)

        print("\n>>> Running CodeEvaluationCrew ...")
        eval_inputs = {"code": result_main}

        result_eval = crew_eval.kickoff(inputs=eval_inputs)
        print("=== EVALUATION RESULT ===")
        print(result_eval)

    # Exit status
    exit_code = 0
    if "error" in str(result_main).lower():
        exit_code = 1
    if args.evaluate and ("error" in str(result_eval).lower()):
        exit_code = 1

    raise SystemExit(exit_code)
