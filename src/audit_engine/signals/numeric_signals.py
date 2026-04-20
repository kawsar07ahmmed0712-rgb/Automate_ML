    import numpy as np
    import pandas as pd

    def build_numeric_signals(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                outlier_pct = 0.0
            else:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_pct = float(((s < lower) | (s > upper)).mean() * 100)
            skewness = float(s.skew()) if len(s) > 2 else 0.0
            zero_pct = float((s == 0).mean() * 100)
            rows.append({
                "column": col,
                "outlier_pct_iqr": round(outlier_pct, 4),
                "skewness": round(skewness, 4),
                "zero_pct": round(zero_pct, 4),
                "scaling_candidate": abs(skewness) < 2 and s.nunique() > 5,
                "log_transform_candidate": abs(skewness) >= 1 and (s >= 0).all(),
            })
        return pd.DataFrame(rows)
    
