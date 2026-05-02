import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment() -> None:
    repo_env = Path(__file__).resolve().parents[1] / ".env"
    if repo_env.exists():
        load_dotenv(dotenv_path=repo_env, override=False)

    local_env = Path(__file__).resolve().parent / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=local_env, override=False)


def run_crew_pipeline() -> str:
    load_environment()

    try:
        from .crew import AISignalCrew
    except ImportError:
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from source_code.crew import AISignalCrew

    crew_instance = AISignalCrew()
    crew = crew_instance.build()
    return crew.kickoff()