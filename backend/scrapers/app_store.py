"""
Google Play Store scraper for delivery platform apps.

Collects review counts, ratings, and install counts as proxy signals
for platform activity and relative market sizing.

Real data fallback scraped on 2026-03-05.
"""

import json
import os
from datetime import datetime, timedelta

from backend.config import PLATFORMS, REAL_APP_DATA

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE_FILE = os.path.join(CACHE_DIR, "app_store_cache.json")


def _load_cache() -> dict:
    os.makedirs(CACHE_DIR, exist_ok=True)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def _save_cache(data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


async def scrape_google_play(app_id: str) -> dict | None:
    """Scrape app info from Google Play using google-play-scraper."""
    try:
        from google_play_scraper import app as gp_app

        info = gp_app(app_id, lang="ar", country="sa")
        return {
            "app_id": app_id,
            "title": info.get("title"),
            "score": info.get("score"),
            "ratings": info.get("ratings"),
            "reviews_count": info.get("reviews"),
            "installs": info.get("realInstalls") or info.get("installs"),
            "last_updated": info.get("lastUpdatedOn"),
            "scraped_at": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"app_id": app_id, "error": str(e)}


async def scrape_all_platforms() -> dict:
    """Scrape Google Play data for all configured platforms."""
    cache = _load_cache()

    if cache.get("_scraped_at"):
        scraped = datetime.fromisoformat(cache["_scraped_at"])
        if datetime.now() - scraped < timedelta(hours=6):
            return cache

    results = {}
    for key, plat in PLATFORMS.items():
        data = await scrape_google_play(plat["google_play_id"])
        if data and "error" not in data:
            results[key] = data
        else:
            # Fall back to real scraped data
            results[key] = {**REAL_APP_DATA.get(key, {}), "scraped_at": "2026-03-05T00:00:00"}

    results["_scraped_at"] = datetime.now().isoformat()
    _save_cache(results)
    return results


def get_fallback_app_data() -> dict:
    """Return the real app data we scraped on 2026-03-05."""
    return {k: {**v, "scraped_at": "2026-03-05T00:00:00"} for k, v in REAL_APP_DATA.items()}
