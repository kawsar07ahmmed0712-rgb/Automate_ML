    import pandas as pd

    def build_dtype_signals(df: pd.DataFrame, parse_profile: pd.DataFrame) -> pd.DataFrame:
        out = parse_profile.copy()
        dtype_map = df.dtypes.astype(str).rename("current_dtype").reset_index().rename(columns={"index": "column"})
        out = out.merge(dtype_map, on="column", how="left")
        out["numeric_like_object_flag"] = (
            (out["current_dtype"] == "object") &
            (out["numeric_parse_ratio"] >= 0.90)
        )
        out["datetime_like_object_flag"] = (
            (out["current_dtype"] == "object") &
            (out["datetime_parse_ratio"] >= 0.90)
        )
        return out[["column", "current_dtype", "numeric_like_object_flag", "datetime_like_object_flag"]]
    
