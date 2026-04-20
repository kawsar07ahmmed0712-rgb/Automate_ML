    from functools import reduce
    import pandas as pd

    def build_master_report(frames: list[pd.DataFrame]) -> pd.DataFrame:
        valid_frames = [df for df in frames if df is not None and not df.empty]
        if not valid_frames:
            return pd.DataFrame()
        return reduce(lambda left, right: left.merge(right, on="column", how="outer"), valid_frames)
    
