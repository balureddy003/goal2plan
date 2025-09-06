from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
import typer

from dkernel.config import get_settings
from dkernel.data.synth import make_synthetic_data
from dkernel.data.adapters import load_sales_csv, load_inventory_csv, load_offers_csv
from dkernel.features.pipeline import build_feature_tables
from dkernel.forecasting.darts_forecaster import forecast_demand
from dkernel.optimization.ortools_optimizer import optimize_plan
from dkernel.scoring import compute_kpis, score_plan
from dkernel.learner.trainer import train_llm, evaluate_llm


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command("synth")
def cmd_synth(out: str = typer.Option("./_out/data", help="Output directory for CSVs")):
    outp = Path(out)
    outp.mkdir(parents=True, exist_ok=True)
    sales, inventory, offers = make_synthetic_data()
    sales.to_csv(outp / "sales.csv", index=False)
    inventory.to_csv(outp / "inventory.csv", index=False)
    offers.to_csv(outp / "offers.csv", index=False)
    typer.echo(f"Wrote synthetic data to {outp}")


@app.command("plan")
def cmd_plan(
    sales: str = typer.Option(..., help="Path to sales.csv"),
    inventory: str = typer.Option(..., help="Path to inventory.csv"),
    offers: str = typer.Option(..., help="Path to offers.csv"),
    budget: float = typer.Option(8000.0, help="Monthly budget GBP"),
    slt: float = typer.Option(0.97, help="Service level target [0-1]"),
    out: str = typer.Option("./_out/plan.json", help="Where to save plan JSON"),
):
    s = load_sales_csv(sales)
    i = load_inventory_csv(inventory)
    o = load_offers_csv(offers)
    feats = build_feature_tables(s, i, o)
    forecast = forecast_demand(feats["demand_daily"], horizon=30)
    result = optimize_plan(forecast, feats["joined_offers"], service_target=slt, budget=budget)
    result["offers"] = feats["joined_offers"]
    kpis = compute_kpis(result, forecast)
    summary = {**result["summary"], **kpis}
    outp = Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({"summary": summary}, indent=2))
    typer.echo(json.dumps(summary, indent=2))


@app.command("train-llm")
def cmd_train_llm(
    data: str = typer.Option(..., help="Path to dataset.jsonl"),
    out: str = typer.Option("./_out/llm", help="Output directory"),
):
    path = train_llm(data, out)
    typer.echo(f"Saved: {path}")


@app.command("eval-llm")
def cmd_eval_llm(
    data: str = typer.Option(..., help="Path to dataset.jsonl"),
    provider: Optional[str] = typer.Option(None, help="Provider name override"),
):
    report = evaluate_llm(data, provider_name=provider)
    typer.echo(json.dumps(report, indent=2))


@app.command("bench")
def cmd_bench(runs: int = typer.Option(3, help="Number of runs"), seed: Optional[int] = None):
    from dkernel.config import Settings

    if seed is not None:
        # Update cached settings seed for determinism per run
        Settings(SEED=seed)
    results = []
    for _ in range(runs):
        s, i, o = make_synthetic_data()
        feats = build_feature_tables(s, i, o)
        fc = forecast_demand(feats["demand_daily"], horizon=30)
        res = optimize_plan(fc, feats["joined_offers"], service_target=0.97, budget=8000)
        res["offers"] = feats["joined_offers"]
        kpis = compute_kpis(res, fc)
        results.append(kpis)
    outp = Path("./_out/bench.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({"runs": results}, indent=2))
    typer.echo(json.dumps({"runs": results}, indent=2))


def _main() -> None:  # pragma: no cover
    import sys
    # When invoked without args (e.g., VS Code run), show help and exit 0 instead of raising
    if len(sys.argv) == 1:
        from typer.main import get_command
        import click

        cmd = get_command(app)
        with click.Context(cmd) as ctx:
            click.echo(cmd.get_help(ctx))
        raise SystemExit(0)
    app()


if __name__ == "__main__":  # pragma: no cover
    _main()
