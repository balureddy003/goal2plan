from __future__ import annotations

from typing import Dict, List

import pandas as pd


def apply_policies(plan: Dict[str, object], constraints: Dict[str, List[str]] | None) -> Dict[str, object]:
    """Apply simple guardrails to allocation: ban vendors/categories.

    If allocations are removed, attempt reassignment to remaining cheapest suppliers.
    """
    constraints = constraints or {}
    banned_vendors = set(constraints.get("banned_vendors", []))

    allocation: pd.DataFrame = plan["allocation"]  # type: ignore[assignment]
    offers: pd.DataFrame | None = plan.get("offers") if isinstance(plan, dict) else None  # type: ignore
    if allocation.empty or not banned_vendors:
        return plan

    keep = allocation[~allocation["supplier"].isin(banned_vendors)].copy()
    removed = allocation[allocation["supplier"].isin(banned_vendors)]

    if not removed.empty and isinstance(offers, pd.DataFrame):
        # Try to reassign removed SKUs to next cheapest supplier
        for sku in removed["sku"].unique():
            need = float(removed[removed["sku"] == sku]["qty"].sum())
            cand = offers[(offers["sku"] == sku) & (~offers["supplier"].isin(banned_vendors))]
            if not cand.empty:
                best = cand.sort_values("price").iloc[0]
                qty = max(float(best["moq"]), need)
                cost = qty * float(best["price"])
                keep.loc[len(keep)] = {
                    "sku": sku,
                    "supplier": best["supplier"],
                    "price": float(best["price"]),
                    "qty": float(qty),
                    "cost": float(cost),
                    "lead_time_days": int(best["lead_time_days"]),
                }

    summary = plan.get("summary", {})
    if isinstance(summary, dict):
        summary = summary.copy()
    total_cost = float(keep["cost"].sum()) if not keep.empty else 0.0
    summary["total_cost"] = round(total_cost, 2)
    return {**plan, "allocation": keep.reset_index(drop=True), "summary": summary}

