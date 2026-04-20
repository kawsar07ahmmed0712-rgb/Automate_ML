    def build_summary(master_df, fe_df):
        return {
            "column_count": int(len(master_df)),
            "high_priority_columns": int((fe_df["priority"] == "high").sum()) if "priority" in fe_df.columns else 0,
        }
    
