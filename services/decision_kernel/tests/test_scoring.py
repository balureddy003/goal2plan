from dkernel.data.synth import make_synthetic_data
from dkernel.features.pipeline import build_feature_tables
from dkernel.forecasting.darts_forecaster import forecast_demand
from dkernel.optimization.ortools_optimizer import optimize_plan
from dkernel.scoring import compute_kpis, score_plan


def test_scoring_monotonic_with_weights():
    s, i, o = make_synthetic_data(n_skus=5, days=15, n_suppliers=2)
    feats = build_feature_tables(s, i, o)
    fc = forecast_demand(feats["demand_daily"], horizon=7)
    res = optimize_plan(fc, feats["joined_offers"], service_target=0.9, budget=1e7)
    score_hi_service = score_plan(res, fc, {"service": 1.0, "cost": 0.0, "diversity": 0.0})
    score_hi_cost = score_plan(res, fc, {"service": 0.0, "cost": 1.0, "diversity": 0.0})
    # Service-weighted score should be higher than cost-weighted since cost term is negative
    assert score_hi_service["score"] > score_hi_cost["score"]

