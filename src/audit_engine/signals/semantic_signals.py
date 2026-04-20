from __future__ import annotations

import pandas as pd


def infer_semantic_types(df: pd.DataFrame, profile_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    profile_map = profile_df.set_index("column").to_dict(orient="index")

    for col in df.columns:
        meta = profile_map[col]

        dtype = str(meta["current_dtype"])
        unique_ratio = float(meta["unique_ratio"])
        unique_count = int(meta["unique_count"])
        avg_str_len = float(meta["avg_str_len"])
        numeric_parse_ratio = float(meta["numeric_parse_ratio"])
        datetime_parse_ratio = float(meta["datetime_parse_ratio"])
        bool_token_ratio = float(meta["bool_token_ratio"])

        col_lower = col.lower()

        semantic_type = "unknown"
        confidence = 0.40

        # 1) identifier
        if ("id" in col_lower or col_lower.endswith("_key") or col_lower.startswith("key_")) and unique_ratio >= 0.98:
            semantic_type = "identifier"
            confidence = 0.95

        # 2) datetime
        elif dtype.startswith("datetime") or datetime_parse_ratio >= 0.95:
            semantic_type = "datetime"
            confidence = 0.95

        # 3) binary flag
        elif unique_count == 2:
            semantic_type = "binary_flag"
            confidence = 0.90

        elif "flag" in col_lower and unique_count <= 5:
            semantic_type = "binary_flag"
            confidence = 0.80

        elif dtype == "object" and bool_token_ratio >= 0.95 and unique_count <= 2:
            semantic_type = "binary_flag"
            confidence = 0.92

        # 4) numeric types
        elif pd.api.types.is_numeric_dtype(df[col]):
            if unique_count <= 15 and unique_ratio < 0.05:
                semantic_type = "numeric_discrete"
                confidence = 0.80
            else:
                semantic_type = "numeric_continuous"
                confidence = 0.82

        # 5) object but numeric-like
        elif dtype == "object" and numeric_parse_ratio >= 0.95:
            if unique_count <= 15 and unique_ratio < 0.05:
                semantic_type = "numeric_discrete_as_text"
                confidence = 0.82
            else:
                semantic_type = "numeric_as_text"
                confidence = 0.84

        # 6) categorical vs text
        elif dtype == "object":
            if unique_count <= 20 and avg_str_len <= 25:
                semantic_type = "categorical"
                confidence = 0.80
            elif unique_ratio <= 0.20 and avg_str_len <= 30:
                semantic_type = "categorical"
                confidence = 0.72
            else:
                semantic_type = "text"
                confidence = 0.70

        rows.append(
            {
                "column": col,
                "semantic_type": semantic_type,
                "semantic_confidence": round(confidence, 4),
                "semantic_review_flag": confidence < 0.75,
            }
        )

    return pd.DataFrame(rows)