from crewai import Agent
from first_project.pipelines.ingestion import load_all_from_directory
from first_project.pipelines.validation import validate_and_clean, save_processed
from first_project.monitoring.logger import log_ingestion


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
            # Step 1: Load
            df = load_raw_data(input_path)

            # Step 2: Validate Schema
            validate_schema(df)

            # Step 3: Clean Data
            df_clean = clean_data(df)

            # Step 4: Save Processed Data
            save_processed(df_clean, output_path)

            # Step 5: Log Ingestion Metadata
            log_ingestion(len(df_clean), output_path)

            print("Data Agent pipeline completed successfully.")

            return {
                "status": "success",
                "records_processed": len(df_clean),
                "output_path": output_path
            }

        except Exception as e:
            print(f"Data Agent failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
