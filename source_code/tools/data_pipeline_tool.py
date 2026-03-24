import pathlib
from crewai.tools import BaseTool
from source_code.pipelines.ingestion import load_all_from_directory
from source_code.pipelines.validation import (
    validate_and_clean,
    save_processed,
)
from source_code.monitoring.logger import log_ingestion

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _resolve(path: str) -> str:
    p = pathlib.Path(path)
    return str(p) if p.is_absolute() else str(PROJECT_ROOT / p)


class DataPipelineTool(BaseTool):
    name: str = "data_pipeline_tool"
    description: str = (
        "Loads raw financial news data, validates schema, cleans it, "
        "saves structured output, and logs ingestion metadata."
    )

    def _run(self, input_path: str = "data/raw", output_path: str = "data/processed/news_cleaned.csv") -> str:
        try:
            resolved_input = _resolve(input_path)
            resolved_output = _resolve(output_path)
            
            # Load all supported file formats from the directory
            df = load_all_from_directory(resolved_input)
            
            if df.empty:
                return f"No data found in {resolved_input}"
            
            # Validate and clean the combined dataset
            df_clean = validate_and_clean(df)
            
            if df_clean.empty:
                return f"All records were filtered out during validation"
            
            save_processed(df_clean, resolved_output)
            log_ingestion(len(df_clean), resolved_output)

            return f"Successfully processed {len(df_clean)} records from multiple sources."

        except Exception as e:
            return f"Pipeline failed: {str(e)}"
