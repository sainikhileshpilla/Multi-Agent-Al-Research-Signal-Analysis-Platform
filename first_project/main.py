from first_project.crew import AISignalCrew


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
