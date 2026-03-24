try:
    from .crew import AISignalCrew
except ImportError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from source_code.crew import AISignalCrew


def run():
    print("Starting AI Signal Research Crew...\n")

    crew_instance = AISignalCrew()
    crew = crew_instance.build()

    result = crew.kickoff()

    print("\n Crew Execution Completed.\n")
    print("Final Output:\n")
    print(result)


if __name__ == "__main__":
    run()
