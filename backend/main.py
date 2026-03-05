"""
Gig Economy Observatory — API Server

Endpoints:
  /api/summary          → Latest quarter KPIs and gap analysis
  /api/timeseries       → Historical estimates + forecast
  /api/platforms        → Per-platform breakdown
  /api/triangulation    → Validation matrix showing method cross-checks
  /api/trends           → Google Trends data (consumer + driver supply)
  /api/appstore         → App store metrics for all platforms
  /api/ml               → XGBoost model: feature importance + SHAP explanation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.estimators import (
    get_latest_summary,
    get_time_series,
    get_validation_matrix,
)
from backend.models.forecast import get_full_projection
from backend.models.ml_model import train_and_explain
from backend.scrapers.app_store import get_fallback_app_data, scrape_all_platforms
from backend.scrapers.google_trends import REAL_TRENDS_DATA, fetch_trends_data

app = FastAPI(
    title="Gig Economy Observatory",
    description="Smart observatory for measuring platform-based employment in Saudi Arabia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/summary")
async def summary():
    """Latest quarter: total estimate, GOSI official, gap, per-platform breakdown."""
    return get_latest_summary()


@app.get("/api/timeseries")
async def timeseries():
    """Historical estimated vs official + 4-quarter forecast."""
    return get_full_projection()


@app.get("/api/platforms")
async def platforms():
    """Per-platform worker estimates for the latest quarter."""
    data = get_latest_summary()
    if "error" in data:
        return data
    return {
        "quarter": data["quarter"],
        "platforms": data["platforms"],
        "total_unique": data["unique_workers_estimate"],
        "overlap_rate": data["overlap_rate"],
    }


@app.get("/api/triangulation")
async def triangulation():
    """Cross-validation matrix: financial vs TGA vs app ecosystem."""
    return get_validation_matrix()


@app.get("/api/trends")
async def trends():
    """Google Trends data: consumer demand + driver registration intent."""
    try:
        data = await fetch_trends_data()
        return data
    except Exception:
        return REAL_TRENDS_DATA


@app.get("/api/appstore")
async def appstore():
    """App store metrics: ratings, reviews, install counts."""
    try:
        data = await scrape_all_platforms()
        return data
    except Exception:
        return get_fallback_app_data()


@app.get("/api/ml")
async def ml_model():
    """XGBoost model: feature importance, SHAP values, prediction accuracy."""
    return train_and_explain()
