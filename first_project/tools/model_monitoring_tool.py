import json
import os
import pathlib

from crewai.tools import BaseTool
from first_project.monitoring.drift import detect_performance_drift
from first_project.monitoring.retraining import trigger_retraining

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = str(PROJECT_ROOT / "logs" / "model_performance.json")


def _resolve(path: str) -> str:
    p = pathlib.Path(path)
    return str(p) if p.is_absolute() else str(PROJECT_ROOT / p)


class ModelMonitoringTool(BaseTool):
    name: str = "model_monitoring_tool"
    description: str = (
        "Reads the model performance log, compares the two most recent runs to detect "
        "accuracy drift, and triggers retraining if the accuracy drop exceeds the 5% threshold. "
        "Returns a monitoring report with current metrics and drift status. "
        "Accepts an optional log_path argument (defaults to logs/model_performance.json)."
    )

    def _run(self, log_path: str = DEFAULT_LOG_PATH) -> str:
        try:
            resolved = _resolve(log_path)
            if not os.path.exists(resolved):
                return "No performance log found. Run model training first."

            entries = []
            with open(resolved) as f:
                for line in f:
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
                    trigger_retraining()
                    report_lines.append(
                        f"\nDrift detected: accuracy dropped from "
                        f"{previous['metrics']['accuracy']:.4f} to "
                        f"{latest['metrics']['accuracy']:.4f}. Retraining triggered."
                    )
                else:
                    report_lines.append(
                        f"\nNo significant drift detected (previous accuracy: "
                        f"{previous['metrics']['accuracy']:.4f})."
                    )
            else:
                report_lines.append(
                    "\nOnly one run recorded — no drift comparison available yet."
                )

            return "\n".join(report_lines)

        except Exception as e:
            return f"Monitoring failed: {str(e)}"
