    from dataclasses import dataclass
    import pandas as pd

    @dataclass
    class StatsCache:
        df: pd.DataFrame
    
