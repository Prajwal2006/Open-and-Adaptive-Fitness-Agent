from datetime import date, datetime
from typing import Any


def date_to_str(d: date | None) -> str | None:
    if d is None:
        return None
    return d.isoformat()


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator
