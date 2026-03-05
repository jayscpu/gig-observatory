"""
Tadawul Financial Data Collector for Jahez (Symbol 6017).

Derives Jahez driver count from audited quarterly financial filings.
This is the anchor estimate — the strongest signal in the observatory.

Source: Tadawul 6017 quarterly filings via stockanalysis.com
"""

from backend.config import JAHEZ_FINANCIALS, DRIVER_ECONOMICS


def estimate_workers_from_financials(quarter: str) -> dict:
    """
    Core anchor method: derive Jahez worker count from audited financials.

    Logic:
      1. cost_of_revenue * delivery_share = estimated delivery spend
      2. delivery_spend / avg_payout_per_order = implied driver-fulfilled orders
      3. orders / (orders_per_driver_per_day * active_days) = FTE drivers
      4. Cross-check: reported orders_m vs implied orders for consistency

    We use cost of revenue (not just delivery cost) because Jahez doesn't
    break out delivery cost separately. We estimate 60% of CoR goes to
    driver payouts based on industry benchmarks.
    """
    fin = JAHEZ_FINANCIALS.get(quarter)
    if not fin:
        return {"error": f"No financial data for {quarter}"}

    eco = DRIVER_ECONOMICS
    cor = fin["cost_of_revenue_sar"]

    # Estimated delivery spend (driver payouts portion of cost of revenue)
    delivery_spend = cor * eco["delivery_cost_share_of_cor"]

    # Implied orders from spend
    implied_orders = delivery_spend / eco["avg_payout_per_order"]

    # Reported orders for cross-check
    reported_orders = fin["orders_m"] * 1_000_000

    # FTE drivers needed to fulfill reported orders
    fte_from_reported = reported_orders / (
        eco["avg_orders_per_driver_day"] * eco["active_days_per_quarter"]
    )

    # FTE from financial implication
    fte_from_financial = implied_orders / (
        eco["avg_orders_per_driver_day"] * eco["active_days_per_quarter"]
    )

    # Average the two approaches for robustness
    fte_avg = (fte_from_reported + fte_from_financial) / 2

    # Confidence band: range between the two methods +/- 10%
    low_fte = min(fte_from_reported, fte_from_financial) * 0.90
    high_fte = max(fte_from_reported, fte_from_financial) * 1.10

    return {
        "quarter": quarter,
        "platform": "jahez",
        "method": "financial_anchor",
        "revenue_sar": fin["revenue_sar"],
        "cost_of_revenue_sar": cor,
        "estimated_delivery_spend_sar": round(delivery_spend),
        "implied_orders": round(implied_orders),
        "reported_orders_m": fin["orders_m"],
        "fte_from_financial": round(fte_from_financial),
        "fte_from_reported": round(fte_from_reported),
        "estimated_workers": round(fte_avg),
        "confidence_low": round(low_fte),
        "confidence_high": round(high_fte),
        "take_rate": fin["take_rate"],
    }


def get_all_quarterly_estimates() -> list[dict]:
    """Return anchor estimates for all available quarters."""
    results = []
    for quarter in sorted(JAHEZ_FINANCIALS.keys()):
        est = estimate_workers_from_financials(quarter)
        if "error" not in est:
            results.append(est)
    return results
