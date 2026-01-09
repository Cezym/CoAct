# pip install deepeval

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import OllamaModel
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams

from src.crew import DevelopersCrew


def test_deepeval():
    inputs = {
        "task": "Write Pacman game in python"}
    final_answer = DevelopersCrew().crew().kickoff(inputs=inputs)
    actual_output = str(final_answer)

    ollama_llm = OllamaModel(model="llama3.1:8b", temperature=0.0)

    readability_metric = GEval(
        name="Readability",
        criteria="Determine if the script is easy to read, follows best coding practices, and has clear variable names with no duplicates.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7,
        model=ollama_llm,
        async_mode=False
    )

    test_case = LLMTestCase(
        input=inputs["task"],
        actual_output=actual_output,
    )

    # Obowiązkowe: oblicz score
    readability_metric.measure(test_case)

    # Opcjonalnie: wyświetl score
    print(f"Readability Score: {readability_metric.score}")
    print(f"Reason: {readability_metric.reason}")

    # assert_test rzuci błąd, jeśli score < threshold
    assert_test(test_case, [readability_metric])

# Uruchomienie: deepeval test run nazwa_pliku.py
