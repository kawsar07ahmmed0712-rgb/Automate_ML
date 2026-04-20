    import clevercsv

    def detect_delimiter(sample_text: str) -> str:
        dialect = clevercsv.Sniffer().sniff(sample_text)
        return getattr(dialect, "delimiter", ",")
    
