"""
Forecasting module for workforce projections.

Uses exponential smoothing on the quarterly estimation time-series
to project 4 quarters ahead. Falls back to linear trend if Prophet
is not available.
"""

import math
from backend.models.estimators import get_time_series


def _quarter_to_index(q: str) -> int:
    """Convert '2024_Q1' to a numeric index for regression."""
    year, qn = q.split("_")
    return int(year) * 4 + int(qn[1])


def _index_to_quarter(idx: int) -> str:
    year = (idx - 1) // 4
    q = ((idx - 1) % 4) + 1
    return f"{year}_Q{q}"


def linear_forecast(series: list[dict], periods: int = 4) -> list[dict]:
    """Simple linear regression forecast."""
    if not series:
        return []

    xs = [_quarter_to_index(s["quarter"]) for s in series]
    ys = [s["estimated"] for s in series]
    n = len(xs)

    x_mean = sum(xs) / n
    y_mean = sum(ys) / n

    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)

    slope = num / den if den else 0
    intercept = y_mean - slope * x_mean

    # Residual std for confidence interval
    residuals = [(y - (slope * x + intercept)) for x, y in zip(xs, ys)]
    residual_std = math.sqrt(sum(r ** 2 for r in residuals) / max(n - 2, 1))

    last_idx = max(xs)
    forecasts = []
    for i in range(1, periods + 1):
        future_idx = last_idx + i
        point = slope * future_idx + intercept
        # Widen confidence band as we project further
        margin = residual_std * 1.96 * math.sqrt(1 + 1 / n + (future_idx - x_mean) ** 2 / den)
        forecasts.append({
            "quarter": _index_to_quarter(future_idx),
            "forecast": round(point),
            "confidence_low": round(point - margin),
            "confidence_high": round(point + margin),
            "is_forecast": True,
        })

    return forecasts


def exponential_smoothing_forecast(series: list[dict], periods: int = 4, alpha: float = 0.4) -> list[dict]:
    """
    Double exponential smoothing (Holt's method) for trend-aware forecasting.
    """
    if len(series) < 2:
        return linear_forecast(series, periods)

    ys = [s["estimated"] for s in series]

    # Initialize
    level = ys[0]
    trend = ys[1] - ys[0]
    beta = 0.3

    # Fit
    fitted = []
    for y in ys:
        last_level = level
        level = alpha * y + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        fitted.append(level)

    # Residual std
    residuals = [y - f for y, f in zip(ys, fitted)]
    residual_std = math.sqrt(sum(r ** 2 for r in residuals) / max(len(residuals) - 2, 1))

    last_idx = _quarter_to_index(series[-1]["quarter"])
    forecasts = []
    for i in range(1, periods + 1):
        point = level + i * trend
        margin = residual_std * 1.96 * math.sqrt(i)
        forecasts.append({
            "quarter": _index_to_quarter(last_idx + i),
            "forecast": round(point),
            "confidence_low": round(point - margin),
            "confidence_high": round(point + margin),
            "is_forecast": True,
        })

    return forecasts


def get_full_projection(periods: int = 4) -> dict:
    """
    Return historical series + forecast combined for dashboard use.
    """
    series = get_time_series()

    # Use exponential smoothing (better for trending data)
    forecast = exponential_smoothing_forecast(series, periods)

    # Also compute official GOSI projection (simple linear)
    gosi_series = [{"quarter": s["quarter"], "estimated": s["official"]} for s in series]
    gosi_forecast = linear_forecast(gosi_series, periods)

    return {
        "historical": series,
        "forecast": forecast,
        "gosi_forecast": gosi_forecast,
        "method": "Double exponential smoothing (Holt's method)",
        "forecast_periods": periods,
        "note": "Confidence intervals widen with projection horizon",
    }
