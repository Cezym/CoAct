import os
import sys

import yaml

from src.crew import DevelopersCrew


def run():
    print("## Welcome to the CoAct")
    print("-------------------------------")

    inputs = {"task": "Write best script (role, goal, backstory) for AI agent that will write best tests for given code."}#input("write instructions:")}
    final_answer = DevelopersCrew().crew().kickoff(inputs=inputs)

    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("final code:...")
    print("\n\n########################")
    print(final_answer)


def train():
    """
    Train the crew for a given number of iterations.
    """

    with open(
        "src/game_builder_crew/config/gamedesign.yaml", "r", encoding="utf-8"
    ) as file:
        examples = yaml.safe_load(file)

    inputs = {"game": examples["example1_pacman"]}
    try:
        DevelopersCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


if __name__ == "__main__":
    os.environ["OTEL_SDK_DISABLED"] = "true"  # Turn off telemetry
    os.environ["CREWAI_TRACING_ENABLED"] = "false" # Turn off tracing
    run()
