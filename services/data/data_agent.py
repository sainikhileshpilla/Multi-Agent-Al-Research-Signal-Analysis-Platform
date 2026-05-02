from crewai import Agent

from services.data.ingestion import load_all_from_directory
from services.data.validation import save_processed, validate_and_clean
from services.ml.monitoring.logger import log_ingestion


class DataAgent:
    def __init__(self):
        self.agent = Agent(
            role="Financial Data Engineer",
            goal="Collect, clean, validate, and structure financial news data",
            backstory=(
                "Expert in building reliable, scalable data ingestion pipelines "
                "for machine learning systems with strong validation and monitoring practices."
            ),
        )

    def run_pipeline(self, input_path: str, output_path: str):
        print("Starting Data Agent pipeline...")

        try:
            df = load_all_from_directory(input_path)
            if df.empty:
                return {"status": "failed", "error": "No records loaded from input path."}

            df_clean = validate_and_clean(df)
            if df_clean.empty:
                return {"status": "failed", "error": "All records were filtered out."}

            save_processed(df_clean, output_path)
            log_ingestion(len(df_clean), output_path)

            print("Data Agent pipeline completed successfully.")
            return {
                "status": "success",
                "records_processed": len(df_clean),
                "output_path": output_path,
            }

        except Exception as exc:
            print(f"Data Agent failed: {exc}")
            return {"status": "failed", "error": str(exc)}
