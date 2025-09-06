from pathlib import Path

from typer.testing import CliRunner

from dkernel.cli import app


def test_cli_synth_and_plan(tmp_path: Path):
    runner = CliRunner()
    out_dir = tmp_path / "data"
    # synth data
    r = runner.invoke(app, ["synth", "--out", str(out_dir)])
    assert r.exit_code == 0
    sales = out_dir / "sales.csv"
    inv = out_dir / "inventory.csv"
    offers = out_dir / "offers.csv"
    assert sales.exists() and inv.exists() and offers.exists()

    # plan
    plan_path = tmp_path / "plan.json"
    r2 = runner.invoke(
        app,
        [
            "plan",
            "--sales",
            str(sales),
            "--inventory",
            str(inv),
            "--offers",
            str(offers),
            "--budget",
            "8000",
            "--slt",
            "0.97",
            "--out",
            str(plan_path),
        ],
    )
    assert r2.exit_code == 0, r2.output
    assert plan_path.exists()

