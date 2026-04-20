    import pandas as pd

    def build_categorical_signals(df: pd.DataFrame, profile_df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        prof_map = profile_df.set_index("column").to_dict(orient="index")
        for col in df.columns:
            if str(df[col].dtype) != "object":
                continue
            unique_count = int(prof_map.get(col, {}).get("unique_count", 0))
            rows.append({
                "column": col,
                "cardinality": unique_count,
                "high_cardinality_flag": unique_count > 50,
                "encoding_hint": "one_hot" if unique_count <= 15 else "review_target_or_frequency",
            })
        return pd.DataFrame(rows)
    
