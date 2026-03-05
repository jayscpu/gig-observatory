"""
Platform configuration and constants for the Gig Observatory.

Data sources:
- Jahez financials: Tadawul 6017 quarterly filings via stockanalysis.com
- Market data: Transport General Authority (TGA) via Saudi Gazette / SPA
- App store: Google Play Store (scraped live)
- Market share: Argaam, Redseer, Saudi Gazette
"""

PLATFORMS = {
    "jahez": {
        "name": "Jahez",
        "name_ar": "جاهز",
        "google_play_id": "net.jahez",
        "is_public": True,
        "tadawul_symbol": "6017",
        "search_terms": ["جاهز توصيل", "Jahez delivery"],
        "driver_search_terms": ["تسجيل سائق جاهز", "وظائف جاهز توصيل"],
    },
    "hungerstation": {
        "name": "HungerStation",
        "name_ar": "هنقرستيشن",
        "google_play_id": "com.hungerstation.android.web",
        "is_public": False,
        "parent": "Delivery Hero SE",
        "search_terms": ["هنقرستيشن", "HungerStation"],
        "driver_search_terms": ["تسجيل هنقرستيشن سائق", "وظائف هنقرستيشن"],
    },
    "mrsool": {
        "name": "Mrsool",
        "name_ar": "مرسول",
        "google_play_id": "com.mrsool",
        "is_public": False,
        "search_terms": ["مرسول توصيل", "Mrsool"],
        "driver_search_terms": ["تسجيل مرسول مندوب", "وظائف مرسول"],
    },
    "chefz": {
        "name": "The Chefz",
        "name_ar": "ذا شفز",
        "google_play_id": "com.nextwo.the_chefz",
        "is_public": False,
        "search_terms": ["شفز توصيل", "Chefz"],
        "driver_search_terms": ["تسجيل شفز سائق"],
    },
}

# ─── Jahez Quarterly Financials (Tadawul 6017) ────────────────────────────────
# Source: stockanalysis.com/quote/tadawul/6017/financials/?p=quarterly
# Revenue and Cost of Revenue in SAR (exact from filings)
# Orders: 2024 total = 106M (25% YoY), split estimated proportionally by revenue
# Take rate: 14.6% in 2024, 15.5% in 9M 2025
JAHEZ_FINANCIALS = {
    "2023_Q1": {
        "revenue_sar": 417_807_797,
        "cost_of_revenue_sar": 325_451_189,
        "gross_profit_sar": 92_356_608,
        "orders_m": 21.2,       # ~85M total 2023 / 4 (estimated)
        "take_rate": 0.135,
    },
    "2023_Q2": {
        "revenue_sar": 421_035_113,
        "cost_of_revenue_sar": 317_983_334,
        "gross_profit_sar": 103_051_779,
        "orders_m": 21.5,
        "take_rate": 0.135,
    },
    "2023_Q3": {
        "revenue_sar": 451_646_699,
        "cost_of_revenue_sar": 350_373_128,
        "gross_profit_sar": 101_273_571,
        "orders_m": 22.0,
        "take_rate": 0.135,
    },
    "2023_Q4": {
        "revenue_sar": 497_492_991,
        "cost_of_revenue_sar": 377_602_254,
        "gross_profit_sar": 119_890_737,
        "orders_m": 22.3,
        "take_rate": 0.135,
    },
    "2024_Q1": {
        "revenue_sar": 480_931_652,
        "cost_of_revenue_sar": 385_292_740,
        "gross_profit_sar": 95_638_912,
        "orders_m": 24.5,       # 106M total, Q1 typically lighter
        "take_rate": 0.146,
    },
    "2024_Q2": {
        "revenue_sar": 540_962_580,
        "cost_of_revenue_sar": 419_683_827,
        "gross_profit_sar": 121_278_753,
        "orders_m": 26.0,
        "take_rate": 0.146,
    },
    "2024_Q3": {
        "revenue_sar": 601_266_739,
        "cost_of_revenue_sar": 443_675_587,
        "gross_profit_sar": 157_591_152,
        "orders_m": 27.5,
        "take_rate": 0.146,
    },
    "2024_Q4": {
        "revenue_sar": 595_501_764,
        "cost_of_revenue_sar": 428_848_015,
        "gross_profit_sar": 166_653_749,
        "orders_m": 28.0,       # 106M - (24.5+26+27.5) = 28M
        "take_rate": 0.146,
    },
    "2025_Q1": {
        "revenue_sar": 525_956_884,
        "cost_of_revenue_sar": 399_981_456,
        "gross_profit_sar": 125_975_428,
        "orders_m": 26.0,       # 9M total = 80.9M, so Q1 ~26M
        "take_rate": 0.155,
    },
    "2025_Q2": {
        "revenue_sar": 567_077_409,
        "cost_of_revenue_sar": 447_800_116,
        "gross_profit_sar": 119_277_293,
        "orders_m": 27.5,
        "take_rate": 0.155,
    },
    "2025_Q3": {
        "revenue_sar": 533_269_798,
        "cost_of_revenue_sar": 401_006_659,
        "gross_profit_sar": 132_263_139,
        "orders_m": 27.4,       # 80.9M - 26 - 27.5 = 27.4M
        "take_rate": 0.155,
    },
}

