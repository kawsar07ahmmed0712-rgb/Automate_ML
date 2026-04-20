    from pathlib import Path
    from charset_normalizer import from_path

    def detect_encoding(file_path: str | Path) -> str:
        result = from_path(str(file_path)).best()
        return result.encoding if result and result.encoding else "utf-8"
    
