from __future__ import annotations

from typing import Dict, Optional


def build_evidence_graph(
    goal: Dict,
    inputs: Dict,
    model_versions: Optional[Dict[str, str]] = None,
    plan: Optional[Dict] = None,
) -> Dict:
    """Return a provenance graph as nodes/edges dict.

    Nodes include goal, data nodes, forecaster, optimizer, policy, scoring.
    """
    nodes = [{"id": "goal", "type": "goal", "data": goal}]
    for name, present in (inputs or {}).items():
        nodes.append({"id": name, "type": "data", "present": bool(present)})
    for comp in ["forecaster", "optimizer", "policies", "scoring"]:
        nodes.append({"id": comp, "type": "component", "version": (model_versions or {}).get(comp)})
    if plan is not None:
        nodes.append({"id": "plan", "type": "artifact", "summary": plan.get("summary")})
    edges = [
        {"source": name, "target": "goal", "why": "input"} for name in inputs.keys()
    ]
    edges += [
        {"source": "forecaster", "target": "optimizer", "why": "forecast drives demand"},
        {"source": "optimizer", "target": "policies", "why": "policies adjust plan"},
        {"source": "policies", "target": "scoring", "why": "evaluate KPIs"},
    ]
    if plan is not None:
        edges.append({"source": "scoring", "target": "plan", "why": "produce summary"})
    return {"nodes": nodes, "edges": edges}


def to_networkx(graph: Dict):
    try:
        import networkx as nx  # type: ignore
    except Exception as e:  # pragma: no cover - optional
        raise RuntimeError("networkx not installed") from e
    G = nx.DiGraph()
    for n in graph["nodes"]:
        G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in graph["edges"]:
        G.add_edge(e["source"], e["target"], **{k: v for k, v in e.items() if k not in ("source", "target")})
    return G
