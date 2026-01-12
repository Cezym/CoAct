"""Crew that evaluates the generated code – CodeEvaluationCrew."""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, task, crew
from crewai.tools import tool

from embedder_provider import EMBEDDERS
from llm_provider import LLMS
from . import CrewConfigMixin


@CrewBase
class CodeEvaluationCrew:
    """Crew that performs code quality evaluation."""

    # ---------- AGENTS ----------
    @agent
    def readability_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["readability_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def documentation_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["documentation_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def functional_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["functional_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def tests_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["tests_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def complexity_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["complexity_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def duplication_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["duplication_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def performance_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["performance_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def security_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["security_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def maintainability_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["maintainability_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    @agent
    def compliance_agent(self) -> Agent:
        cfg = CrewConfigMixin.crew_agents_config()["compliance_agent"]
        return Agent(config=cfg, llm=LLMS[cfg["llm_model"]])

    # ---------- TASKS ----------
    def _task_with_code(self, key: str) -> Task:
        """Helper that builds a task that expects a `{code}` variable."""
        cfg = CrewConfigMixin.crew_tasks_config()[key]
        return Task(
            config=cfg,
            agent=getattr(self, f"{key.split('_')[0]}_agent")(),
            description=f"Code to evaluate:\n{{code}}\n\n{cfg['description']}",
            expected_output=cfg["expected_output"],
        )

    @task
    def readability_task(self) -> Task:
        return self._task_with_code("readability_task")

    @task
    def documentation_task(self) -> Task:
        return self._task_with_code("documentation_task")

    @task
    def functional_task(self) -> Task:
        return self._task_with_code("functional_task")

    @task
    def tests_task(self) -> Task:
        return self._task_with_code("tests_task")

    @task
    def complexity_task(self) -> Task:
        return self._task_with_code("complexity_task")

    @task
    def duplication_task(self) -> Task:
        return self._task_with_code("duplication_task")

    @task
    def performance_task(self) -> Task:
        return self._task_with_code("performance_task")

    @task
    def security_task(self) -> Task:
        return self._task_with_code("security_task")

    @task
    def maintainability_task(self) -> Task:
        return self._task_with_code("maintainability_task")

    @task
    def compliance_task(self) -> Task:
        return self._task_with_code("compliance_task")

    # ---------- CREW ----------
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            embedder=EMBEDDERS["evaluation_crew_embedder"],
        )
