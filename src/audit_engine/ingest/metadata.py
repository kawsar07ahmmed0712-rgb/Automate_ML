    from pathlib import Path

    def get_file_metadata(file_path: str | Path) -> dict:
        p = Path(file_path)
        stat = p.stat()
        return {
            "file_name": p.name,
            "file_size_bytes": stat.st_size,
            "suffix": p.suffix.lower(),
        }
    
