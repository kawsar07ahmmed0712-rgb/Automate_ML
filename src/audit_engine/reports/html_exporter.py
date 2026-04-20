    from pathlib import Path

    def export_html(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(df.to_html(index=False), encoding="utf-8")
    
