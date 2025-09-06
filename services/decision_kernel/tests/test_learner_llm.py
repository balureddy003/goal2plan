from dkernel.learner.llm_providers import provider_factory
from dkernel.learner.prompts import PLAN_CRITIQUE_SCHEMA, plan_critique_prompt


def test_llm_mock_provider_returns_json(monkeypatch):
    prov = provider_factory("mock")
    out = prov.complete_json(plan_critique_prompt("g", "d", "p"), PLAN_CRITIQUE_SCHEMA)
    assert set(["assumptions", "risks", "tweak_actions"]).issubset(out.keys())

