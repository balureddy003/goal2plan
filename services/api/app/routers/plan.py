from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

from app.models.goal_dsl import GeneratePlanRequest, PlanOption

# Import decision kernel (installed via Docker and local instructions)
from dkernel import optimizer as dk_optimizer


router = APIRouter(prefix="/plan", tags=["plan"], default_response_class=ORJSONResponse)


@router.post("/generate", response_model=list[PlanOption])
def generate_plan(req: GeneratePlanRequest) -> ORJSONResponse:
    goal_dict = req.goal.model_dump()
    raw_options = dk_optimizer.build_plan(goal_dict)

    options: list[PlanOption] = []
    for ro in raw_options:
        options.append(
            PlanOption(
                name=ro["name"],
                description=ro.get("description", ro["name"]),
                estimated_monthly_cost=ro["estimated_monthly_cost"],
                expected_service_level=ro["expected_service_level"],
                tradeoffs=ro.get("tradeoffs", ""),
            )
        )

    return ORJSONResponse([o.model_dump() for o in options])

