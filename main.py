import sys
from crew import create_crew
import os
import shutil
import dotenv

def main():
    # if len(sys.argv) < 2:
    #     print("Podaj zadanie, np: python main.py 'Napisz prosty kalkulator w Pythonie'")
    #     sys.exit(1)

    initial_task = "Program typical, simple calculator in python; assume answers if you are not sure"#input("Podaj zadanie")#sys.argv[1]
    print(f"{initial_task=}")
    approved = False
    inputs = {"zadanie": initial_task}
    # project_dir = "project_output"  # Katalog na strukturę plików
    #
    # if os.path.exists(project_dir):
    #     shutil.rmtree(project_dir)  # Czyszczenie przed startem
    # os.makedirs(project_dir)

    while not approved:
        #inputs["project_dir"] = project_dir
        result = create_crew(inputs["zadanie"])
        print(result)

        feedback = input("Co zmienić? Lub wpisz 'ok' by zaakceptować: ")

        if feedback.lower() == 'ok':
            approved = True
            print(f"Projekt zaakceptowany. Pliki w ")#{project_dir}.")
        else:
            inputs["zadanie"] = f"{initial_task} z zmianami: {feedback}"
            print("Iteruję...")

if __name__ == "__main__":
    main()