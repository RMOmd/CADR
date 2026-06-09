def entry_signal(zscore: float, threshold: float = 2.0) -> bool:
    """Basic entry signal logic based on z-score."""
    return abs(zscore) >= threshold

def exit_signal(current_zscore: float, entry_zscore: float, exit_threshold: float = 0.5) -> bool:
    """Exit when spread reverts to mean."""
    # If entered long when z < -2.0, exit when z > -0.5
    if entry_zscore <= -2.0 and current_zscore >= -exit_threshold:
        return True
    # If entered short when z > 2.0, exit when z < 0.5
    if entry_zscore >= 2.0 and current_zscore <= exit_threshold:
        return True
    return False
