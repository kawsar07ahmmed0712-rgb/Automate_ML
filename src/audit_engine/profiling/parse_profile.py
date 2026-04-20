    import pandas as pd

    def build_parse_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for col in df.columns:
            s = df[col].dropna().astype(str).str.strip()
            if len(s) == 0:
                rows.append({"column": col, "numeric_parse_ratio": 0.0, "datetime_parse_ratio": 0.0})
                continue
            num_ratio = pd.to_numeric(s, errors="coerce").notna().mean()
            dt_ratio = pd.to_datetime(s, errors="coerce").notna().mean()
            rows.append({
                "column": col,
                "numeric_parse_ratio": round(float(num_ratio), 4),
                "datetime_parse_ratio": round(float(dt_ratio), 4),
            })
        return pd.DataFrame(rows)
    
