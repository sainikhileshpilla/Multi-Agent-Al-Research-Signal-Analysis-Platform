import json
import os
import shutil
from datetime import datetime

import joblib
import pandas as pd
from crewai.tools import BaseTool

from services.ml.feature_engineering import generate_features
from services.ml.monitoring.drift import detect_performance_drift
from services.ml.monitoring.retraining import trigger_retraining
from services.ml.train import train_model
from source_code.paths import (
    DEPLOYED_DIR,
    DEPLOYED_MODEL_PATH,
    DEPLOYMENT_MANIFEST_PATH,
    MODEL_PATH,
    PERFORMANCE_LOG_PATH,
    PROCESSED_NEWS_PATH,
    resolve_path,
)

DEFAULT_LOG_PATH = str(PERFORMANCE_LOG_PATH)
DEFAULT_DATA_PATH = str(PROCESSED_NEWS_PATH)


class ModelTrainingTool(BaseTool):
    name: str = "model_training_tool"
    description: str = (
        "Trains and compares multiple ML models (Logistic Regression, Random Forest, "
        "Gradient Boosting, SVM) on the cleaned financial news dataset. "
        "Accepts the path to the processed CSV file. Selects the best model by F1 score "
        "and saves it to models/signal_model.pkl. Returns a comparison of all models."
    )

    def _run(self, data_path: str) -> str:
        try:
            metrics = train_model(str(resolve_path(data_path)))
            best = metrics["best_model"]
            all_models = metrics["all_models"]

            comparison = "\n".join(
                f"  {name}: accuracy={r['accuracy']:.4f}  precision={r['precision']:.4f}"
                f"  recall={r['recall']:.4f}  f1={r['f1_score']:.4f}"
                for name, r in all_models.items()
            )

            return (
                f"Model comparison:\n{comparison}\n\n"
                f"Best model: {best}\n"
                f"Accuracy:  {metrics['accuracy']:.4f}\n"
                f"Precision: {metrics['precision']:.4f}\n"
                f"Recall:    {metrics['recall']:.4f}\n"
                f"F1 Score:  {metrics['f1_score']:.4f}\n"
                "Saved to models/signal_model.pkl."
            )
        except Exception as exc:
            return f"Model training failed: {str(exc)}"


class ModelPredictionTool(BaseTool):
    name: str = "model_prediction_tool"
    description: str = (
        "Loads the trained signal model and runs predictions on a processed financial news "
        "CSV file. Accepts the path to the processed CSV. Returns a prediction summary "
        "including total records, bullish/bearish signal counts, and a sample of predictions."
    )

    def _run(self, data_path: str) -> str:
        try:
            if not MODEL_PATH.exists():
                return f"Model not found at '{MODEL_PATH}'. Run the training step first."

            resolved = resolve_path(data_path)
            if not resolved.exists():
                return f"Dataset not found at '{resolved}'. Ensure the data pipeline ran successfully."

            model = joblib.load(str(MODEL_PATH))
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
        except Exception as exc:
            return f"Prediction failed: {str(exc)}"


class ModelMonitoringTool(BaseTool):
    name: str = "model_monitoring_tool"
    description: str = (
        "Reads the model performance log, compares the two most recent runs to detect "
        "accuracy drift, and triggers retraining if the accuracy drop exceeds the 5% threshold. "
        "Returns a monitoring report with current metrics and drift status. "
        "Accepts optional log_path (defaults to logs/model_performance.json) and "
        "data_path (defaults to data/processed/news_cleaned.csv)."
    )

    def _run(self, log_path: str = DEFAULT_LOG_PATH, data_path: str = DEFAULT_DATA_PATH) -> str:
        try:
            resolved = resolve_path(log_path)
            if not os.path.exists(resolved):
                return "No performance log found. Run model training first."

            entries = []
            with open(resolved) as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))

            if not entries:
                return "Performance log is empty."

            latest = entries[-1]
            report_lines = [
                f"Latest run ({latest['timestamp']}):",
                f"  Accuracy:  {latest['metrics']['accuracy']:.4f}",
                f"  Precision: {latest['metrics']['precision']:.4f}",
                f"  Recall:    {latest['metrics']['recall']:.4f}",
                f"  F1 Score:  {latest['metrics']['f1_score']:.4f}",
            ]

            if len(entries) >= 2:
                previous = entries[-2]
                drift_detected = detect_performance_drift(
                    previous["metrics"]["accuracy"],
                    latest["metrics"]["accuracy"],
                )
                if drift_detected:
                    retrain_result = trigger_retraining(data_path)
                    report_lines.append(
                        f"\nDrift detected: accuracy dropped from "
                        f"{previous['metrics']['accuracy']:.4f} to "
                        f"{latest['metrics']['accuracy']:.4f}. Retraining completed."
                    )
                    report_lines.append(
                        "Retraining result: "
                        f"best_model={retrain_result['best_model']} "
                        f"accuracy={retrain_result['accuracy']:.4f} "
                        f"precision={retrain_result['precision']:.4f} "
                        f"recall={retrain_result['recall']:.4f} "
                        f"f1={retrain_result['f1_score']:.4f}"
                    )
                else:
                    report_lines.append(
                        f"\nNo significant drift detected (previous accuracy: "
                        f"{previous['metrics']['accuracy']:.4f})."
                    )
            else:
                report_lines.append("\nOnly one run recorded - no drift comparison available yet.")

            return "\n".join(report_lines)

        except Exception as exc:
            return f"Monitoring failed: {str(exc)}"


class ModelDeploymentTool(BaseTool):
    name: str = "model_deployment_tool"
    description: str = (
        "Deploys the trained signal model by copying it to the deployed/ directory "
        "and writing a deployment manifest with metadata. "
        "Returns a deployment confirmation report."
    )

    def _run(self) -> str:
        try:
            if not MODEL_PATH.exists():
                return f"Deployment failed: trained model not found at '{MODEL_PATH}'."

            DEPLOYED_DIR.mkdir(parents=True, exist_ok=True)

            deployed_model_path = DEPLOYED_MODEL_PATH
            shutil.copy2(str(MODEL_PATH), str(DEPLOYED_MODEL_PATH))

            manifest = {
                "status": "deployed",
                "deployed_at": datetime.now().isoformat(),
                "source_model": str(MODEL_PATH),
                "deployed_model": str(deployed_model_path),
            }
            DEPLOYMENT_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

            return (
                "Model deployed successfully.\n"
                f"Deployed model: {deployed_model_path}\n"
                f"Manifest written: {DEPLOYMENT_MANIFEST_PATH}\n"
                f"Deployed at: {manifest['deployed_at']}"
            )
        except Exception as exc:
            return f"Deployment failed: {str(exc)}"
