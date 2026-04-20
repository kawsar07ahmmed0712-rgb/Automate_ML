    from pathlib import Path
    import pandas as pd

    from audit_engine.ingest.encoding_detector import detect_encoding

    def load_dataframe(file_path: str | Path) -> pd.DataFrame:
        file_path = Path(file_path)
        encoding = detect_encoding(file_path)
        return pd.read_csv(file_path, encoding=encoding, low_memory=False)
    
