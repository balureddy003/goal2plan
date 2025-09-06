from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from dkernel.config import get_settings


def _fallback_forecast(series: pd.Series, horizon: int) -> np.ndarray:
    # Simple deterministic moving average fallback
    window = min(14, max(3, len(series)))
    avg = float(series.tail(window).mean()) if len(series) else 0.0
    rng = np.random.default_rng(get_settings().SEED)
    noise = rng.normal(0, 0.05, size=horizon)
    forecast = np.maximum(0.0, avg * (1.0 + noise))
    return forecast


def forecast_demand(demand_daily: pd.DataFrame, horizon: int = 30) -> pd.DataFrame:
    """Per-SKU forecast over horizon. Fallback to moving average.

    Returns DataFrame[sku, date, forecast_qty]. Deterministic given SEED.
    """
    fc_rows = []
    last_date = pd.to_datetime(demand_daily["date"]).max()
    for sku, grp in demand_daily.groupby("sku"):
        series = grp.sort_values("date")["demand"].astype(float)
        values = _fallback_forecast(series, horizon)
        dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
        for d, q in zip(dates, values):
            fc_rows.append((sku, d, float(round(q, 3))))
    return pd.DataFrame(fc_rows, columns=["sku", "date", "forecast_qty"])  # type: ignore

