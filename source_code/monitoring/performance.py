import json
import os
from datetime import datetime

PERFORMANCE_LOG = "logs/model_performance.json"

def log_model_performance(metrics: dict):
    os.makedirs("logs", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics
    }

    with open(PERFORMANCE_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return "Model performance logged."
