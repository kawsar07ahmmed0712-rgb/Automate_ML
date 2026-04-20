    import re
    import pandas as pd

    _special_re = re.compile(r"[^A-Za-z0-9\s]")

    def build_string_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        obj_cols = df.select_dtypes(include=["object"]).columns
        for col in obj_cols:
            s = df[col].dropna().astype(str)
            if len(s) == 0:
                rows.append({"column": col, "avg_str_len": 0.0, "special_char_ratio": 0.0})
                continue
            avg_len = s.str.len().mean()
            sp_ratio = s.str.contains(_special_re, regex=True).mean()
            rows.append({
                "column": col,
                "avg_str_len": round(float(avg_len), 4),
                "special_char_ratio": round(float(sp_ratio), 4),
            })
        return pd.DataFrame(rows)
    
