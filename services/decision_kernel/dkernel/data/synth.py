from __future__ import annotations

from math import sin, pi
from typing import Tuple

import numpy as np
import pandas as pd

from dkernel.config import get_settings


def make_synthetic_data(
    n_skus: int = 100, days: int = 120, n_suppliers: int = 5
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate synthetic sales, inventory, and offers.

    Deterministic with Settings.SEED.
    """
    rng = np.random.default_rng(get_settings().SEED)

    # SKUs and suppliers
    skus = [f"SKU-{i:03d}" for i in range(n_skus)]
    suppliers = [f"Supplier {chr(65+i)}" for i in range(n_suppliers)]

    # Dates
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")

    # Base demand per SKU
    base = rng.uniform(5, 50, size=n_skus)
    seasonal_amp = rng.uniform(0.1, 0.4, size=n_skus)

    sales_rows = []
    for d_idx, day in enumerate(dates):
        season = 1.0 + 0.3 * sin(2 * pi * (d_idx % 30) / 30)
        noise = rng.normal(1.0, 0.1, size=n_skus)
        qty = np.maximum(0, np.round(base * season * noise)).astype(int)
        price = rng.uniform(5.0, 25.0, size=n_skus)
        for i, sku in enumerate(skus):
            if qty[i] == 0 and rng.random() < 0.5:
                continue
            sales_rows.append((day, sku, int(qty[i]), float(round(price[i], 2))))
    sales = pd.DataFrame(sales_rows, columns=["date", "sku", "qty", "price"])  # type: ignore

    # Inventory: on_hand around weekly demand, safety_stock fraction
    inv_on_hand = np.maximum(0, (base * 7 * rng.uniform(0.8, 1.2, size=n_skus))).astype(int)
    safety_stock = np.maximum(1, (base * 2 * rng.uniform(0.5, 1.0, size=n_skus))).astype(int)
    inventory = pd.DataFrame(
        {
            "sku": skus,
            "on_hand": inv_on_hand,
            "safety_stock": safety_stock,
        }
    )

    # Offers: each SKU from 2 suppliers
    offer_rows = []
    for sku_idx, sku in enumerate(skus):
        chosen = rng.choice(suppliers, size=min(2, n_suppliers), replace=False)
        base_price = rng.uniform(5, 25)
        for s in chosen:
            moq = int(rng.integers(10, 100))
            lead = int(rng.integers(5, 21))
            price = round(base_price * rng.uniform(0.9, 1.1), 2)
            offer_rows.append(
                (s, sku, price, moq, lead, (pd.Timestamp.today() + pd.Timedelta(days=180)))
            )
    offers = pd.DataFrame(
        offer_rows,
        columns=["supplier", "sku", "price", "moq", "lead_time_days", "validity_to"],
    )

    return sales, inventory, offers

