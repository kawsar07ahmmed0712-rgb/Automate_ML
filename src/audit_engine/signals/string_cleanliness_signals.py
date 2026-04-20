from __future__ import annotations

import pandas as pd


def _clean_string_series(series: pd.Series) -> pd.Series:
    s = series.dropna().astype(str)
    if s.empty:
        return s
    return s


def build_string_cleanliness_signals(
    df: pd.DataFrame,
    profile_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    profile_map = profile_df.set_index("column").to_dict(orient="index")

    for col in df.columns:
        dtype = str(profile_map.get(col, {}).get("current_dtype", ""))

        if dtype != "object":
            continue

        s = _clean_string_series(df[col])
        if s.empty:
            rows.append(
                {
                    "column": col,
                    "whitespace_issue_flag": False,
                    "empty_string_issue_flag": False,
                    "special_character_flag": False,
                    "case_inconsistency_flag": False,
                    "possible_format_inconsistency_flag": False,
                }
            )
            continue

        stripped = s.str.strip()
        non_empty = stripped[stripped != ""]

        whitespace_ratio = float(profile_map.get(col, {}).get("whitespace_ratio", 0))
        empty_string_ratio = float(profile_map.get(col, {}).get("empty_string_ratio", 0))
        special_char_ratio = float(profile_map.get(col, {}).get("special_char_ratio", 0))

        whitespace_issue_flag = whitespace_ratio > 0.0
        empty_string_issue_flag = empty_string_ratio > 0.0
        special_character_flag = special_char_ratio > 0.10

        case_inconsistency_flag = False
        possible_format_inconsistency_flag = False

        if not non_empty.empty and non_empty.nunique() > 1:
            raw_unique = non_empty.nunique()
            lower_unique = non_empty.str.lower().nunique()
            upper_unique = non_empty.str.upper().nunique()

            # safer than old logic: only flag when normalization actually collapses categories
            case_inconsistency_flag = (
                lower_unique < raw_unique or upper_unique < raw_unique
            ) and raw_unique > 2

            alpha_ratio = non_empty.str.contains(r"[A-Za-z]", regex=True).mean()
            digit_ratio = non_empty.str.contains(r"\d", regex=True).mean()

            # mixed letters + digits often means possible code/format inconsistency
            possible_format_inconsistency_flag = (
                0.20 <= alpha_ratio <= 0.95
                and 0.20 <= digit_ratio <= 0.95
                and raw_unique > 2
            )

        rows.append(
            {
                "column": col,
                "whitespace_issue_flag": whitespace_issue_flag,
                "empty_string_issue_flag": empty_string_issue_flag,
                "special_character_flag": special_character_flag,
                "case_inconsistency_flag": case_inconsistency_flag,
                "possible_format_inconsistency_flag": possible_format_inconsistency_flag,
            }
        )

    return pd.DataFrame(rows)