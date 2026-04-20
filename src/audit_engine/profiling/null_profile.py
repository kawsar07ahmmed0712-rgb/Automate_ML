    import pandas as pd

    def build_null_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for col in df.columns:
            s = df[col]
            rows.append({
                "column": col,
                "missing_count": int(s.isna().sum()),
                "missing_pct": round(float(s.isna().mean() * 100), 4),
            })
        return pd.DataFrame(rows)
    
