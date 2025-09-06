from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Constraint(BaseModel):
    """Represents a simple named constraint, e.g., 'avoid Supplier X'."""

    name: str
    details: Optional[str] = None


class GoalDSL(BaseModel):
    """Structured representation of a planning goal extracted from text."""

    monthly_budget_gbp: float = Field(ge=0)
    service_level_target: float = Field(ge=0, le=1)
    categories: List[str] = Field(default_factory=list)
    excludes: List[str] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=list)

    @field_validator("categories", "excludes")
    @classmethod
    def normalize_strs(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if s and s.strip()]


class GoalParseRequest(BaseModel):
    goal_text: str


class PlanOption(BaseModel):
    name: str
    description: str
    estimated_monthly_cost: float
    expected_service_level: float = Field(ge=0, le=1)
    tradeoffs: str


class GeneratePlanRequest(BaseModel):
    goal: GoalDSL


class KPI(BaseModel):
    name: str
    value: float


class FeedbackIngestRequest(BaseModel):
    plan_name: str
    kpis: List[KPI]
    notes: Optional[str] = None


class Evidence(BaseModel):
    """Minimal evidence representation used by the kernel."""

    nodes: List[dict]
    edges: List[dict]

