import json
import os
from datetime import datetime
from typing import Dict

from source_code.paths import LOGS_DIR


LOG_DIR = str(LOGS_DIR)


def _ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def _write_log(file_name: str, log_entry: Dict) -> None:
    _ensure_log_dir()
    file_path = os.path.join(LOG_DIR, file_name)
    payload = json.dumps(log_entry)

    with open(file_path, "a") as handle:
        handle.write(payload + "\n")


def log_ingestion(record_count: int, output_path: str) -> None:
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "data_ingestion",
        "records_processed": record_count,
        "output_path": output_path,
    }
    _write_log("ingestion_log.json", log_entry)


def log_model_performance(metrics: dict) -> None:
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "model_performance",
        "metrics": metrics,
    }
    _write_log("model_performance.json", log_entry)