# ─── TGA Official Delivery Sector Data (2024) ─────────────────────────────────
# Source: Saudi Gazette / SPA citing Transport General Authority
# "2024 sees 290 million delivery orders, with number of Saudi drivers
#  surpassing 140,000" — Saudi Gazette, citing TGA
TGA_MARKET_DATA = {
    "2024": {
        "total_orders_m": 290,
        "saudi_drivers": 140_000,
        "non_saudi_drivers": 302_000,
        "total_drivers": 442_000,
        "licensed_companies": 61,
        "avg_delivery_time_min": 35,
        "yoy_order_growth": 0.272,
        "yoy_saudi_driver_growth": 0.21,
        "yoy_non_saudi_driver_growth": 0.05,
    },
    "2023": {
        "total_orders_m": 228,    # 290 / 1.272
        "saudi_drivers": 115_700, # 140000 / 1.21
        "non_saudi_drivers": 287_600, # 302000 / 1.05
        "total_drivers": 403_300,
        "avg_delivery_time_min": 45,
    },
}

# ─── Market Share by Orders (2024) ────────────────────────────────────────────
# Source: Argaam — "Jahez holds 32% share of delivery orders in Saudi Arabia"
# Source: Redseer — "Keeta has gained 10% market share in KSA"
# Source: Various — "HungerStation and Jahez hold over 67% of market share"
# Total market: 290M orders
# Jahez: 91M orders in KSA (32%) — from Argaam/Jahez CFO
# HungerStation: ~35% (67% combined - 32% Jahez) = ~101.5M orders
# Keeta: ~10% = ~29M orders (launched late 2024)
# Mrsool + Others: ~23% = ~66.7M orders
ORDER_MARKET_SHARE = {
    "jahez": {"share": 0.32, "orders_m": 91, "source": "Jahez CFO / TGA"},
    "hungerstation": {"share": 0.35, "orders_m": 101.5, "source": "Derived: 67% combined - 32% Jahez"},
    "mrsool": {"share": 0.15, "orders_m": 43.5, "source": "Estimated from remaining share"},
    "chefz": {"share": 0.05, "orders_m": 14.5, "source": "Estimated from remaining share"},
    "keeta": {"share": 0.10, "orders_m": 29, "source": "Redseer report"},
    "others": {"share": 0.03, "orders_m": 10.5, "source": "Remaining"},
}

# ─── Driver Economics ──────────────────────────────────────────────────────────
# Jahez has 4,000+ Logi drivers under direct sponsorship (Q3 2025)
# Total market has 442,000 drivers (TGA 2024)
# Cost of revenue includes: delivery costs, payment processing, tech infra
# Delivery/logistics portion estimated at ~60% of cost of revenue
DRIVER_ECONOMICS = {
    "delivery_cost_share_of_cor": 0.60,  # delivery cost as share of cost of revenue
    "avg_payout_per_order": 11.5,        # SAR — derived: COR*0.6 / orders
    "avg_orders_per_driver_day": 12,     # conservative for blended FT/PT
    "active_days_per_quarter": 78,       # ~26 days/month * 3
    "jahez_logi_drivers": 4_000,         # Jahez direct fleet (Q3 2025)
    "jahez_logi_target_pct": 0.60,       # target 60% of Jahez deliveries by 2026
}

# ─── Real Google Play Data (scraped 2026-03-05) ──────────────────────────────
# Source: google-play-scraper
REAL_APP_DATA = {
    "jahez": {
        "app_id": "net.jahez",
        "score": 2.85,
        "ratings": 28_427,
        "reviews": 11_753,
        "installs": 4_900_730,
    },
    "hungerstation": {
        "app_id": "com.hungerstation.android.web",
        "score": 4.51,
        "ratings": 326_569,
        "reviews": 62_571,
        "installs": 18_910_323,
    },
    "mrsool": {
        "app_id": "com.mrsool",
        "score": 4.10,
        "ratings": 372_385,
        "reviews": 128_553,
        "installs": 11_265_005,
    },
    "chefz": {
        "app_id": "com.nextwo.the_chefz",
        "score": 4.33,
        "ratings": 7_025,
        "reviews": 2_181,
        "installs": 1_046_884,
    },
}

# ─── Real Google Trends Data (fetched 2026-03-05) ────────────────────────────
# Source: pytrends, geo=SA, last 12 months
# HungerStation dominates search; Jahez lower (possibly brand is more
# established so less searching needed)
REAL_TRENDS_SNAPSHOT = {
    "consumer_demand": {
        "هنقرستيشن": 51,
        "شفز": 18,
        "جاهز توصيل": 1,
        "مرسول توصيل": 1,
    },
    "driver_registration": {
        "تسجيل هنقرستيشن": 100,
        "تسجيل مرسول": 15,
        "تسجيل شفز": 8,
        "تسجيل سائق جاهز": 0,
    },
}

# ─── Gig Economy Context ─────────────────────────────────────────────────────
# Source: HRSD / Saudi Gazette / GASTAT
GIG_ECONOMY_CONTEXT = {
    "workforce_gig_pct": 0.157,    # 15.7% of Saudi workforce in gig/informal (HRSD 2024)
    "freelance_registered": 2_250_000,  # Saudis on official freelance platform
    "freelance_contribution_sar_b": 72.5, # SAR billion
    "total_workforce_sa": 17_200_000,    # GASTAT Q3 2024
    "unemployment_rate": 0.032,          # 3.2% all-time low Q2 2025
    "saudi_unemployment": 0.063,         # 6.3% Q1 2025
    "wage_protection_establishments": 900_000,
    "wage_protection_employees": 8_500_000,
}
