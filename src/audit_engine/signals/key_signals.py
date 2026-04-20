    import pandas as pd

    def build_key_signals(profile_df: pd.DataFrame) -> pd.DataFrame:
        out = profile_df[["column", "unique_ratio"]].copy()
        out["possible_primary_key_flag"] = out["unique_ratio"] >= 0.98
        out["possible_reference_key_flag"] = (out["unique_ratio"] > 0.05) & (out["unique_ratio"] < 0.98)
        return out
    
