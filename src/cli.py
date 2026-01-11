"""Command‑line interface for the CoAct system."""

import argparse
import os
import re
import time
from pathlib import Path

from crewai import Process, Crew
from crewai.types.streaming import CrewStreamingOutput

from crew.developers_crew import DevelopersCrew
from crew.evaluation_crew import CodeEvaluationCrew


def _set_async_mode(crew: Crew, async_enabled: bool) -> None:
    """If `async_enabled` is True, mark every task as async."""
    if not async_enabled:
        return
    for t in crew.tasks:
        t.async_execution = True


def _set_verbose_mode(crew: Crew, verobse_enabled: bool) -> None:
    """If `verbose_enabled` is True, mark verbose for every agent as True."""
    if not verobse_enabled:
        return
    crew.verbose = True
    for a in crew.agents:
        a.verbose = True


def _set_memory(crew: Crew, memory_enabled: bool) -> None:
    """If `memory_enabled` is True, enable memory for crew."""
    if not memory_enabled:
        return
    crew.memory = True


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
    parser.add_argument(
        "--input",
        type=str,
        help="Input prompt for DevelopersCrew.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print debug info.")
    parser.add_argument(
        "--memory", action="store_true", help="Enable memory for crews."
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
    if args.verbose:
        _set_verbose_mode(crew_main, verobse_enabled=True)
    if args.memory:
        _set_memory(crew_main, memory_enabled=True)

    print("\n>>> Running DevelopersCrew ...")

    input_prompt = args.input

    if not input_prompt:
        input_prompt = input("Enter your task: ")

    inputs_main = {"task": input_prompt}
    result_main = crew_main.kickoff(inputs=inputs_main)
    print("=== MAIN RESULT ===")
    print(result_main)

    # ---------- OPTIONAL EVALUATION ----------
    if args.evaluate:
        eval_crew_obj = CodeEvaluationCrew()
        eval_crew_obj._agents_cfg_path = str(config_dir / "agents.yaml")
        eval_crew_obj._tasks_cfg_path = str(config_dir / "tasks.yaml")

        crew_eval = eval_crew_obj.crew()

        crew_eval.process = Process.sequential

        if args.mode == "parallel":
            _set_async_mode(crew_eval, async_enabled=True)
        if args.verbose:
            _set_verbose_mode(crew_eval, verobse_enabled=True)
        if args.memory:
            _set_memory(crew_eval, memory_enabled=True)

        print("\n>>> Running CodeEvaluationCrew ...")
        eval_inputs = {"code": str(result_main)}

        result_eval = crew_eval.kickoff(inputs=eval_inputs)
        print("=== EVALUATION RESULT ===")

        print("Summary:")
        print(result_eval)

        while isinstance(result_eval, CrewStreamingOutput):  # For syncing output
            time.sleep(1)
        time.sleep(3)  # Synching with output
        print("Details:")
        sum = 0
        for task in crew_eval.tasks:
            title = f"===== {task.name.split('_')[0].title()} ====="
            print(title)
            print(task.output)
            if title == "Summary":
                continue
            try:
                points_given = int(
                    re.search(r"Points given:\s*(\d)\s*-", str(task.output)).group(1)
                )
            except AttributeError:
                points_given = int(re.search(r".+(\d)\s*-", str(task.output)).group(1))
            sum += points_given
        print("Total points: ", sum)
        print("Average: ", sum / 10)

    # Exit status
    exit_code = 0
    if "error" in str(result_main).lower():
        exit_code = 1
    if args.evaluate and ("error" in str(result_eval).lower()):
        exit_code = 1

    raise SystemExit(exit_code)
