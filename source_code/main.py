from source_code.runtime import load_environment, run_crew_pipeline


load_environment()


def run():
    print("Starting AI Signal Research Crew...\n")

    result = run_crew_pipeline()

    print("\n Crew Execution Completed.\n")
    print("Final Output:\n")
    print(result)


if __name__ == "__main__":
    run()
