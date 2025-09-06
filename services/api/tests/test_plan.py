from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_plan_generate_returns_three_options():
    payload = {
        "goal": {
            "monthly_budget_gbp": 8000,
            "service_level_target": 0.97,
            "categories": ["supplies"],
            "excludes": [],
            "constraints": [],
        }
    }
    r = client.post("/plan/generate", json=payload)
    assert r.status_code == 200
    options = r.json()
    assert isinstance(options, list)
    assert len(options) == 3
    for o in options:
        assert "estimated_monthly_cost" in o
        assert "expected_service_level" in o

