    from pathlib import Path

    def export_json(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_json(path, orient="records", indent=2)
    
