    import pandas as pd

    def build_quality_scores(master_df: pd.DataFrame) -> pd.DataFrame:
        out = master_df[["column"]].copy()
        score = pd.Series(100, index=out.index, dtype=float)
        if "missing_pct" in master_df.columns:
            score -= master_df["missing_pct"].fillna(0).clip(0, 100) * 0.2
        if "special_character_flag" in master_df.columns:
            score -= master_df["special_character_flag"].fillna(False).astype(int) * 5
        if "high_cardinality_flag" in master_df.columns:
            score -= master_df["high_cardinality_flag"].fillna(False).astype(int) * 3
        out["quality_score"] = score.clip(lower=0).round(2)
        return out
    
