import yaml
from crewai import Agent, Task, Crew, Process, LLM


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def create_crew(task_input):
    # ollama_llm = OllamaLLM(model="llama3.1:8b", base_url="http://localhost:11434")

    agents_config = load_yaml('config/agents.yaml')
    tasks_config = load_yaml('config/tasks.yaml')

    llm = LLM(
        model="openai/gpt-oss-20b",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed"  # Dummy dla lokalnego
    )

    manager = Agent(llm=llm, **agents_config['manager'])
    coder = Agent(llm=llm, **agents_config['coder'])
    tester = Agent(llm=llm, **agents_config['tester'])
    researcher = Agent(llm=llm, **agents_config['researcher'])
    critic = Agent(llm=llm, **agents_config['critic'])

    manager_task = Task(agent=manager, **tasks_config['manager_task'])
    coder_task = Task(agent=coder, **tasks_config['coder_task'])
    tester_task = Task(agent=tester, **tasks_config['tester_task'])
    researcher_task = Task(agent=researcher, **tasks_config['researcher_task'])
    critic_task = Task(agent=critic, **tasks_config['critic_task'])

    crew = Crew(
        agents=[coder, tester, researcher, critic],
        tasks=[manager_task, coder_task, tester_task, researcher_task, critic_task],
        manager_agent=manager,
        process=Process.hierarchical,
        verbose=True
    )

    return crew.kickoff(inputs={"zadanie": task_input})
