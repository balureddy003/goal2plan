from __future__ import annotations

from typing import Sequence

import pandas as pd
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime


class SalesRow(BaseModel):
    date: datetime
    sku: str
    qty: float = Field(ge=0)
    price: float = Field(ge=0)


class InventoryRow(BaseModel):
    sku: str
    on_hand: float = Field(ge=0)
    safety_stock: float = Field(ge=0)


class OfferRow(BaseModel):
    supplier: str
    sku: str
    price: float = Field(ge=0)
    moq: float = Field(ge=0)
    lead_time_days: int = Field(ge=0)
    validity_to: datetime


def _validate_frame(df: pd.DataFrame, model: type[BaseModel], required_cols: Sequence[str]) -> pd.DataFrame:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    # Normalize dtypes
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "validity_to" in df.columns:
        df["validity_to"] = pd.to_datetime(df["validity_to"], errors="coerce")
    # Drop rows with NA in required
    df = df.dropna(subset=list(required_cols)).copy()
    # Row-level validation to catch negatives, etc.
    for idx, row in df.iterrows():
        try:
            model(**row.to_dict())
        except ValidationError as e:
            raise ValueError(f"Row {idx} invalid: {e}")
    return df.reset_index(drop=True)


def load_sales_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _validate_frame(df, SalesRow, ["date", "sku", "qty", "price"])
    # Normalize types
    df["sku"] = df["sku"].astype(str)
    df["qty"] = df["qty"].astype(float)
    df["price"] = df["price"].astype(float)
    return df


def load_inventory_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _validate_frame(df, InventoryRow, ["sku", "on_hand", "safety_stock"])
    df["sku"] = df["sku"].astype(str)
    df["on_hand"] = df["on_hand"].astype(float)
    df["safety_stock"] = df["safety_stock"].astype(float)
    return df


def load_offers_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = _validate_frame(
        df,
        OfferRow,
        ["supplier", "sku", "price", "moq", "lead_time_days", "validity_to"],
    )
    df["supplier"] = df["supplier"].astype(str)
    df["sku"] = df["sku"].astype(str)
    df["price"] = df["price"].astype(float)
    df["moq"] = df["moq"].astype(float)
    df["lead_time_days"] = df["lead_time_days"].astype(int)
    return df
