    import pandas as pd

    def build_fe_actions(master_df: pd.DataFrame) -> pd.DataFrame:
        rows = []

        for _, row in master_df.iterrows():
            semantic_type = row.get("semantic_type", "unknown")
            unique_ratio = float(row.get("unique_ratio", 0) or 0)
            missing_pct = float(row.get("missing_pct", 0) or 0)
            high_cardinality = bool(row.get("high_cardinality_flag", False))
            log_candidate = bool(row.get("log_transform_candidate", False))
            scaling_candidate = bool(row.get("scaling_candidate", False))

            keep_drop_review = "keep"
            missing_action = "none"
            outlier_action = "review"
            encoding_needed = "not_applicable"
            scaling_needed = False
            transform_needed = "none"
            priority = "low"
            final_recommendation = "no major action"

            if semantic_type == "identifier" and unique_ratio >= 0.98:
                keep_drop_review = "drop"
                final_recommendation = "drop identifier column from modeling"
                priority = "high"

            elif semantic_type == "categorical":
                encoding_needed = "one_hot" if not high_cardinality else "review_target_or_frequency"
                final_recommendation = "clean labels and encode categorical feature"
                priority = "medium" if high_cardinality else "low"

            elif semantic_type == "numeric_continuous":
                if missing_pct >= 30:
                    missing_action = "median_plus_indicator"
                    priority = "high"
                elif missing_pct > 0:
                    missing_action = "median"

                if scaling_candidate:
                    scaling_needed = True
                if log_candidate:
                    transform_needed = "log1p_candidate"

                final_recommendation = "review missingness, outliers, scaling, and transformation"

            rows.append({
                "column": row["column"],
                "semantic_type": semantic_type,
                "keep_drop_review": keep_drop_review,
                "missing_action": missing_action,
                "outlier_action": outlier_action,
                "encoding_needed": encoding_needed,
                "scaling_needed": scaling_needed,
                "transform_needed": transform_needed,
                "priority": priority,
                "final_recommendation": final_recommendation,
            })

        return pd.DataFrame(rows)
    
