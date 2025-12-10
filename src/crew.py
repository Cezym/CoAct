import yaml
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, llm
from crewai.rag.embeddings.providers.ollama.types import OllamaProviderSpec


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
        return Task(config=self.tasks_config["clarifier_task"], agent=self.clarifier())

    @task
    def code_task(self) -> Task:
        return Task(config=self.tasks_config["code_task"], agent=self.coder())

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_task"],
            agent=self.qa_engineer_agent(),
            #### output_json=ResearchRoleRequirements
        )

    @task
    def evaluate_task(self) -> Task:
        return Task(
            config=self.tasks_config["evaluate_task"],
            agent=self.chief_qa_engineer_agent(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GameBuilderCrew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            # embedder={
            #     "provider": "ollama",
            #     "config": {
            #         "model": "mxbai-embed-large",
            #         "url": "http://localhost:11434/api/embeddings"
            #     }
            # },
        )
