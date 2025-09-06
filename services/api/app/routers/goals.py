from __future__ import annotations

import re
from typing import List, Set

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.models.goal_dsl import GoalDSL, GoalParseRequest


router = APIRouter(prefix="/goals", tags=["goals"], default_response_class=ORJSONResponse)


_CATEGORY_VOCAB: Set[str] = {
    "supplies",
    "food",
    "beverages",
    "cleaning",
    "maintenance",
    "it",
    "office",
}


def _parse_budget(text: str) -> float:
    # Prefer explicit currency symbol
    m = re.search(r"£\s*([0-9][0-9,]*)", text)
    if m:
        return float(m.group(1).replace(",", ""))
    # Or amounts labeled as GBP/pounds
    m = re.search(r"([0-9][0-9,]*)\s*(?:gbp|pounds)", text, re.I)
    if m:
        return float(m.group(1).replace(",", ""))
    # Or numbers in close context with 'budget' or 'month'
    for m in re.finditer(r"([0-9][0-9,]*)", text):
        start = m.start()
        window = text[max(0, start - 20) : min(len(text), start + 20)].lower()
        if "budget" in window or "month" in window:
            return float(m.group(1).replace(",", ""))
    return 0.0


def _parse_service_target(text: str) -> float:
    # Match 97% or 0.97 service
    m_pct = re.search(r"(\d{1,3})\s*%", text)
    if m_pct:
        return min(1.0, max(0.0, int(m_pct.group(1)) / 100.0))
    m_dec = re.search(r"(0\.\d+)\s*(?:service|target|fill|level)?", text, re.I)
    if m_dec:
        return min(1.0, max(0.0, float(m_dec.group(1))))
    return 0.95


def _parse_categories(text: str) -> List[str]:
    found: List[str] = []
    lower = text.lower()
    for cat in _CATEGORY_VOCAB:
        if cat in lower:
            found.append(cat)
    return found


def _parse_excludes(text: str) -> List[str]:
    excl: List[str] = []
    for m in re.finditer(r"(?:exclude|avoid)\s+([A-Z][\w\s&-]+)", text, re.I):
        excl.append(m.group(1).strip())
    return excl


@router.post("/parse", response_model=GoalDSL)
def parse_goal(req: GoalParseRequest) -> ORJSONResponse:
    text = req.goal_text
    budget = _parse_budget(text)
    service = _parse_service_target(text)
    categories = _parse_categories(text)
    excludes = _parse_excludes(text)

    goal = GoalDSL(
        monthly_budget_gbp=budget,
        service_level_target=service,
        categories=categories,
        excludes=excludes,
        constraints=[],
    )
    return ORJSONResponse(goal.model_dump())
