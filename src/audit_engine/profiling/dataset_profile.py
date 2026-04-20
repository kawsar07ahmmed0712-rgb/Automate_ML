    def build_dataset_profile(df):
        return {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
        }
    
