import math

from crewai import Agent, Crew, Task, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai.tools import tool
import yaml

def load_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


llm_providers_config = load_yaml("../config/llm_providers.yaml")
LLMS = {}

for llm in llm_providers_config:
    print(f"{llm=}")
    print(f"{llm_providers_config[llm]=}")
    LLMS[llm] = LLM(**llm_providers_config[llm])


@CrewBase
class DevelopersCrew:
    """Developers crew"""

    agents_config = "../config/agents.yaml"
    tasks_config = "../config/tasks.yaml"

    @agent
    def clarifier(self) -> Agent:
        return Agent(
            config=self.agents_config["clarifier"],
            allow_delegation=False,
            verbose=True,
            llm=LLMS[self.agents_config["clarifier"]["llm_model"]],
        )

    @agent
    def senior_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            allow_delegation=False,
            verbose=True,
            llm=LLMS[self.agents_config["coder"]["llm_model"]],
        )

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            allow_delegation=False,
            verbose=True,
            llm=LLMS[self.agents_config["coder"]["llm_model"]],
        )

    @agent
    def qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_engineer_agent"],
            allow_delegation=False,
            verbose=True,
            llm=LLMS[self.agents_config["qa_engineer_agent"]["llm_model"]],
        )

    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["chief_qa_engineer_agent"],
            allow_delegation=False,
            verbose=True,
            llm=LLMS[self.agents_config["chief_qa_engineer_agent"]["llm_model"]],
        )

    @task
    def clarifier_task(self) -> Task:
        return Task(
            name="clarifier_task",
            config=self.tasks_config["clarifier_task"],
            agent=self.clarifier(),
        )

    @task
    def code_task(self) -> Task:
        return Task(
            name="code_task",
            config=self.tasks_config["code_task"],
            agent=self.coder(),
        )

    @task
    def review_task(self) -> Task:
        return Task(
            name="review_task",
            config=self.tasks_config["review_task"],
            agent=self.qa_engineer_agent(),
            #### output_json=ResearchRoleRequirements
        )

    @task
    def evaluate_task(self) -> Task:
        return Task(
            name="evaluate_task",
            config=self.tasks_config["evaluate_task"],
            agent=self.chief_qa_engineer_agent(),
        )

    @task
    def human_input_evaluation_task(self):
        return Task(
            name="human_input_evaluation_task",
            config=self.tasks_config["human_input_evaluation_task"],
            agent=self.chief_qa_engineer_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DevelopersCrew"""
        for agent in self.agents:
            print(agent)
        print()
        for task in self.tasks:
            print(task)
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=False,
            embedder=DevelopersCrew.llm_providers_config["memory_embedder"]
        )


import yaml
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class CodeEvaluationCrew:
    """Code Evaluation Crew"""

    agents_config = "../config/agents.yaml"
    tasks_config = "../config/tasks.yaml"

    @agent
    def readability_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["readability_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["readability_agent"]["llm_model"]],
        )

    @agent
    def documentation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["documentation_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["documentation_agent"]["llm_model"]],
        )

    @agent
    def functional_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["functional_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["functional_agent"]["llm_model"]],
        )

    @agent
    def tests_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["tests_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["tests_agent"]["llm_model"]],
        )

    @agent
    def complexity_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["complexity_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["complexity_agent"]["llm_model"]],
        )

    @agent
    def duplication_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["duplication_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["duplication_agent"]["llm_model"]],
        )

    @agent
    def performance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["performance_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["performance_agent"]["llm_model"]],
        )

    @agent
    def security_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["security_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["security_agent"]["llm_model"]],
        )

    @agent
    def maintainability_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["maintainability_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["maintainability_agent"]["llm_model"]],
        )

    @agent
    def compliance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["compliance_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["compliance_agent"]["llm_model"]],
        )

    @agent
    def summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["summary_agent"],
            verbose=True,
            llm=LLMS[self.agents_config["summary_agent"]["llm_model"]],
        )

    @task
    def readability_task(self) -> Task:
        return Task(
            config=self.tasks_config["readability_task"],
            agent=self.readability_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["readability_task"]["description"],
            expected_output=self.tasks_config["readability_task"]["expected_output"]
        )

    @task
    def documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config["documentation_task"],
            agent=self.documentation_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["documentation_task"]["description"],
            expected_output=self.tasks_config["documentation_task"]["expected_output"]
        )

    @task
    def functional_task(self) -> Task:
        return Task(
            config=self.tasks_config["functional_task"],
            agent=self.functional_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["functional_task"]["description"],
            expected_output=self.tasks_config["functional_task"]["expected_output"]
        )

    @task
    def tests_task(self) -> Task:
        return Task(
            config=self.tasks_config["tests_task"],
            agent=self.tests_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["tests_task"]["description"],
            expected_output=self.tasks_config["tests_task"]["expected_output"]
        )

    @task
    def complexity_task(self) -> Task:
        return Task(
            config=self.tasks_config["complexity_task"],
            agent=self.complexity_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["complexity_task"]["description"],
            expected_output=self.tasks_config["complexity_task"]["expected_output"]
        )

    @task
    def duplication_task(self) -> Task:
        return Task(
            config=self.tasks_config["duplication_task"],
            agent=self.duplication_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["duplication_task"]["description"],
            expected_output=self.tasks_config["duplication_task"]["expected_output"]
        )

    @task
    def performance_task(self) -> Task:
        return Task(
            config=self.tasks_config["performance_task"],
            agent=self.performance_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["performance_task"]["description"],
            expected_output=self.tasks_config["performance_task"]["expected_output"]
        )

    @task
    def security_task(self) -> Task:
        return Task(
            config=self.tasks_config["security_task"],
            agent=self.security_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["security_task"]["description"],
            expected_output=self.tasks_config["security_task"]["expected_output"]
        )

    @task
    def maintainability_task(self) -> Task:
        return Task(
            config=self.tasks_config["maintainability_task"],
            agent=self.maintainability_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["maintainability_task"]["description"],
            expected_output=self.tasks_config["maintainability_task"]["expected_output"]
        )

    @task
    def compliance_task(self) -> Task:
        return Task(
            config=self.tasks_config["compliance_task"],
            agent=self.compliance_agent(),
            description="Code to evaluate:\n{code}\n\n" + self.tasks_config["compliance_task"]["description"],
            expected_output=self.tasks_config["compliance_task"]["expected_output"]
        )
    @staticmethod
    @tool("Average tool")
    def average_tool(numbers: list) -> str:
        """Useful for when you need to get average of a list of numbers."""
        return str(sum(numbers)/len(numbers))

    @staticmethod
    @tool("Sum tool")
    def sum_tool(numbers: list) -> str:
        """Useful for when you need to get sum of a list of numbers."""
        return str(sum(numbers))

    @task
    def summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["summary_task"],
            agent=self.summary_agent(),
            context=[
                self.readability_task(),
                self.documentation_task(),
                self.functional_task(),
                self.tests_task(),
                self.complexity_task(),
                self.duplication_task(),
                self.performance_task(),
                self.security_task(),
                self.maintainability_task(),
                self.compliance_task()
            ],
            tools=[self.average_tool, self.sum_tool]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
