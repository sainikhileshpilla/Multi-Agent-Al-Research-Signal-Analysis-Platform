def detect_performance_drift(previous_accuracy: float, current_accuracy: float, threshold: float = 0.05) -> bool:
    """
    Returns True if performance drop exceeds threshold.
    """
    if previous_accuracy - current_accuracy > threshold:
        return True
    return False
