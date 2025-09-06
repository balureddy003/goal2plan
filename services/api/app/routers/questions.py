from __future__ import annotations

from typing import Dict, List
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse


router = APIRouter(prefix="/questions", tags=["questions"], default_response_class=ORJSONResponse)


_REQUIRED_FILES = ["sales.csv", "inventory.csv", "offers.csv"]


def _voi_rationale(name: str) -> str:
    why = {
        "sales.csv": "Recent sales variability drives demand forecasts and stock risk.",
        "inventory.csv": "Current on-hand and safety stock determine service feasibility.",
        "offers.csv": "Supplier pricing, MOQs, and lead times affect cost-service tradeoffs.",
    }
    return why.get(name, "Improves plan quality via reduced uncertainty.")


@router.post("/next")
def next_questions(payload: Dict[str, bool] | None = None) -> ORJSONResponse:
    provided = payload or {}
    missing = [f for f in _REQUIRED_FILES if not provided.get(f, False)]
    items: List[dict] = [
        {"id": f, "text": f"Please provide {f}", "why": _voi_rationale(f)} for f in missing
    ]
    return ORJSONResponse(items)

