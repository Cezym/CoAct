import os
import sys

import yaml

from src.crew import DevelopersCrew


def run():
    print("## Welcome to the CoAct")
    print("-------------------------------")

    inputs = {"task": input("write instructions:")}
    developers_crew = DevelopersCrew().crew()
    final_answer = developers_crew.kickoff(inputs=inputs)
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("final code:...")
    print("\n\n########################")
    tasks = {task.name: task for task in developers_crew.tasks}
    print(tasks)
    print(final_answer)

if __name__ == "__main__":
    run()
