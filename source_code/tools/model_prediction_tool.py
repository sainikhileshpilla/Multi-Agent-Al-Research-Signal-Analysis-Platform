import os
import pathlib
import joblib
import pandas as pd
from crewai.tools import BaseTool

from source_code.pipelines.feature_engineering import generate_features


# Resolve project root from this file's location:
# tools/ -> source_code/ (project root)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_PATH = str(PROJECT_ROOT / "models" / "signal_model.pkl")


def _resolve(path: str) -> str:
    """Resolve a relative path against the project root."""
    p = pathlib.Path(path)
    return str(p) if p.is_absolute() else str(PROJECT_ROOT / p)


class ModelPredictionTool(BaseTool):
    name: str = "model_prediction_tool"
    description: str = (
        "Loads the trained signal model and runs predictions on a processed financial news "
        "CSV file. Accepts the path to the processed CSV. Returns a prediction summary "
        "including total records, bullish/bearish signal counts, and a sample of predictions."
    )

    def _run(self, data_path: str) -> str:
        try:
            if not os.path.exists(MODEL_PATH):
                return f"Model not found at '{MODEL_PATH}'. Run the training step first."

            resolved = _resolve(data_path)
            if not os.path.exists(resolved):
                return f"Dataset not found at '{resolved}'. Ensure the data pipeline ran successfully."

            model = joblib.load(MODEL_PATH)
            df = pd.read_csv(resolved)
            features_df = generate_features(df)

            X = features_df[["headline_length", "sentiment_score"]]
            predictions = model.predict(X)

            features_df = features_df.copy()
            features_df["prediction"] = predictions

            total = len(predictions)
            bullish = int((predictions == 1).sum())
            bearish = total - bullish

            sample = features_df[["headline_length", "sentiment_score", "prediction"]].head(10)

            return (
                f"Predictions complete on {total} records.\n"
                f"Bullish signals (1): {bullish}\n"
                f"Bearish signals (0): {bearish}\n\n"
                f"Sample predictions (first 10 rows):\n{sample.to_string(index=False)}"
            )
        except Exception as e:
            return f"Prediction failed: {str(e)}"
