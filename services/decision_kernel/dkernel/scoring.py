from __future__ import annotations

from typing import Dict

import pandas as pd


def compute_kpis(plan: Dict[str, object], forecast: pd.DataFrame) -> Dict[str, float]:
    alloc: pd.DataFrame = plan["allocation"]  # type: ignore[assignment]
    demand = forecast.groupby("sku")["forecast_qty"].sum().rename("demand")
    bought = alloc.groupby("sku")["qty"].sum().rename("bought") if not alloc.empty else pd.Series(dtype=float)
    df = pd.concat([demand, bought], axis=1).fillna(0)
    service = (df["bought"] / (df["demand"] + 1e-6)).clip(0, 1).mean() if not df.empty else 0.0
    total_cost = float(alloc["cost"].sum()) if not alloc.empty else 0.0
    suppliers_used = alloc["supplier"].nunique() if not alloc.empty else 0
    supplier_diversity = float(suppliers_used / max(1, len(alloc))) if not alloc.empty else 0.0
    stockout_risk = float(1.0 - service)
    return {
        "total_cost": round(total_cost, 2),
        "service_level": round(float(service), 4),
        "stockout_risk": round(stockout_risk, 4),
        "supplier_diversity": round(supplier_diversity, 4),
    }


def score_plan(plan: Dict[str, object], forecast: pd.DataFrame, weights: Dict[str, float]) -> Dict[str, object]:
    kpis = compute_kpis(plan, forecast)
    w = {"cost": 0.3, "service": 0.5, "diversity": 0.2}
    w.update(weights or {})
    # Normalize cost by itself to avoid needing external baseline (lower is better)
    cost_term = -kpis["total_cost"]
    service_term = kpis["service_level"] * 1000
    diversity_term = kpis["supplier_diversity"] * 100
    total = w["cost"] * cost_term + w["service"] * service_term + w["diversity"] * diversity_term
    return {"score": round(float(total), 3), "kpis": kpis, "weights": w}

