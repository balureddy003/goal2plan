from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_questions_all_missing():
    r = client.post("/questions/next", json={})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    ids = {i["id"] for i in items}
    assert {"sales.csv", "inventory.csv", "offers.csv"}.issubset(ids)


def test_questions_one_provided():
    r = client.post("/questions/next", json={"sales.csv": True})
    assert r.status_code == 200
    items = r.json()
    ids = {i["id"] for i in items}
    assert "sales.csv" not in ids
    assert {"inventory.csv", "offers.csv"}.issubset(ids)

