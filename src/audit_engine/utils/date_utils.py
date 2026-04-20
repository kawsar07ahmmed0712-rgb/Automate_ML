    def is_date_col(name: str) -> bool:
        lowered = name.lower()
        return "date" in lowered or "time" in lowered
    
