import json
import os
from datetime import datetime

from source_code.paths import LOGS_DIR, PERFORMANCE_LOG_PATH


PERFORMANCE_LOG = str(PERFORMANCE_LOG_PATH)


def log_model_performance(metrics: dict) -> str:
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
    }

    with open(PERFORMANCE_LOG, "a") as handle:
        handle.write(json.dumps(log_entry) + "\n")

    return "Model performance logged."
