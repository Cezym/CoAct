"""Crew that writes and reviews code – DevelopersCrew."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, task, crew

from embedder_provider import EMBEDDERS
from llm_provider import LLMS
from . import CrewConfigMixin
from tools.web_rag_tool import WebRAGTool


@CrewBase
class DevelopersCrew:
    """Crew that creates code and performs a first review."""

    # ---------- AGENTS ----------
    @agent
    def clarifier_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["clarifier_agent"]
        return Agent(
            config=cfg,
            allow_delegation=False,
            verbose=True,
            llm=LLMS[cfg["llm_model"]],
        )

    @agent
    def coder_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["coder_agent"]
        return Agent(
            config=cfg,
            allow_delegation=False,
            # tools=[WebRAGTool()], ### under development ###
            llm=LLMS[cfg["llm_model"]],
        )

    @agent
    def qa_engineer_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["qa_engineer_agent"]
        return Agent(
            config=cfg,
            allow_delegation=False,
            # tools=[WebRAGTool()], ### under development ###
            llm=LLMS[cfg["llm_model"]],
        )

    @agent
    def chief_qa_engineer_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["chief_qa_engineer_agent"]
        return Agent(
            config=cfg,
            allow_delegation=False,
            # tools=[WebRAGTool()], ### under development ###
            llm=LLMS[cfg["llm_model"]],
        )

    # ---------- TASKS ----------
    @task
    def clarifier_task(self) -> Task:
        cfg = CrewConfigMixin.crew_tasks_config()["clarifier_task"]
        return Task(config=cfg, agent=self.clarifier_agent())

    @task
    def code_task(self) -> Task:
        cfg = CrewConfigMixin.crew_tasks_config()["code_task"]
        return Task(config=cfg, agent=self.coder_agent())

    @task
    def review_task(self) -> Task:
        cfg = CrewConfigMixin.crew_tasks_config()["review_task"]
        return Task(config=cfg, agent=self.qa_engineer_agent())

    @task
    def evaluate_task(self) -> Task:
        cfg = CrewConfigMixin.crew_tasks_config()["evaluate_task"]
        return Task(config=cfg, agent=self.chief_qa_engineer_agent())

    @task
    def human_input_evaluation_task(self):
        cfg = CrewConfigMixin.crew_tasks_config()["human_input_evaluation_task"]
        return Task(config=cfg, agent=self.chief_qa_engineer_agent())

    # ---------- CREW ----------
    @crew
    def crew(self) -> Crew:
        """Return a fully configured Crew instance."""
        return Crew(
            agents=self.agents,  # automatically collected by decorators
            tasks=self.tasks,  # automatically collected by decorators
            process=Process.sequential,
            memory=False,
            embedder=EMBEDDERS["developers_crew_embedder"],
        )
