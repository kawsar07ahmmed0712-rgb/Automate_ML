from __future__ import annotations

import re

import pandas as pd


ID_PATTERNS = [
    re.compile(r"(^id$)|(^id_)|(_id$)"),
    re.compile(r"(^key$)|(^key_)|(_key$)"),
    re.compile(r"(^sk_id)"),
    re.compile(r"(^pk_)|(_pk$)"),
    re.compile(r"(^fk_)|(_fk$)"),
    re.compile(r"(^code$)|(^code_)|(_code$)"),
]


def _looks_identifier_name(column_name: str) -> bool:
    lowered = column_name.lower()
    return any(pattern.search(lowered) for pattern in ID_PATTERNS)


def build_key_signals(profile_df: pd.DataFrame, semantic_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    profile_map = profile_df.set_index("column").to_dict(orient="index")
    semantic_map = semantic_df.set_index("column").to_dict(orient="index")

    for col in profile_df["column"]:
        meta = profile_map[col]
        semantic_type = semantic_map.get(col, {}).get("semantic_type", "unknown")

        unique_ratio = float(meta.get("unique_ratio", 0))
        missing_pct = float(meta.get("missing_pct", 0))
        unique_count = int(meta.get("unique_count", 0))
        row_count = int(meta.get("row_count", 1))
        dominant_ratio = float(meta.get("dominant_value_ratio", 0))

        name_hint = _looks_identifier_name(col)

        possible_primary_key_flag = (
            unique_ratio >= 0.98
            and missing_pct == 0
            and unique_count >= max(2, row_count - 1)
        )

        possible_reference_key_flag = (
            name_hint
            and 0.05 <= unique_ratio < 0.98
            and dominant_ratio < 0.90
        )

        id_like_flag = name_hint or semantic_type == "identifier"

        rows.append(
            {
                "column": col,
                "id_like_flag": id_like_flag,
                "possible_primary_key_flag": possible_primary_key_flag,
                "possible_reference_key_flag": possible_reference_key_flag,
                "key_review_flag": id_like_flag or possible_primary_key_flag or possible_reference_key_flag,
            }
        )

    return pd.DataFrame(rows)