from dkernel.evidence import build_evidence_graph


def test_evidence_graph_contents():
    goal = {"monthly_budget_gbp": 8000, "service_level_target": 0.97}
    inputs = {"sales.csv": True, "inventory.csv": True, "offers.csv": True}
    versions = {"forecaster": "fallback-0.1", "optimizer": "greedy-0.1", "policies": "simple-0.1", "scoring": "v0.1"}
    plan = {"summary": {"total_cost": 1000}}
    g = build_evidence_graph(goal, inputs, versions, plan)
    ids = {n["id"] for n in g["nodes"]}
    assert {"goal", "forecaster", "optimizer", "policies", "scoring", "plan"}.issubset(ids)

