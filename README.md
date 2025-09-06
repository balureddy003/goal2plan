# SMB Planner – Goal→Plan MVP

FastAPI service that turns plain goals into structured plans with VoI questions, simple optimization stubs, and a feedback loop.

## Quick Start

### Local (no Docker)

Prereqs: Python 3.11, pip, virtualenv.

```
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e services/decision_kernel
pip install -e services/api[dev]
pytest -q
uvicorn app.main:app --reload --port 8000 --app-dir services/api/app
```

Open Swagger UI: http://localhost:8000/docs

### Docker Compose

1) Copy env and adjust if needed:

```
cp .env.example .env
```

2) Build and run:

```
docker compose up --build
```

API will be reachable at http://localhost:${API_PORT:-8000}/docs

## Project Layout

```
.
├── docker-compose.yml
├── .env.example
├── README.md
├── services/
│   ├── api/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/{goals.py,questions.py,plan.py,feedback.py}
│   │   │   └── models/goal_dsl.py
│   │   └── tests/test_*.py
│   └── decision_kernel/
│       ├── pyproject.toml
│       └── dkernel/{__init__.py,voi.py,optimizer.py,evidence.py}
└── templates/{sales.csv,inventory.csv,offers.csv}
```

## Curl Smoke Tests

Run these after starting the API (local or Docker):

```
curl -s http://localhost:8000/health

curl -s -X POST http://localhost:8000/goals/parse \
  -H 'content-type: application/json' \
  -d '{"goal_text":"Keep service at 97% with £8000/month budget, focus on supplies and food, exclude Supplier X"}'

curl -s -X POST http://localhost:8000/questions/next \
  -H 'content-type: application/json' \
  -d '{}'

curl -s -X POST http://localhost:8000/plan/generate \
  -H 'content-type: application/json' \
  -d '{"goal":{"monthly_budget_gbp":8000,"service_level_target":0.97,"categories":["supplies","food"],"excludes":["Supplier X"],"constraints":[]}}'

curl -s -X POST http://localhost:8000/feedback/ingest \
  -H 'content-type: application/json' \
  -d '{"plan_name":"balanced","kpis":[{"name":"service_level","value":0.965}],"notes":"look good"}'
```

## Notes

- Responses default to ORJSON for speed. FastAPI tags per router.
- Decision kernel is a separate local package installed alongside the API.
- Minimal heuristics now; optimization is stubbed for MVP.

