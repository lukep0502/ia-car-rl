def normalize(value, max_value):
    if max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))
