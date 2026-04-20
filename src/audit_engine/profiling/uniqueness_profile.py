    import pandas as pd

    def build_uniqueness_profile(df: pd.DataFrame) -> pd.DataFrame:
        n_rows = len(df) if len(df) else 1
        rows = []
        for col in df.columns:
            uniq = int(df[col].nunique(dropna=True))
            rows.append({
                "column": col,
                "unique_count": uniq,
                "unique_ratio": round(uniq / n_rows, 6),
            })
        return pd.DataFrame(rows)
    
