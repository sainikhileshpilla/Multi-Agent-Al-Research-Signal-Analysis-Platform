"""Compatibility shim for gradual migration to services.ml.monitoring.performance."""

from services.ml.monitoring.performance import (  # noqa: F401
    PERFORMANCE_LOG,
    log_model_performance,
)
