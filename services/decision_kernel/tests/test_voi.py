from dkernel.data.synth import make_synthetic_data
from dkernel.features.pipeline import build_feature_tables
from dkernel.voi import pick_questions


def test_voi_ranking_missing():
    s, i, o = make_synthetic_data(n_skus=10, days=15, n_suppliers=2)
    feats = build_feature_tables(s, i, o)
    qs = pick_questions({"sales.csv": False}, {"demand_daily": feats["demand_daily"]})
    ids = [q["id"] for q in qs]
    assert set(ids) >= {"sales.csv", "inventory.csv", "offers.csv"}
    # ensure voi field present and sorted
    vois = [q["voi"] for q in qs]
    assert sorted(vois, reverse=True) == vois

