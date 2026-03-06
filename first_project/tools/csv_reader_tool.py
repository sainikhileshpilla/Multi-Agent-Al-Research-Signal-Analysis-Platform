import pathlib
import pandas as pd
from crewai.tools import BaseTool


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _resolve(path: str) -> str:
    p = pathlib.Path(path)
    return str(p) if p.is_absolute() else str(PROJECT_ROOT / p)


class CSVReaderTool(BaseTool):
    name: str = "csv_reader_tool"
    description: str = (
        "Reads a CSV file from the given path and returns a summary of its contents, "
        "including column names, row count, and the first few records as a formatted table."
    )

    def _run(self, file_path: str) -> str:
        try:
            df = pd.read_csv(_resolve(file_path))
            summary = (
                f"Rows: {len(df)}\n"
                f"Columns: {list(df.columns)}\n\n"
                f"First 10 records:\n{df.head(10).to_string(index=False)}"
            )
            return summary
        except Exception as e:
            return f"Failed to read CSV: {str(e)}"
