from dkernel.data.synth import make_synthetic_data
from dkernel.features.pipeline import build_feature_tables


def test_build_feature_tables():
    s, i, o = make_synthetic_data(n_skus=12, days=20, n_suppliers=3)
    feats = build_feature_tables(s, i, o)
    assert set(["demand_daily", "sku_stats", "supplier_reliability", "joined_offers", "inventory"]) <= set(feats.keys())
    assert {"date", "sku", "demand"}.issubset(feats["demand_daily"].columns)
    assert {"sku", "ABC"}.issubset(feats["sku_stats"].columns)
    assert {"supplier", "reliability"}.issubset(feats["supplier_reliability"].columns)
    assert {"supplier", "sku", "price", "moq", "lead_time_days"}.issubset(feats["joined_offers"].columns)

