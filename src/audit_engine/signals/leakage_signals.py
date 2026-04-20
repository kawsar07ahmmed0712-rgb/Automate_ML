    import pandas as pd

    def build_leakage_signals(df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"column": list(df.columns), "leakage_review_flag": [False] * len(df.columns)})
    
