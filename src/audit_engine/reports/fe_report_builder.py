    import pandas as pd

    def build_fe_report(fe_df: pd.DataFrame) -> pd.DataFrame:
        return fe_df.sort_values(["priority", "column"]).reset_index(drop=True)
    
