import yaml
from crewai import Agent, Task, Crew, Process, LLM

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def create_crew(task_input):
    llm = LLM(
        provider="openai",
        model="openai/gpt-oss-20b",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed"
    )

    agents_config = load_yaml('config/agents.yaml')
    tasks_config = load_yaml('config/tasks.yaml')

    manager = Agent(llm=llm, **agents_config['manager'])
    coder = Agent(llm=llm, **agents_config['coder'])
    tester = Agent(llm=llm, **agents_config['tester'])
    researcher = Agent(llm=llm, **agents_config['researcher'])
    critic = Agent(llm=llm, **agents_config['critic'])

    tasks_dict = {}

    manager_task = Task(agent=manager, **tasks_config['manager_task'])
    tasks_dict['manager_task'] = manager_task

    # Dla każdej task rozwiąż context
    def create_task_with_context(name, config, agent):
        context_names = config.get('context', [])
        context = [tasks_dict[c] for c in context_names if c in tasks_dict]
        return Task(agent=agent, context=context, **{k: v for k, v in config.items() if k != 'context'})

    coder_task = create_task_with_context('coder_task', tasks_config['coder_task'], coder)
    tasks_dict['coder_task'] = coder_task

    tester_task = create_task_with_context('tester_task', tasks_config['tester_task'], tester)
    tasks_dict['tester_task'] = tester_task

    researcher_task = create_task_with_context('researcher_task', tasks_config['researcher_task'], researcher)
    tasks_dict['researcher_task'] = researcher_task

    critic_task = create_task_with_context('critic_task', tasks_config['critic_task'], critic)
    tasks_dict['critic_task'] = critic_task

    crew = Crew(
        agents=[coder, tester, researcher, critic],
        manager_agent=manager,
        tasks=[manager_task, coder_task, tester_task, researcher_task, critic_task],
        process=Process.hierarchical,
        verbose=True
    )

    return crew.kickoff(inputs={"task": task_input})