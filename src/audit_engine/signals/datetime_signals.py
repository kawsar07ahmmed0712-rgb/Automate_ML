    import pandas as pd

    def build_datetime_signals(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        dt_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
        for col in dt_cols:
            s = df[col]
            rows.append({
                "column": col,
                "min_date": s.min(),
                "max_date": s.max(),
                "datetime_flag": True,
            })
        return pd.DataFrame(rows)
    
