from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


def pick_questions(
    context: Dict[str, bool] | None = None,
    data_health: Optional[Dict[str, pd.DataFrame]] = None,
) -> List[dict]:
    """Return ranked VoI questions based on missingness and uncertainty.

    Heuristic: VoI ~ uncertainty (A-class demand variance) * missingness flag.
    """
    required = ["sales.csv", "inventory.csv", "offers.csv"]
    provided = context or {}
    missing = {f: (not provided.get(f, False)) for f in required}

    # Uncertainty proxy
    uncert = {
        "sales.csv": 1.0,
        "inventory.csv": 0.6,
        "offers.csv": 0.7,
    }
    if data_health and "demand_daily" in data_health:
        dd = data_health["demand_daily"]
        # scale by coefficient of variation
        if not dd.empty:
            cv = (
                dd.groupby("sku")["demand"].agg(lambda s: (s.std() / (s.mean() + 1e-6)))
            ).mean()
            if pd.notnull(cv):
                uncert["sales.csv"] = float(min(1.5, max(0.5, cv)))

    why_map = {
        "sales.csv": "Forecast uncertainty high for key SKUs; need last 90d sales.",
        "inventory.csv": "On-hand/safety stock needed to assess service feasibility.",
        "offers.csv": "Supplier terms required to optimize cost and service.",
    }

    items = []
    for f in required:
        if missing[f]:
            voi = round(uncert.get(f, 0.5) * 1.0, 3)
            items.append({"id": f, "text": f"Please provide {f}", "why": why_map[f], "voi": voi})
    items.sort(key=lambda x: x.get("voi", 0), reverse=True)
    return items
