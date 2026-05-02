def detect_performance_drift(
    previous_accuracy: float,
    current_accuracy: float,
    threshold: float = 0.05,
) -> bool:
    """Return True if performance drop exceeds the threshold."""
    return (previous_accuracy - current_accuracy) > threshold
