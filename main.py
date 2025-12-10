import sys
import yaml
from crew import GameBuilderCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    print("## Welcome to the Crew")
    print('-------------------------------')

    inputs = {
        'game': input("write instructions:")
    }
    game = GameBuilderCrew().crew().kickoff(inputs=inputs)

    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("final code:...")
    print("\n\n########################")
    print(game)

def train():
    """
    Train the crew for a given number of iterations.
    """

    with open('src/game_builder_crew/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)

    inputs = {
        'game': examples['example1_pacman']
    }
    try:
        GameBuilderCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

if __name__ == "__main__":
    run()