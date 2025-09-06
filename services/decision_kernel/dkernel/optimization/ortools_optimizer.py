from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd


def _greedy_allocate(
    forecast: pd.DataFrame,
    offers: pd.DataFrame,
    service_target: float,
    budget: float,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    # aggregate demand per SKU
    demand = forecast.groupby("sku")["forecast_qty"].sum().rename("demand").reset_index()
    offers_sorted = offers.sort_values(["sku", "price"]).copy()
    alloc_rows = []
    total_cost = 0.0
    remaining_budget = budget
    for _, row in demand.iterrows():
        sku = row["sku"]
        need = float(row["demand"]) * service_target
        if need <= 0:
            continue
        avail = offers_sorted[offers_sorted["sku"] == sku]
        if avail.empty:
            continue
        best = avail.iloc[0]
        qty = max(float(best["moq"]), float(np.ceil(need)))
        cost = qty * float(best["price"])
        total_cost += cost
        remaining_budget -= cost
        alloc_rows.append(
            {
                "sku": sku,
                "supplier": best["supplier"],
                "price": float(best["price"]),
                "qty": float(qty),
                "cost": float(cost),
                "lead_time_days": int(best["lead_time_days"]),
            }
        )
    allocation = pd.DataFrame(alloc_rows)
    summary = {
        "total_cost": float(round(total_cost, 2)),
        "within_budget": bool(total_cost <= budget),
        "budget": float(budget),
        "service_target": float(service_target),
    }
    return allocation, summary


def optimize_plan(
    forecast: pd.DataFrame,
    offers: pd.DataFrame,
    service_target: float,
    budget: float,
) -> Dict[str, object]:
    """Return allocation and summary. Fallback greedy to avoid heavy deps.

    Schema:
      {
        "allocation": DataFrame columns [sku,supplier,price,qty,cost,lead_time_days],
        "summary": {total_cost, within_budget, budget, service_target}
      }
    """
    allocation, summary = _greedy_allocate(forecast, offers, service_target, budget)
    return {"allocation": allocation, "summary": summary}

