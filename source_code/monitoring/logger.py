"""Compatibility shim for gradual migration to services.ml.monitoring.logger."""

from services.ml.monitoring.logger import (  # noqa: F401
    LOG_DIR,
    log_ingestion,
    log_model_performance,
)
