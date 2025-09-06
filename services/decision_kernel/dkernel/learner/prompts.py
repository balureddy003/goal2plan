from __future__ import annotations

PLAN_CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "tweak_actions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["assumptions", "risks", "tweak_actions"],
}

SYSTEM_CRITIQUE = (
    "You are a helpful assistant that outputs valid JSON conforming to a schema."
)


def plan_critique_prompt(goal: str, data_summary: str, plan_summary: str) -> str:
    return (
        f"System: {SYSTEM_CRITIQUE}\n"
        f"User: Analyze the following goal, data summary, and plan.\n"
        f"Goal: {goal}\n"
        f"Data: {data_summary}\n"
        f"Plan: {plan_summary}\n"
        f"Return JSON with keys: assumptions, risks, tweak_actions."
    )

