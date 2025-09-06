from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.models.goal_dsl import FeedbackIngestRequest


router = APIRouter(prefix="/feedback", tags=["feedback"], default_response_class=ORJSONResponse)


@router.post("/ingest")
def ingest_feedback(req: FeedbackIngestRequest) -> ORJSONResponse:
    return ORJSONResponse({"ok": True, "received": req.model_dump()})

