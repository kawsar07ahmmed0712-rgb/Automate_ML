    import pandas as pd

    def build_string_cleanliness_signals(string_profile_df: pd.DataFrame) -> pd.DataFrame:
        out = string_profile_df.copy()
        out["special_character_flag"] = out["special_char_ratio"] > 0.10
        out["long_text_flag"] = out["avg_str_len"] > 40
        return out
    
