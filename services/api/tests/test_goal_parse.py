from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_goal_parse_budget_and_service():
    payload = {
        "goal_text": "Keep service at 97% with £8,000/month budget; focus on supplies and food; exclude Supplier X",
    }
    r = client.post("/goals/parse", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["monthly_budget_gbp"] == 8000
    assert abs(data["service_level_target"] - 0.97) < 1e-6
    assert "supplies" in data["categories"]
    assert "food" in data["categories"]
    assert "Supplier X" in data["excludes"]

