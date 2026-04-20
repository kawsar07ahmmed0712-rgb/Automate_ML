    import pandas as pd

    def build_train_test_shift_signals(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
        cols = sorted(set(train_df.columns) & set(test_df.columns))
        return pd.DataFrame({"column": cols, "train_test_shift_review_flag": [False] * len(cols)})
    
