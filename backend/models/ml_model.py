"""
XGBoost one-quarter-ahead workforce forecasting with SHAP explainability.

Purpose:
  Given THIS quarter's proxy signals, predict NEXT quarter's workforce size.
  This is genuinely predictive — the model learns temporal dynamics that
  the estimation formula cannot capture (it only computes current quarter).

  SHAP reveals which current-quarter signals best forecast future workforce
  changes — actionable intelligence for policymakers.

Features (current quarter t):
  - Gross margin trend (financial health → future hiring capacity)
  - Take rate (platform maturity → future workforce needs)
  - Revenue growth rate (expansion signal → future demand)
  - Order volume (current demand → future driver needs)
  - Revenue per order (unit economics → sustainability)
  - Cost efficiency (operational health → growth capacity)
  - Quarter index (seasonality / time trend)

Target:
  - Workforce estimate at quarter t+1 (one step ahead)
"""

import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from backend.config import JAHEZ_FINANCIALS
from backend.models.estimators import get_time_series

FEATURE_LABELS = {
    "gross_margin_pct": "Gross Margin %",
    "take_rate_pct": "Take Rate %",
    "revenue_growth_qoq": "Revenue Growth (QoQ)",
    "order_volume_m": "Order Volume (M)",
    "revenue_per_order": "Revenue per Order (SAR)",
    "cost_efficiency": "Cost Efficiency (GP/CoR)",
    "quarter_index": "Time Trend",
}


def _build_feature_matrix():
    """
    Build one-step-ahead feature matrix.
    X[i] = features from quarter t, y[i] = workforce at quarter t+1.
    """
    series = get_time_series()
    if not series:
        return np.array([]), np.array([]), [], [], []

    feature_names = list(FEATURE_LABELS.keys())
    sorted_quarters = sorted(JAHEZ_FINANCIALS.keys())

    # First, compute features for ALL quarters
    all_features = []
    all_targets = []
    all_quarters = []

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

        all_features.append([
            gross_margin, take_rate, rev_growth, orders,
            rev_per_order, cost_efficiency, float(i),
        ])
        all_targets.append(match[0]["estimated"])
        all_quarters.append(q)

    # One-step-ahead: X[t] → y[t+1]
    X_rows = []
    y_rows = []
    input_quarters = []  # quarter of features (t)
    target_quarters = []  # quarter of target (t+1)

    for i in range(len(all_features) - 1):
        X_rows.append(all_features[i])
        y_rows.append(all_targets[i + 1])
        input_quarters.append(all_quarters[i])
        target_quarters.append(all_quarters[i + 1])

    # The latest quarter features are for the NEXT prediction (unseen future)
    latest_features = np.array([all_features[-1]])
    latest_quarter = all_quarters[-1]

    return (
        np.array(X_rows), np.array(y_rows),
        feature_names, input_quarters, target_quarters,
        latest_features, latest_quarter,
    )


def train_and_explain() -> dict:
    """
    Train one-step-ahead XGBoost forecaster and compute SHAP values.
    Uses expanding window validation (train on 1..t, test on t+1).
    """
    result = _build_feature_matrix()
    if len(result[0]) == 0:
        return {"error": "Not enough data"}

    X, y, feature_names, input_quarters, target_quarters, latest_X, latest_q = result

    if len(X) < 4:
        return {"error": "Not enough data points to train model"}

    # Expanding window cross-validation (more realistic than LOO for time series)
    min_train = 3
    ew_predictions = []
    ew_actuals = []
    ew_quarters = []

    for t in range(min_train, len(X)):
        X_train, y_train = X[:t], y[:t]
        X_test = X[t:t + 1]

        m = XGBRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.15,
            reg_alpha=1.0, reg_lambda=3.0, subsample=0.8, random_state=42,
        )
        m.fit(X_train, y_train)
        pred = m.predict(X_test)[0]
        ew_predictions.append(pred)
        ew_actuals.append(y[t])
        ew_quarters.append(target_quarters[t])

    ew_predictions = np.array(ew_predictions)
    ew_actuals = np.array(ew_actuals)

    mae = mean_absolute_error(ew_actuals, ew_predictions)
    r2 = r2_score(ew_actuals, ew_predictions)
    mape = np.mean(np.abs((ew_actuals - ew_predictions) / ew_actuals)) * 100

    # Train final model on ALL data for SHAP + next-quarter forecast
    model = XGBRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.15,
        reg_alpha=1.0, reg_lambda=3.0, subsample=0.8, random_state=42,
    )
    model.fit(X, y)

    # Forecast next quarter (unseen)
    next_quarter_pred = int(model.predict(latest_X)[0])

    # Derive next quarter label
    year, qnum = latest_q.split("_Q")
    next_qnum = int(qnum) + 1
    if next_qnum > 4:
        next_quarter_label = f"{int(year) + 1}_Q1"
    else:
        next_quarter_label = f"{year}_Q{next_qnum}"

    # SHAP
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values_all = explainer.shap_values(X)

        mean_shap = np.abs(shap_values_all).mean(axis=0)
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

        # SHAP breakdown for the next-quarter forecast
        latest_shap = explainer.shap_values(latest_X)[0]
        base_value = float(explainer.expected_value)
        forecast_breakdown = []
        for i, name in enumerate(feature_names):
            forecast_breakdown.append({
                "feature": name,
                "label": FEATURE_LABELS.get(name, name),
                "shap_value": round(float(latest_shap[i]), 0),
                "feature_value": round(float(latest_X[0][i]), 2),
                "direction": "positive" if latest_shap[i] > 0 else "negative",
            })
        forecast_breakdown.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    except Exception:
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
        forecast_breakdown = []
        base_value = float(y.mean())

    # Expanding window results for chart
    validation_results = []
    for i, q in enumerate(ew_quarters):
        validation_results.append({
            "quarter": q,
            "actual": int(ew_actuals[i]),
            "predicted": int(ew_predictions[i]),
            "error_pct": round(abs(ew_actuals[i] - ew_predictions[i]) / ew_actuals[i] * 100, 1),
        })

    return {
        "model": "XGBoost One-Step-Ahead Forecaster",
        "description": "Predicts next quarter's workforce from current quarter's proxy signals",
        "n_samples": len(X),
        "n_features": len(feature_names),
        "performance": {
            "r2_score": round(float(r2), 3),
            "mae": round(float(mae)),
            "mape_pct": round(float(mape), 1),
            "validation": "Expanding Window (time-series aware)",
        },
        "feature_importance": feature_importance,
        "next_quarter_forecast": {
            "input_quarter": latest_q,
            "forecast_quarter": next_quarter_label,
            "predicted_workers": next_quarter_pred,
            "base_value": round(base_value),
            "shap_breakdown": forecast_breakdown,
        },
        "validation_results": validation_results,
    }
