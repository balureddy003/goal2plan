from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def build_feature_tables(
    sales: pd.DataFrame, inventory: pd.DataFrame, offers: pd.DataFrame
) -> Dict[str, pd.DataFrame]:
    # demand_daily
    demand_daily = (
        sales.groupby(["date", "sku"], as_index=False)["qty"].sum().rename(columns={"qty": "demand"})
    )

    # sku_stats with ABC by revenue share
    revenue = sales.assign(rev=lambda d: d["qty"] * d["price"]).groupby("sku")["rev"].sum()
    revenue = revenue.sort_values(ascending=False)
    cum_share = (revenue / revenue.sum()).cumsum()
    def abc(score: float) -> str:
        if score <= 0.8:
            return "A"
        if score <= 0.95:
            return "B"
        return "C"
    sku_stats = (
        pd.DataFrame({"sku": revenue.index, "cum_share": cum_share.values})
        .assign(ABC=lambda d: d["cum_share"].map(abc))
        .reset_index(drop=True)
    )

    # supplier_reliability (simple heuristic: inverse of lead time noise)
    rel = (
        offers.groupby("supplier")["lead_time_days"].mean().rename("avg_lead").reset_index()
    )
    rel["reliability"] = 1.0 - (rel["avg_lead"] - rel["avg_lead"].min()) / (
        rel["avg_lead"].max() - rel["avg_lead"].min() + 1e-6
    )

    # joined_offers: join offers to sku_stats
    joined_offers = offers.merge(sku_stats[["sku", "ABC"]], on="sku", how="left")
    joined_offers["ABC"] = joined_offers["ABC"].fillna("C")

    return {
        "demand_daily": demand_daily,
        "sku_stats": sku_stats,
        "supplier_reliability": rel,
        "joined_offers": joined_offers,
        "inventory": inventory.copy(),
    }

