    import pandas as pd

    def build_schema_signals(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
        all_cols = sorted(set(train_df.columns) | set(test_df.columns))
        rows = []
        for col in all_cols:
            in_train = col in train_df.columns
            in_test = col in test_df.columns
            train_dtype = str(train_df[col].dtype) if in_train else None
            test_dtype = str(test_df[col].dtype) if in_test else None
            rows.append({
                "column": col,
                "in_train": in_train,
                "in_test": in_test,
                "train_dtype": train_dtype,
                "test_dtype": test_dtype,
                "dtype_mismatch_flag": in_train and in_test and (train_dtype != test_dtype),
            })
        return pd.DataFrame(rows)
    
