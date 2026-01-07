from crew import CodeEvaluationCrew


def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

code_path = "../game.py"
code = load_file(code_path)

inputs = {
    "code": code,
}

crew = CodeEvaluationCrew().crew()
result = crew.kickoff(inputs=inputs)
print(result)