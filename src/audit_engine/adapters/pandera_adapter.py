from __future__ import annotations

from typing import Any

import pandas as pd
import pandera.pandas as pa
from pandera import Check


def _build_generic_schema(df: pd.DataFrame) -> pa.DataFrameSchema:
    """
    Very generic schema from current dataframe dtypes.
    This is not a business schema; this is a baseline validation schema.
    """
    columns = {}

    for col in df.columns:
        dtype = df[col].dtype

        try:
            columns[col] = pa.Column(dtype, nullable=True)
        except Exception:
            columns[col] = pa.Column(object, nullable=True)

    return pa.DataFrameSchema(columns=columns, coerce=False, strict=False)


def run_pandera_checks(df: pd.DataFrame) -> dict[str, Any]:
    """
    Returns a lightweight validation summary.
    """
    schema = _build_generic_schema(df)

    try:
        schema.validate(df, lazy=True)
        return {
            "pandera_validation_passed": True,
            "pandera_error_count": 0,
            "pandera_errors": [],
        }
    except pa.errors.SchemaErrors as exc:
        failure_cases = exc.failure_cases.copy()

        if not failure_cases.empty:
            failure_cases = failure_cases.fillna("NA")
            error_rows = failure_cases[["column", "check", "failure_case"]].head(50).to_dict(orient="records")
        else:
            error_rows = []

        return {
            "pandera_validation_passed": False,
            "pandera_error_count": int(len(failure_cases)),
            "pandera_errors": error_rows,
        }
    except Exception as exc:
        return {
            "pandera_validation_passed": False,
            "pandera_error_count": 1,
            "pandera_errors": [{"error": str(exc)}],
        }