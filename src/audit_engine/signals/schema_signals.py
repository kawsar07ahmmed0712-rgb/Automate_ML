from __future__ import annotations

import pandas as pd


def build_schema_signals(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame | None = None,
    train_semantic_df: pd.DataFrame | None = None,
    test_semantic_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if test_df is None:
        return pd.DataFrame(
            {
                "column": list(train_df.columns),
                "schema_check_available": [False] * len(train_df.columns),
                "in_train": [True] * len(train_df.columns),
                "in_test": [None] * len(train_df.columns),
                "train_dtype": [str(train_df[c].dtype) for c in train_df.columns],
                "test_dtype": [None] * len(train_df.columns),
                "dtype_mismatch_flag": [False] * len(train_df.columns),
                "semantic_mismatch_flag": [False] * len(train_df.columns),
                "missing_in_test_flag": [False] * len(train_df.columns),
                "missing_in_train_flag": [False] * len(train_df.columns),
                "schema_mismatch_flag": [False] * len(train_df.columns),
            }
        )

    train_semantic_map = {}
    test_semantic_map = {}

    if train_semantic_df is not None and not train_semantic_df.empty:
        train_semantic_map = train_semantic_df.set_index("column").to_dict(orient="index")

    if test_semantic_df is not None and not test_semantic_df.empty:
        test_semantic_map = test_semantic_df.set_index("column").to_dict(orient="index")

    all_cols = sorted(set(train_df.columns) | set(test_df.columns))
    rows = []

    for col in all_cols:
        in_train = col in train_df.columns
        in_test = col in test_df.columns

        train_dtype = str(train_df[col].dtype) if in_train else None
        test_dtype = str(test_df[col].dtype) if in_test else None

        train_semantic = train_semantic_map.get(col, {}).get("semantic_type") if in_train else None
        test_semantic = test_semantic_map.get(col, {}).get("semantic_type") if in_test else None

        missing_in_test_flag = in_train and not in_test
        missing_in_train_flag = in_test and not in_train
        dtype_mismatch_flag = in_train and in_test and (train_dtype != test_dtype)

        semantic_mismatch_flag = (
            in_train
            and in_test
            and train_semantic is not None
            and test_semantic is not None
            and train_semantic != test_semantic
        )

        schema_mismatch_flag = (
            missing_in_test_flag
            or missing_in_train_flag
            or dtype_mismatch_flag
            or semantic_mismatch_flag
        )

        rows.append(
            {
                "column": col,
                "schema_check_available": True,
                "in_train": in_train,
                "in_test": in_test,
                "train_dtype": train_dtype,
                "test_dtype": test_dtype,
                "train_semantic_type": train_semantic,
                "test_semantic_type": test_semantic,
                "dtype_mismatch_flag": dtype_mismatch_flag,
                "semantic_mismatch_flag": semantic_mismatch_flag,
                "missing_in_test_flag": missing_in_test_flag,
                "missing_in_train_flag": missing_in_train_flag,
                "schema_mismatch_flag": schema_mismatch_flag,
            }
        )

    return pd.DataFrame(rows)