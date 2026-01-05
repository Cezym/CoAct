from crew import CodeEvaluationCrew
import os

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

code_path = "../game.py"
rules = load_file("../config/evaluation_rules.txt")
code = load_file(code_path)

inputs = {
    "rules": rules,
    "code": code
}

crew = CodeEvaluationCrew().crew()
result = crew.kickoff(inputs=inputs)
print(result)