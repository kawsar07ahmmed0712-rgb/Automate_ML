    import pandas as pd

    def infer_semantic_types(df: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
        rows = []
        dtype_map = {c: str(df[c].dtype) for c in df.columns}
        prof_map = profiles.set_index("column").to_dict(orient="index")

        for col in df.columns:
            meta = prof_map.get(col, {})
            dtype = dtype_map[col]
            unique_ratio = float(meta.get("unique_ratio", 0))
            missing_pct = float(meta.get("missing_pct", 0))

            if "id" in col.lower() and unique_ratio >= 0.98:
                semantic_type = "identifier"
                confidence = 0.95
            elif dtype.startswith("datetime"):
                semantic_type = "datetime"
                confidence = 0.98
            elif dtype in ("int64", "Int64", "float64", "float32", "int32"):
                semantic_type = "numeric_continuous"
                confidence = 0.75
            elif dtype == "object":
                semantic_type = "categorical"
                confidence = 0.65
            else:
                semantic_type = "unknown"
                confidence = 0.40

            rows.append({
                "column": col,
                "semantic_type": semantic_type,
                "semantic_confidence": confidence,
                "review_needed_flag": missing_pct > 30,
            })
        return pd.DataFrame(rows)
    
