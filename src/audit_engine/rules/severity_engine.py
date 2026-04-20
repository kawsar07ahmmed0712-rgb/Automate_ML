    import pandas as pd

    def assign_severity(master_df: pd.DataFrame) -> pd.DataFrame:
        out = master_df[["column"]].copy()
        severity = []
        for _, row in master_df.iterrows():
            if row.get("severe_missingness_flag", False):
                severity.append("high")
            elif row.get("high_missingness_flag", False) or row.get("special_character_flag", False):
                severity.append("medium")
            else:
                severity.append("low")
        out["severity"] = severity
        return out
    
