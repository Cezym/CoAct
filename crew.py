from crewai import Agent, Task, Crew
import yaml

# Ładowanie konfiguracji agentów z YAML
with open("config/agents.yaml", "r") as f:
    agents_config = yaml.safe_load(f)

# Ładowanie konfiguracji zadań z YAML
with open("config/tasks.yaml", "r") as f:
    tasks_config = yaml.safe_load(f)

# Tworzenie agentów na podstawie YAML
researcher = Agent(
    role=agents_config["researcher"]["role"],
    goal=agents_config["researcher"]["goal"],
    backstory=agents_config["researcher"]["backstory"],
    llm="ollama/llama3.1:8b",  # Bezpośrednie wskazanie modelu Ollama
)

writer = Agent(
    role=agents_config["writer"]["role"],
    goal=agents_config["writer"]["goal"],
    backstory=agents_config["writer"]["backstory"],
    llm="ollama/llama3.1:8b",  # Bezpośrednie wskazanie modelu Ollama
)

# Tworzenie zadań na podstawie YAML
research_task = Task(
    description=tasks_config["research_task"]["description"],
    expected_output=tasks_config["research_task"]["expected_output"],
    agent=researcher,
)

writing_task = Task(
    description=tasks_config["writing_task"]["description"],
    expected_output=tasks_config["writing_task"]["expected_output"],
    agent=writer,
)

# Definiowanie crew (zespołu)
crew = Crew(
    agents=[researcher, writer], tasks=[research_task, writing_task], verbose=True
)
