import pandas as pd
import pytest

from dkernel.data.synth import make_synthetic_data
from dkernel.data.adapters import load_sales_csv, load_inventory_csv, load_offers_csv


def test_synth_shapes(tmp_path):
    sales, inventory, offers = make_synthetic_data(n_skus=10, days=30, n_suppliers=3)
    assert {"date", "sku", "qty", "price"}.issubset(sales.columns)
    assert {"sku", "on_hand", "safety_stock"}.issubset(inventory.columns)
    assert {"supplier", "sku", "price", "moq", "lead_time_days", "validity_to"}.issubset(offers.columns)
    # Save and reload
    p = tmp_path
    sales.to_csv(p / "sales.csv", index=False)
    inventory.to_csv(p / "inventory.csv", index=False)
    offers.to_csv(p / "offers.csv", index=False)
    s2 = load_sales_csv(p / "sales.csv")
    i2 = load_inventory_csv(p / "inventory.csv")
    o2 = load_offers_csv(p / "offers.csv")
    assert len(s2) > 0 and len(i2) == 10 and len(o2) > 0


def test_loaders_invalid_columns(tmp_path):
    pd.DataFrame({"a": [1]}).to_csv(tmp_path / "x.csv", index=False)
    with pytest.raises(ValueError):
        load_sales_csv(tmp_path / "x.csv")
    with pytest.raises(ValueError):
        load_inventory_csv(tmp_path / "x.csv")
    with pytest.raises(ValueError):
        load_offers_csv(tmp_path / "x.csv")

