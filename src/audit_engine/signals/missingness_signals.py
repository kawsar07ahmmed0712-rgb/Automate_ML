from __future__ import annotations

import pandas as pd

from audit_engine.core.config import AuditThresholds


MISSING_TOKENS = {
    "", "na", "n/a", "null", "none", "nan", "missing", "unknown", "?"
}


def build_missingness_signals(
    df: pd.DataFrame,
    profile_df: pd.DataFrame,
    thresholds: AuditThresholds,
) -> pd.DataFrame:
    rows = []

    profile_map = profile_df.set_index("column").to_dict(orient="index")

    low_thr = thresholds.missing.low
    high_thr = thresholds.missing.high
    severe_thr = thresholds.missing.severe
    extreme_drop_thr = thresholds.missing.extreme_drop
    indicator_min = thresholds.missing.indicator_min
    indicator_max = thresholds.missing.indicator_max

    for col in df.columns:
        meta = profile_map[col]
        s = df[col]

        missing_count = int(meta["missing_count"])
        missing_pct = float(meta["missing_pct"])
        dtype = str(meta["current_dtype"])

        mixed_null_tokens_flag = False
        missing_token_count = 0

        if dtype == "object":
            cleaned = s.dropna().astype(str).str.strip().str.lower()
            cleaned = cleaned[cleaned != ""]
            if not cleaned.empty:
                token_mask = cleaned.isin(MISSING_TOKENS)
                missing_token_count = int(token_mask.sum())
                mixed_null_tokens_flag = missing_token_count > 0

        if missing_pct == 0:
            severity = "none"
        elif missing_pct < low_thr:
            severity = "low"
        elif missing_pct < high_thr:
            severity = "medium"
        elif missing_pct < severe_thr:
            severity = "high"
        else:
            severity = "severe"

        high_missingness_flag = missing_pct >= high_thr
        severe_missingness_flag = missing_pct >= severe_thr
        missing_indicator_candidate = indicator_min <= missing_pct <= indicator_max
        drop_candidate_extreme_missing = missing_pct >= extreme_drop_thr

        rows.append(
            {
                "column": col,
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "missing_severity": severity,
                "high_missingness_flag": high_missingness_flag,
                "severe_missingness_flag": severe_missingness_flag,
                "mixed_null_tokens_flag": mixed_null_tokens_flag,
                "missing_token_count": missing_token_count,
                "missing_indicator_candidate": missing_indicator_candidate,
                "drop_candidate_extreme_missing": drop_candidate_extreme_missing,
            }
        )

    return pd.DataFrame(rows)