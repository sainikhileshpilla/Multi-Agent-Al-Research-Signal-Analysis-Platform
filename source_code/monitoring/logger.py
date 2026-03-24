import os
import json
import pathlib
from datetime import datetime
from typing import Dict

LOG_DIR = str(pathlib.Path(__file__).resolve().parents[1] / "logs")

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)

def _write_log(file_name: str, log_entry: Dict):
    _ensure_log_dir()
    file_path = os.path.join(LOG_DIR, file_name)

    with open(file_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def log_ingestion(record_count: int, output_path: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "data_ingestion",
        "records_processed": record_count,
        "output_path": output_path
    }
    _write_log("ingestion_log.json", log_entry)


def log_model_performance(metrics: dict):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "model_performance",
        "metrics": metrics
    }
    _write_log("model_performance.json", log_entry)
