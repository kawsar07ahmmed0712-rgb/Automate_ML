    from pathlib import Path

    def export_csv(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    
