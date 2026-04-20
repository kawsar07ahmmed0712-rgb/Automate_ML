    from pydantic import BaseModel

    class ColumnProfileSchema(BaseModel):
        column: str
        current_dtype: str
        missing_count: int
        missing_pct: float
        unique_count: int
        unique_ratio: float
    
