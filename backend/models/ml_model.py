"""
XGBoost proxy-to-workforce calibration model with SHAP explainability.

Purpose:
  Given INDEPENDENT proxy signals (not the ones used in the estimation
  formula), train a model that predicts workforce size. This validates
  whether non-traditional data sources genuinely correlate with
  platform-based employment.

  Key design choice: features are PROXY signals only — not the inputs
  to the estimation formula. This way SHAP shows which external data
  sources are actually predictive, rather than reflecting our own math.

Features (all independent proxies):
  - Gross margin trend (financial health → hiring capacity)
  - Take rate (platform maturity signal)
  - Revenue growth rate (expansion signal)
  - Order volume (demand signal)
  - Quarter index (seasonality / time trend)

Target:
  - Triangulated worker estimate (from estimators.py)
"""

import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import mean_absolute_error, r2_score

from backend.config import JAHEZ_FINANCIALS
from backend.models.estimators import get_time_series

# Human-readable feature labels for the dashboard
FEATURE_LABELS = {
    "gross_margin_pct": "Gross Margin %",
    "take_rate_pct": "Take Rate %",
    "revenue_growth_qoq": "Revenue Growth (QoQ)",
    "order_volume_m": "Order Volume (M)",
    "revenue_per_order": "Revenue per Order (SAR)",
    "cost_efficiency": "Cost Efficiency (GP/CoR)",
    "quarter_index": "Time Trend",
}


def _build_feature_matrix() -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    """
    Build feature matrix from quarterly data.
    Features are proxy signals NOT used directly in the estimation formula.
    """
    series = get_time_series()
    if not series:
        return np.array([]), np.array([]), [], []

    feature_names = list(FEATURE_LABELS.keys())

    X_rows = []
    y_rows = []
    quarters = []

    sorted_quarters = sorted(JAHEZ_FINANCIALS.keys())

    for i, q in enumerate(sorted_quarters):
        fin = JAHEZ_FINANCIALS[q]
        rev = fin["revenue_sar"]
        cor = fin["cost_of_revenue_sar"]
        gp = fin["gross_profit_sar"]
        orders = fin["orders_m"]

        gross_margin = (gp / rev * 100) if rev else 0
        take_rate = fin["take_rate"] * 100
        rev_per_order = (rev / (orders * 1e6)) if orders else 0
        cost_efficiency = (gp / cor) if cor else 0

        if i > 0:
            prev = JAHEZ_FINANCIALS[sorted_quarters[i - 1]]
            rev_growth = (rev - prev["revenue_sar"]) / prev["revenue_sar"] * 100
        else:
            rev_growth = 0.0

        match = [s for s in series if s["quarter"] == q]
        if not match:
            continue

        target = match[0]["estimated"]

        X_rows.append([
            gross_margin,
            take_rate,
            rev_growth,
            orders,
            rev_per_order,
            cost_efficiency,
            float(i),
        ])
        y_rows.append(target)
        quarters.append(q)

    return np.array(X_rows), np.array(y_rows), feature_names, quarters


def train_and_explain() -> dict:
    """
    Train XGBoost and compute SHAP values.
    Returns feature importance, per-quarter explanations, and model accuracy.
    """
    X, y, feature_names, quarters = _build_feature_matrix()

    if len(X) < 4:
        return {"error": "Not enough data points to train model"}

    # Train on all data for SHAP
    model = XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.15,
        reg_alpha=1.0,
        reg_lambda=3.0,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X, y)

    # Leave-one-out cross-validation
    loo = LeaveOneOut()
    loo_predictions = np.zeros(len(y))
    for train_idx, test_idx in loo.split(X):
        m = XGBRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.15,
            reg_alpha=1.0, reg_lambda=3.0, subsample=0.8, random_state=42,
        )
        m.fit(X[train_idx], y[train_idx])
        loo_predictions[test_idx] = m.predict(X[test_idx])

    mae = mean_absolute_error(y, loo_predictions)
    r2 = r2_score(y, loo_predictions)
    mape = np.mean(np.abs((y - loo_predictions) / y)) * 100

    # SHAP
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        mean_shap = np.abs(shap_values).mean(axis=0)
        total_shap = mean_shap.sum()
        shap_pct = (mean_shap / total_shap * 100) if total_shap > 0 else mean_shap

        feature_importance = []
        for i, name in enumerate(feature_names):
            feature_importance.append({
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "importance_pct": round(float(shap_pct[i]), 1),
                "mean_shap": round(float(mean_shap[i]), 1),
            })
        feature_importance.sort(key=lambda x: x["importance_pct"], reverse=True)

        # Per-quarter SHAP for latest quarter
        latest_shap = shap_values[-1]
        base_value = float(explainer.expected_value)
        latest_breakdown = []
        for i, name in enumerate(feature_names):
            latest_breakdown.append({
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "shap_value": round(float(latest_shap[i]), 0),
                "feature_value": round(float(X[-1][i]), 2),
                "direction": "positive" if latest_shap[i] > 0 else "negative",
            })
        latest_breakdown.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    except Exception as e:
        raw_importance = model.feature_importances_
        total = raw_importance.sum()
        feature_importance = []
        for i, name in enumerate(feature_names):
            feature_importance.append({
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "importance_pct": round(float(raw_importance[i] / total * 100), 1),
                "mean_shap": 0,
            })
        feature_importance.sort(key=lambda x: x["importance_pct"], reverse=True)
        latest_breakdown = []
        base_value = float(y.mean())

    # Predictions vs actuals
    predictions = model.predict(X)
    pred_vs_actual = []
    for i, q in enumerate(quarters):
        pred_vs_actual.append({
            "quarter": q,
            "actual": int(y[i]),
            "predicted": int(predictions[i]),
            "loo_predicted": int(loo_predictions[i]),
            "error_pct": round(abs(y[i] - loo_predictions[i]) / y[i] * 100, 1),
        })

    return {
        "model": "XGBoost Regressor",
        "n_samples": len(X),
        "n_features": len(feature_names),
        "performance": {
            "r2_score": round(float(r2), 3),
            "mae": round(float(mae)),
            "mape_pct": round(float(mape), 1),
            "validation": "Leave-One-Out Cross-Validation",
        },
        "feature_importance": feature_importance,
        "latest_quarter_explanation": {
            "quarter": quarters[-1],
            "predicted": int(predictions[-1]),
            "actual": int(y[-1]),
            "base_value": round(base_value),
            "shap_breakdown": latest_breakdown,
        },
        "predictions_vs_actual": pred_vs_actual,
    }
