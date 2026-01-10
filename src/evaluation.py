import os

from crew import CodeEvaluationCrew


def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

code_path = "../game.py"
code = load_file(code_path)

inputs = {
    "code": code,
}

os.environ["OTEL_SDK_DISABLED"] = "true"  # Turn off telemetry
os.environ["CREWAI_TRACING_ENABLED"] = "false"  # Turn off tracing

crew = CodeEvaluationCrew().crew()
result = crew.kickoff(inputs=inputs)
print(result)