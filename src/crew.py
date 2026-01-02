import yaml
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, llm


@CrewBase
class DevelopersCrew:
    """Developers crew"""

    agents_config = "../config/agents.yaml"
    tasks_config = "../config/tasks.yaml"

    @staticmethod
    def load_yaml(file_path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    llm_providers_config = load_yaml("../config/llm_providers.yaml")

    @llm
    def local_gpt_oss_20b(self):
        return LLM(**DevelopersCrew.llm_providers_config["local_gpt_oss_20b"])

    @llm
    def local_llama3_1_8b(self):
        return LLM(**DevelopersCrew.llm_providers_config["local_llama3_1_8b"])

    @agent
    def clarifier(self) -> Agent:
        return Agent(
            config=self.agents_config["clarifier"],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def senior_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_engineer_agent"],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["chief_qa_engineer_agent"],
            allow_delegation=True,
            verbose=True,
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
            config = self.tasks_config["review_task"],
            agent = self.qa_engineer_agent(),
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
        """Creates the GameBuilderCrew"""
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
from crewai.project import CrewBase, agent, crew, task, llm
from crewai import LLM

@CrewBase
class CodeEvaluationCrew:
    """Code Evaluation Crew"""

    agents_config = "../config/agents.yaml"
    tasks_config = "../config/tasks.yaml"

    @llm
    def local_codegemma_7b(self):
        return LLM(**DevelopersCrew.llm_providers_config["local_codegemma_7b"])

    @agent
    def readability_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["readability_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def documentation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["documentation_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def functional_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["functional_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def tests_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["tests_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def complexity_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["complexity_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def duplication_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["duplication_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def performance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["performance_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def security_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["security_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def maintainability_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["maintainability_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def compliance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["compliance_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @agent
    def summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["summary_agent"],
            llm=self.codegemma(),
            verbose=True
        )

    @task
    def readability_task(self) -> Task:
        return Task(
            config=self.tasks_config["readability_task"],
            agent=self.readability_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["readability_task"]["description"],
            expected_output=self.tasks_config["readability_task"]["expected_output"]
        )

    @task
    def documentation_task(self) -> Task:
        return Task(
            config=self.tasks_config["documentation_task"],
            agent=self.documentation_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["documentation_task"]["description"],
            expected_output=self.tasks_config["documentation_task"]["expected_output"]
        )

    @task
    def functional_task(self) -> Task:
        return Task(
            config=self.tasks_config["functional_task"],
            agent=self.functional_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["functional_task"]["description"],
            expected_output=self.tasks_config["functional_task"]["expected_output"]
        )

    @task
    def tests_task(self) -> Task:
        return Task(
            config=self.tasks_config["tests_task"],
            agent=self.tests_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["tests_task"]["description"],
            expected_output=self.tasks_config["tests_task"]["expected_output"]
        )

    @task
    def complexity_task(self) -> Task:
        return Task(
            config=self.tasks_config["complexity_task"],
            agent=self.complexity_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["complexity_task"]["description"],
            expected_output=self.tasks_config["complexity_task"]["expected_output"]
        )

    @task
    def duplication_task(self) -> Task:
        return Task(
            config=self.tasks_config["duplication_task"],
            agent=self.duplication_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["duplication_task"]["description"],
            expected_output=self.tasks_config["duplication_task"]["expected_output"]
        )

    @task
    def performance_task(self) -> Task:
        return Task(
            config=self.tasks_config["performance_task"],
            agent=self.performance_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["performance_task"]["description"],
            expected_output=self.tasks_config["performance_task"]["expected_output"]
        )

    @task
    def security_task(self) -> Task:
        return Task(
            config=self.tasks_config["security_task"],
            agent=self.security_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["security_task"]["description"],
            expected_output=self.tasks_config["security_task"]["expected_output"]
        )

    @task
    def maintainability_task(self) -> Task:
        return Task(
            config=self.tasks_config["maintainability_task"],
            agent=self.maintainability_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["maintainability_task"]["description"],
            expected_output=self.tasks_config["maintainability_task"]["expected_output"]
        )

    @task
    def compliance_task(self) -> Task:
        return Task(
            config=self.tasks_config["compliance_task"],
            agent=self.compliance_agent(),
            description="{rules}\n\nCode to evaluate:\n{code}\n\n" + self.tasks_config["compliance_task"]["description"],
            expected_output=self.tasks_config["compliance_task"]["expected_output"]
        )

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
            ]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )