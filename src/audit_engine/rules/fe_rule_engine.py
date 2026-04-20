from __future__ import annotations

import pandas as pd


def build_fe_report(master_df: pd.DataFrame, target_col: str | None = None) -> pd.DataFrame:
    rows = []

    for _, row in master_df.iterrows():
        semantic_type = row.get("semantic_type", "unknown")
        unique_ratio = float(row.get("unique_ratio", 0) or 0)
        missing_pct = float(row.get("missing_pct", 0) or 0)

        high_outlier_flag = bool(row.get("high_outlier_flag", False))
        scaling_candidate = bool(row.get("scaling_candidate", False))
        log_transform_candidate = bool(row.get("log_transform_candidate", False))
        high_cardinality_flag = bool(row.get("high_cardinality_flag", False))
        rare_label_burden_flag = bool(row.get("rare_label_burden_flag", False))
        primary_key_flag = bool(row.get("possible_primary_key_flag", False))
        id_like_flag = bool(row.get("id_like_flag", False))
        special_character_flag = bool(row.get("special_character_flag", False))
        case_inconsistency_flag = bool(row.get("case_inconsistency_flag", False))
        missing_indicator_candidate = bool(row.get("missing_indicator_candidate", False))
        encoding_hint = row.get("encoding_hint", "not_applicable")
        datetime_feature_candidate = bool(row.get("datetime_feature_candidate", False))
        schema_mismatch_flag = bool(row.get("schema_mismatch_flag", False))
        dirty_label_cluster_flag = bool(row.get("dirty_label_cluster_flag", False))

        keep_drop_review = "keep"
        missing_action = "none"
        outlier_action = "not_applicable"
        encoding_needed = "not_applicable"
        scaling_needed = False
        transform_needed = "none"
        text_cleaning_needed = False
        category_cleaning_needed = False
        priority = "low"
        final_recommendation = "manual review"

        col_name = str(row["column"]).lower()

        if target_col and row["column"] == target_col:
            keep_drop_review = "keep"
            priority = "high"
            final_recommendation = "target column - do not treat as feature unless explicitly intended"

        elif semantic_type == "target":
            keep_drop_review = "keep"
            priority = "high"
            final_recommendation = "target column - do not treat as feature unless explicitly intended"

        elif semantic_type == "identifier" or (id_like_flag and unique_ratio >= 0.98) or primary_key_flag:
            keep_drop_review = "drop"
            priority = "high"
            final_recommendation = "drop identifier-like column from modeling"

        elif semantic_type == "categorical":
            category_cleaning_needed = dirty_label_cluster_flag or case_inconsistency_flag or special_character_flag

            if missing_pct > 0:
                missing_action = "mode_or_missing_label"

            encoding_needed = encoding_hint

            if high_cardinality_flag:
                priority = "high"
                final_recommendation = "clean labels, review rare labels, then use frequency/target-style encoding"
            elif rare_label_burden_flag:
                priority = "medium"
                final_recommendation = "group rare labels, then encode"
            else:
                priority = "low"
                final_recommendation = "clean categorical labels and encode"

            if category_cleaning_needed and priority == "low":
                priority = "medium"

        elif semantic_type in {"numeric_continuous", "numeric_as_text"}:
            if missing_pct >= 30:
                missing_action = "median_plus_indicator" if missing_indicator_candidate else "median"
                priority = "high"
            elif missing_pct > 0:
                missing_action = "median"

            if high_outlier_flag:
                outlier_action = "review_or_winsorize"
                priority = "medium" if priority == "low" else priority

            if scaling_candidate:
                scaling_needed = True

            if log_transform_candidate:
                transform_needed = "log1p_candidate"

            final_recommendation = "review missingness, outliers, transformation, and scaling"

        elif semantic_type in {"numeric_discrete", "numeric_discrete_as_text"}:
            if missing_pct > 0:
                missing_action = "median_or_mode_review"
            final_recommendation = "review whether discrete numeric should stay numeric or be treated categorically"

        elif semantic_type == "binary_flag":
            if missing_pct > 0:
                missing_action = "mode_or_explicit_missing_category"
            encoding_needed = "binary_map"
            final_recommendation = "ensure binary consistency before modeling"

        elif semantic_type == "datetime":
            if datetime_feature_candidate:
                priority = "medium"
                final_recommendation = "extract year/month/day/age/recency features later"
            else:
                final_recommendation = "review datetime column manually"

        elif semantic_type == "text":
            text_cleaning_needed = True
            priority = "medium"
            final_recommendation = "text cleaning / NLP-specific handling needed"

        if special_character_flag or case_inconsistency_flag:
            text_cleaning_needed = True
            if priority == "low":
                priority = "medium"

        if schema_mismatch_flag:
            priority = "high"
            final_recommendation = "schema mismatch detected between train and test; resolve before modeling"

        if "target" in col_name and not target_col:
            final_recommendation = "possible target-like column - review manually"

        rows.append(
            {
                "column": row["column"],
                "semantic_type": semantic_type,
                "keep_drop_review": keep_drop_review,
                "missing_action": missing_action,
                "outlier_action": outlier_action,
                "encoding_needed": encoding_needed,
                "scaling_needed": scaling_needed,
                "transform_needed": transform_needed,
                "text_cleaning_needed": text_cleaning_needed,
                "category_cleaning_needed": category_cleaning_needed,
                "priority": priority,
                "final_recommendation": final_recommendation,
            }
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    out = pd.DataFrame(rows)
    out["priority_order"] = out["priority"].map(priority_order)
    out = out.sort_values(["priority_order", "column"]).drop(columns="priority_order").reset_index(drop=True)
    return out