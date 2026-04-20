from __future__ import annotations

import re
from typing import Any

import pandas as pd


SPECIAL_CHAR_RE = re.compile(r"[^A-Za-z0-9\s]")


def _safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def _string_stats(series: pd.Series) -> dict[str, Any]:
    s = series.dropna().astype(str).str.strip()

    if s.empty:
        return {
            "avg_str_len": 0.0,
            "max_str_len": 0,
            "min_str_len": 0,
            "whitespace_ratio": 0.0,
            "special_char_ratio": 0.0,
            "empty_string_ratio": 0.0,
        }

    original = series.dropna().astype(str)
    stripped = original.str.strip()

    whitespace_ratio = (original != stripped).mean()
    empty_ratio = (stripped == "").mean()
    special_ratio = stripped.str.contains(SPECIAL_CHAR_RE, regex=True).mean()

    return {
        "avg_str_len": round(float(stripped.str.len().mean()), 4),
        "max_str_len": int(stripped.str.len().max()),
        "min_str_len": int(stripped.str.len().min()),
        "whitespace_ratio": round(float(whitespace_ratio), 4),
        "special_char_ratio": round(float(special_ratio), 4),
        "empty_string_ratio": round(float(empty_ratio), 4),
    }


def _parse_ratios(series: pd.Series) -> dict[str, float]:
    s = series.dropna().astype(str).str.strip()
    s = s[s != ""]

    if s.empty:
        return {
            "numeric_parse_ratio": 0.0,
            "datetime_parse_ratio": 0.0,
        }

    numeric_ratio = pd.to_numeric(s, errors="coerce").notna().mean()
    datetime_ratio = pd.to_datetime(s, errors="coerce").notna().mean()

    return {
        "numeric_parse_ratio": round(float(numeric_ratio), 4),
        "datetime_parse_ratio": round(float(datetime_ratio), 4),
    }


def _bool_token_ratio(series: pd.Series) -> float:
    tokens = {
        "true", "false",
        "yes", "no",
        "1", "0",
    }
    s = series.dropna().astype(str).str.strip().str.lower()
    s = s[s != ""]

    if s.empty:
        return 0.0

    return round(float(s.isin(tokens).mean()), 4)


def build_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_rows = len(df) if len(df) else 1

    for col in df.columns:
        s = df[col]

        missing_count = int(s.isna().sum())
        non_null_count = int(s.notna().sum())
        unique_count = int(s.nunique(dropna=True))
        unique_ratio = _safe_div(unique_count, n_rows)

        top_values = s.value_counts(dropna=False).head(5).to_dict()
        top_value = None
        dominant_ratio = 0.0

        if len(s) > 0:
            vc = s.value_counts(dropna=False, normalize=True)
            if not vc.empty:
                top_value = str(vc.index[0])
                dominant_ratio = float(vc.iloc[0])

        parse_stats = _parse_ratios(s)
        str_stats = _string_stats(s)
        bool_ratio = _bool_token_ratio(s)

        rows.append(
            {
                "column": col,
                "row_count": int(n_rows),
                "current_dtype": str(s.dtype),
                "missing_count": missing_count,
                "missing_pct": round(_safe_div(missing_count, n_rows) * 100, 4),
                "non_null_count": non_null_count,
                "unique_count": unique_count,
                "unique_ratio": round(unique_ratio, 6),
                "dominant_value": top_value,
                "dominant_value_ratio": round(dominant_ratio, 4),
                "zero_ratio": round(float((s == 0).mean()) * 100, 4) if pd.api.types.is_numeric_dtype(s) else 0.0,
                "sample_values": str(list(s.dropna().astype(str).head(5).values)),
                "top_values": str(top_values),
                "bool_token_ratio": bool_ratio,
                **parse_stats,
                **str_stats,
            }
        )

    return pd.DataFrame(rows)