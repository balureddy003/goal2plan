from dkernel.data.synth import make_synthetic_data
from dkernel.features.pipeline import build_feature_tables
from dkernel.forecasting.darts_forecaster import forecast_demand


def test_forecast_demand():
    s, i, o = make_synthetic_data(n_skus=8, days=30, n_suppliers=2)
    feats = build_feature_tables(s, i, o)
    fc = forecast_demand(feats["demand_daily"], horizon=10)
    assert set(["sku", "date", "forecast_qty"]).issubset(fc.columns)
    assert fc["sku"].nunique() == feats["demand_daily"]["sku"].nunique()
    # horizon rows per sku
    counts = fc.groupby("sku").size()
    assert counts.min() == 10 and counts.max() == 10

