    import pandas as pd

    def build_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        n_rows = len(df) if len(df) else 1

        for col in df.columns:
            s = df[col]
            missing_count = int(s.isna().sum())
            unique_count = int(s.nunique(dropna=True))
            rows.append({
                "column": col,
                "current_dtype": str(s.dtype),
                "missing_count": missing_count,
                "missing_pct": round(missing_count / n_rows * 100, 4),
                "unique_count": unique_count,
                "unique_ratio": round(unique_count / n_rows, 6),
            })
        return pd.DataFrame(rows)
    
