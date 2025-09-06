from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from dkernel.learner.llm_providers import provider_factory
from dkernel.learner.prompts import PLAN_CRITIQUE_SCHEMA, plan_critique_prompt


def train_llm(dataset_path: str, output_dir: str) -> str:
    """Training stub: select prompt set and save. Returns path to artifact."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    # For MVP, just save the schema and a chosen template flag
    artifact = {"selected": "critique_v1", "schema": PLAN_CRITIQUE_SCHEMA}
    path = out / "prompt_set.json"
    path.write_text(json.dumps(artifact, indent=2))
    return str(path)


def evaluate_llm(dataset_path: str, provider_name: str | None = None) -> Dict[str, float]:
    prov = provider_factory(provider_name)
    total = 0
    valid = 0
    with open(dataset_path, "r") as f:
        for line in f:
            ex = json.loads(line)
            prompt = plan_critique_prompt(ex.get("goal", ""), ex.get("data_summary", ""), ex.get("base_plan", ""))
            try:
                _ = prov.complete_json(prompt, PLAN_CRITIQUE_SCHEMA)
                valid += 1
            except Exception:
                pass
            total += 1
    report = {"n": total, "json_valid": float(valid) / max(1, total)}
    out_path = Path(dataset_path).with_suffix(".report.json")
    out_path.write_text(json.dumps(report, indent=2))
    return report

