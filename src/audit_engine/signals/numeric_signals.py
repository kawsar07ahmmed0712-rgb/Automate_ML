from __future__ import annotations

import pandas as pd

from audit_engine.core.config import AuditThresholds


def _iqr_outlier_pct(series: pd.Series) -> float:
    s = series.dropna()
    if s.empty:
        return 0.0

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return 0.0

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    pct = ((s < lower) | (s > upper)).mean() * 100
    return round(float(pct), 4)


def build_numeric_signals(
    df: pd.DataFrame,
    semantic_df: pd.DataFrame,
    thresholds: AuditThresholds,
) -> pd.DataFrame:
    rows = []
    semantic_map = semantic_df.set_index("column").to_dict(orient="index")

    outlier_high_pct = thresholds.numeric.outlier_high_pct
    skew_moderate = thresholds.numeric.skew_moderate
    skew_severe = thresholds.numeric.skew_severe
    zero_heavy_pct = thresholds.numeric.zero_heavy_pct

    for col in df.columns:
        semantic_type = semantic_map.get(col, {}).get("semantic_type", "unknown")
        s = df[col]

        is_numeric_family = (
            pd.api.types.is_numeric_dtype(s)
            or semantic_type in {"numeric_as_text", "numeric_discrete_as_text"}
        )

        if not is_numeric_family:
            continue

        if not pd.api.types.is_numeric_dtype(s):
            s_num = pd.to_numeric(s.astype(str).str.strip(), errors="coerce")
        else:
            s_num = s

        s_num = s_num.dropna()
        if s_num.empty:
            continue

        skewness = round(float(s_num.skew()), 4) if len(s_num) > 2 else 0.0
        kurtosis = round(float(s_num.kurt()), 4) if len(s_num) > 3 else 0.0
        outlier_pct_iqr = _iqr_outlier_pct(s_num)
        zero_pct = round(float((s_num == 0).mean()) * 100, 4)

        high_outlier_flag = outlier_pct_iqr >= outlier_high_pct
        moderate_skew_flag = abs(skewness) >= skew_moderate
        severe_skew_flag = abs(skewness) >= skew_severe
        zero_heavy_flag = zero_pct >= zero_heavy_pct
        scaling_candidate = s_num.nunique() > 5
        log_transform_candidate = (abs(skewness) >= skew_moderate) and bool((s_num >= 0).all())

        rows.append(
            {
                "column": col,
                "outlier_pct_iqr": outlier_pct_iqr,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "zero_pct": zero_pct,
                "high_outlier_flag": high_outlier_flag,
                "moderate_skew_flag": moderate_skew_flag,
                "severe_skew_flag": severe_skew_flag,
                "zero_heavy_flag": zero_heavy_flag,
                "scaling_candidate": scaling_candidate,
                "log_transform_candidate": log_transform_candidate,
            }
        )

    return pd.DataFrame(rows)