from __future__ import annotations

from typing import Dict, List


def build_plan(goal: Dict) -> List[dict]:
    """Build three simple plan options (cost, balanced, quality).

    Uses a base budget and service target to synthesize options with
    simple multiplicative deltas to illustrate tradeoffs.
    """
    base_budget = float(goal.get("monthly_budget_gbp") or 8000.0)
    target_service = float(goal.get("service_level_target") or 0.97)

    # Clamp
    target_service = max(0.0, min(1.0, target_service))

    options = [
        {
            "name": "cost-focused",
            "description": "Minimize spend with acceptable service compromise.",
            "estimated_monthly_cost": round(base_budget * 0.9, 2),
            "expected_service_level": max(0.0, round(min(target_service - 0.03, 0.99), 4)),
            "tradeoffs": "Lower cost but higher stockout risk.",
        },
        {
            "name": "balanced",
            "description": "Balance cost and service near target.",
            "estimated_monthly_cost": round(base_budget * 1.0, 2),
            "expected_service_level": round(target_service, 4),
            "tradeoffs": "Meets target with moderate spend.",
        },
        {
            "name": "quality-focused",
            "description": "Maximize service, accept higher spend.",
            "estimated_monthly_cost": round(base_budget * 1.1, 2),
            "expected_service_level": min(0.9999, round(target_service + 0.02, 4)),
            "tradeoffs": "Higher cost to reduce stockouts.",
        },
    ]

    return options

