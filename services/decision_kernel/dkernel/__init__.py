"""Decision kernel exports and convenience functions."""

from .config import get_settings
from .voi import pick_questions
from .optimizer import build_plan  # legacy export
from .evidence import build_evidence_graph

__all__ = [
    "get_settings",
    "pick_questions",
    "build_plan",
    "build_evidence_graph",
]
