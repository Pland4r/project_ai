import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Accepted date formats (covers messy real-world inputs)
DATE_FORMATS = [
    "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
    "%Y-%m-%d", "%d-%b-%Y", "%b-%d-%Y",
    "%d-%m-%y", "%y-%m-%d",
]

DIRTY_TOKENS = {"", "nan", "na", "none", "n/a", "?", "-", "###", "ok", "fail", "error", "check", "??"}
MAX_USERS = 1_000_000


def _clean_date_value(val: object) -> Optional[pd.Timestamp]:
    # Follow user's script semantics: try explicit formats first, then fall back
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s in {"", "NaN"}:
        return np.nan
    for fmt in DATE_FORMATS:
        try:
            return pd.Timestamp(datetime.strptime(s, fmt))
        except ValueError:
            continue
    return np.nan


def _clean_numeric_value(val: object) -> Optional[float]:
    # Follow user's script semantics exactly
    if pd.isna(val):
        return np.nan
    if val in ['?', 'N/A', 'NaN', 'none', '']:
        return np.nan
    s = str(val)
    s = s.replace(',', '')
    try:
        num = float(s)
        return num if num >= 0 else np.nan
    except Exception:
        return np.nan


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Drop noise columns if present
    df = df.drop(columns=["debug_info", "extra_col", "??note"], errors="ignore")

    # Dates
    if "date" in df.columns:
        df["date"] = df["date"].apply(_clean_date_value)
        df = df[~df["date"].isna()].sort_values("date")
        df["date"] = df["date"].ffill().bfill()

    # Numerics (user's script behavior)
    numeric_cols = ["total_users", "churned_users", "new_users", "active_users"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(_clean_numeric_value)

    # Cap unreasonably large values (> 1e6) to NaN as per script
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: np.nan if (pd.notna(x) and x > 1_000_000) else x)

    # Drop unnecessary columns
    df = df.drop(columns=["debug_info", "extra_col", "??note"], errors="ignore")

    # For backend analysis, replace remaining NaN numerics with 0 to keep pipeline running
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).clip(lower=0)

    # Derive active/churn using identities (prefer total - churn over provided active)
    if {"total_users", "active_users", "churned_users"}.issubset(df.columns):
        total = df["total_users"]
        active = df["active_users"]
        churn = df["churned_users"]

        # Always prefer active = total - churn when churn is present (incoming active is unreliable)
        has_churn = ~churn.isna()
        active = (total - churn.fillna(0)).where(has_churn, active)

        # If churn missing but active present, derive churn = total - active
        churn = churn.where(has_churn, (total - pd.to_numeric(active, errors="coerce")).fillna(0))

        active = active.fillna(0).clip(0)
        churn = churn.fillna(0).clip(0)
        over = (active + churn) - total
        mask_over = over > 0
        if mask_over.any():
            reduce_amt = over[mask_over]
            churn_adj = (churn[mask_over] - reduce_amt).clip(lower=0)
            remaining_over = (active[mask_over] + churn_adj) - total[mask_over]
            active_adj = (active[mask_over] - remaining_over.clip(lower=0)).clip(lower=0)
            churn.loc[mask_over] = churn_adj
            active.loc[mask_over] = active_adj

        df["active_users"] = active
        df["churned_users"] = churn

    # Rebuild new_users from diffs if missing or inconsistent
    if "total_users" in df.columns:
        diffs = df["total_users"].diff().fillna(0).clip(lower=0)
        if "new_users" not in df.columns:
            df["new_users"] = diffs
        else:
            provided = df["new_users"].fillna(0)
            inconsistent = (provided > (diffs * 3)) & (diffs > 0)
            df.loc[inconsistent, "new_users"] = diffs[inconsistent]

    for col in ["total_users", "active_users", "churned_users", "new_users"]:
        if col in df.columns:
            df[col] = df[col].round().astype(int)

    return df


