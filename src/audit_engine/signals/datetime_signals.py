from __future__ import annotations

import pandas as pd


DATE_HINT_TOKENS = {"date", "time", "timestamp", "dt", "year", "month", "day"}


def _is_date_name(col_name: str) -> bool:
    lowered = col_name.lower()
    return any(token in lowered for token in DATE_HINT_TOKENS)


def _to_datetime_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce")
    return pd.to_datetime(series.astype(str).str.strip(), errors="coerce")


def build_datetime_signals(
    df: pd.DataFrame,
    profile_df: pd.DataFrame,
    semantic_df: pd.DataFrame,
    date_col: str | None = None,
) -> pd.DataFrame:
    rows = []

    profile_map = profile_df.set_index("column").to_dict(orient="index")
    semantic_map = semantic_df.set_index("column").to_dict(orient="index")

    for col in df.columns:
        semantic_type = semantic_map.get(col, {}).get("semantic_type", "unknown")
        current_dtype = str(profile_map.get(col, {}).get("current_dtype", ""))
        datetime_parse_ratio = float(profile_map.get(col, {}).get("datetime_parse_ratio", 0))

        is_candidate = (
            col == date_col
            or semantic_type == "datetime"
            or pd.api.types.is_datetime64_any_dtype(df[col])
            or (current_dtype == "object" and datetime_parse_ratio >= 0.95 and _is_date_name(col))
            or _is_date_name(col) and current_dtype.startswith("datetime")
        )

        if not is_candidate:
            continue

        dt = _to_datetime_series(df[col])
        parse_success_ratio = float(dt.notna().mean()) if len(dt) else 0.0

        if dt.notna().sum() == 0:
            rows.append(
                {
                    "column": col,
                    "datetime_flag": False,
                    "date_parse_success_ratio": round(parse_success_ratio, 4),
                    "min_date": None,
                    "max_date": None,
                    "year_span": 0,
                    "future_date_flag": False,
                    "all_same_date_flag": False,
                    "date_monotonic_increasing_flag": False,
                    "datetime_feature_candidate": False,
                }
            )
            continue

        dt_non_null = dt.dropna().sort_values()
        min_date = dt_non_null.min()
        max_date = dt_non_null.max()

        current_ts = pd.Timestamp.now()
        future_date_flag = bool((dt_non_null > current_ts).any())
        all_same_date_flag = bool(dt_non_null.nunique() == 1)
        monotonic_flag = bool(dt_non_null.is_monotonic_increasing)

        try:
            year_span = int(max_date.year - min_date.year)
        except Exception:
            year_span = 0

        datetime_feature_candidate = True

        rows.append(
            {
                "column": col,
                "datetime_flag": True,
                "date_parse_success_ratio": round(parse_success_ratio, 4),
                "min_date": min_date,
                "max_date": max_date,
                "year_span": year_span,
                "future_date_flag": future_date_flag,
                "all_same_date_flag": all_same_date_flag,
                "date_monotonic_increasing_flag": monotonic_flag,
                "datetime_feature_candidate": datetime_feature_candidate,
            }
        )

    return pd.DataFrame(rows)