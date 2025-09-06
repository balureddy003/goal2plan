from dkernel.data.synth import make_synthetic_data
from dkernel.features.pipeline import build_feature_tables
from dkernel.forecasting.darts_forecaster import forecast_demand
from dkernel.optimization.ortools_optimizer import optimize_plan


def test_optimize_plan_feasible():
    s, i, o = make_synthetic_data(n_skus=6, days=20, n_suppliers=3)
    feats = build_feature_tables(s, i, o)
    fc = forecast_demand(feats["demand_daily"], horizon=7)
    res = optimize_plan(fc, feats["joined_offers"], service_target=0.9, budget=1e7)
    alloc = res["allocation"]
    assert not alloc.empty
    assert {"sku", "supplier", "qty", "cost"}.issubset(alloc.columns)
    assert res["summary"]["total_cost"] > 0

