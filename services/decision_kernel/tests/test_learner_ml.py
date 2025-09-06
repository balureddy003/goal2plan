import numpy as np
import pandas as pd

from dkernel.learner.ml import fit_ml, predict_adjustments


def test_ml_fit_predict_improves_rmse():
    # Synthetic linear relation
    rng = np.random.default_rng(42)
    X = rng.normal(size=(100, 3))
    w_true = np.array([0.5, -0.2, 0.1])
    y = X @ w_true + 0.05 * rng.normal(size=100)
    df = pd.DataFrame(X, columns=["feature_a", "feature_b", "feature_c"]).assign(target=y)
    model = fit_ml(df, alpha=0.1)
    preds = predict_adjustments(model, df.rename(columns={"feature_a": "feature_a"}))
    rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
    assert rmse < 0.2

