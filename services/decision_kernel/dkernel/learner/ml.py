from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass
class RidgeModel:
    w: np.ndarray
    b: float


def _prepare_xy(feedback_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    # Expect columns: feature_* and target
    feat_cols = [c for c in feedback_df.columns if c.startswith("feature_")]
    X = feedback_df[feat_cols].to_numpy(dtype=float)
    y = feedback_df["target"].to_numpy(dtype=float)
    return X, y


def fit_ml(feedback_df: pd.DataFrame, alpha: float = 1.0) -> RidgeModel:
    X, y = _prepare_xy(feedback_df)
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    I = np.eye(d)
    w = np.linalg.solve(X.T @ X + alpha * I, X.T @ y)
    b = float(y.mean() - X.mean(axis=0) @ w)
    return RidgeModel(w=w, b=b)


def predict_adjustments(model: RidgeModel, current_df: pd.DataFrame) -> np.ndarray:
    feat_cols = [c for c in current_df.columns if c.startswith("feature_")]
    X = current_df[feat_cols].to_numpy(dtype=float)
    return X @ model.w + model.b