def analyze_aggregate(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "metrics": {
                "total_users": 0,
                "active_users": 0,
                "churned_users": 0,
                "conversion_rate": 0.0,
                "avg_session_duration": 0.0,
                "avg_sessions_per_user": 0.0,
                "cohort_analysis": {},
            },
            "visualizationData": {"chartData": [], "pieData": []},
        }

    # Use last valid snapshot with total_users > 0
    mask_valid = df["total_users"] > 0
    last_idx = df.index[mask_valid][-1] if mask_valid.any() else df.index[-1]
    snap = df.loc[last_idx]

    total_users = int(max(snap.get("total_users", 0), 0))
    # Prefer deriving active from total - churn when churn exists
    churn_val = float(pd.to_numeric(snap.get("churned_users", 0), errors="coerce") or 0)
    provided_active = float(pd.to_numeric(snap.get("active_users", 0), errors="coerce") or 0)
    derived_active = max(total_users - max(churn_val, 0), 0)
    active_users = int(min(max(derived_active if churn_val > 0 else provided_active, 0), total_users))
    churned_users = int(min(max(churn_val, 0), total_users))

    conversion_rate = float(active_users / total_users) if total_users else 0.0
    conversion_rate = max(0.0, min(conversion_rate, 1.0))

    # Time-series by DAY using totals directly so the chart reflects real counts
    by_day = df.copy()
    by_day["day"] = pd.to_datetime(by_day["date"], errors="coerce").dt.to_period("D")
    # For cohort_analysis (still useful), compute new user inflow per day if available, otherwise diffs
    if "new_users" in by_day.columns:
        inflow_series = by_day.groupby("day")["new_users"].sum()
    else:
        inflow_series = by_day.groupby("day")["total_users"].apply(lambda s: s.diff().clip(lower=0).fillna(0).sum())
    cohort_analysis = {str(k): int(v) for k, v in inflow_series.to_dict().items()}

    # Chart data: actual totals per day
    totals_series = by_day.groupby("day")["total_users"].last()
    actives_series = by_day.groupby("day")["active_users"].last() if "active_users" in by_day.columns else totals_series * conversion_rate
    churn_series = by_day.groupby("day")["churned_users"].last() if "churned_users" in by_day.columns else totals_series - actives_series

    chartData = []
    for day in totals_series.index:
        users_count = int(max(totals_series.loc[day], 0))
        active_count = int(min(max(actives_series.loc[day], 0), users_count))
        churn_count = int(min(max(churn_series.loc[day], 0), users_count))
        chartData.append({"period": str(day), "users": users_count, "active": active_count, "churn": churn_count})

    pie_total = max(total_users, 1)
    pieData = [
        {"name": "Active Users", "value": round((active_users / pie_total) * 100, 2)},
        {"name": "Inactive", "value": round(((total_users - active_users) / pie_total) * 100, 2)},
    ]

    # Build daily series for richer metrics
    totals_series = by_day.groupby("day")["total_users"].last()
    actives_series = by_day.groupby("day")["active_users"].last() if "active_users" in by_day.columns else totals_series * conversion_rate
    churn_series = by_day.groupby("day")["churned_users"].last() if "churned_users" in by_day.columns else totals_series - actives_series

    metrics = {
        # Latest snapshot (what you had before)
        "total_users": total_users,
        "active_users": active_users,
        "churned_users": churned_users,
        "conversion_rate": conversion_rate,
        "avg_session_duration": 0.0,
        "avg_sessions_per_user": 0.0,
        # Day-aware rollups
        "total_new_users": int(inflow_series.sum()) if 'inflow_series' in locals() else 0,
        "avg_active_users": float(actives_series.mean()) if len(actives_series) else 0.0,
        "peak_active_users": int(actives_series.max()) if len(actives_series) else 0,
        "avg_total_users": float(totals_series.mean()) if len(totals_series) else 0.0,
        "peak_total_users": int(totals_series.max()) if len(totals_series) else 0,
        "avg_churned_users": float(churn_series.mean()) if len(churn_series) else 0.0,
        "peak_churned_users": int(churn_series.max()) if len(churn_series) else 0,
        "cohort_analysis": cohort_analysis,
    }
    return {"metrics": metrics, "visualizationData": {"chartData": chartData, "pieData": pieData}}


