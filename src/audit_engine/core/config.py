    from pathlib import Path
    import yaml
    from pydantic import BaseModel

    class AuditConfig(BaseModel):
        target_col: str | None = None
        date_col: str | None = None
        id_col: str | None = None
        export_csv: bool = True
        export_json: bool = True
        export_html: bool = False

    def load_config(path: str | Path | None = None) -> AuditConfig:
        if path is None:
            return AuditConfig()
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return AuditConfig(**data)
    
