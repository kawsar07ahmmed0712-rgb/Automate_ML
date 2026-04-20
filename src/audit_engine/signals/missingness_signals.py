    import pandas as pd

    def build_missingness_signals(profile_df: pd.DataFrame) -> pd.DataFrame:
        out = profile_df[["column", "missing_count", "missing_pct"]].copy()
        out["high_missingness_flag"] = out["missing_pct"] >= 30
        out["severe_missingness_flag"] = out["missing_pct"] >= 60
        out["missing_indicator_candidate"] = out["missing_pct"].between(5, 60, inclusive="both")
        return out
    
