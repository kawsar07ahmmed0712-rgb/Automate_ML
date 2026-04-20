#!/usr/bin/env python3
"""
Project scaffold generator for audit-engine.

Usage:
    python template.py
    python template.py --force

Run this from the ROOT of your GitHub repo (inside the audit-engine folder).
It will create folders/files in the CURRENT directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

PROJECT_NAME = "audit-engine"
PACKAGE_NAME = "audit_engine"


def normalize(text: str) -> str:
    text = text.lstrip("\n")
    if not text.endswith("\n"):
        text += "\n"
    return text


DIRS = [
    "configs",
    "scripts",
    "tests",
    "tests/fixtures",
    "outputs",
    "src",
    "src/audit_engine",
    "src/audit_engine/core",
    "src/audit_engine/ingest",
    "src/audit_engine/profiling",
    "src/audit_engine/signals",
    "src/audit_engine/adapters",
    "src/audit_engine/rules",
    "src/audit_engine/reports",
    "src/audit_engine/pipelines",
    "src/audit_engine/utils",
]

FILES = {
    ".gitignore": """
    __pycache__/
    *.py[cod]
    *.egg-info/
    .pytest_cache/
    .mypy_cache/
    .ruff_cache/
    .venv/
    venv/
    build/
    dist/
    outputs/
    .DS_Store
    """,

    "README.md": """
    # audit-engine

    Column-level data audit engine that generates:
    1. Master Report (100+ signals per column)
    2. Feature Engineering Report (action-oriented recommendations)

    ## Quick start

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux / Mac
    # .venv\\Scripts\\activate  # Windows

    pip install -e .[dev]
    python scripts/run_full_audit.py --help
    ```

    ## Core flow

    file -> ingest -> profiles -> signals -> rules -> reports
    """,

    "requirements.txt": """
    pandas>=2.2
    numpy>=1.26
    pydantic>=2.7
    pyarrow>=16
    charset-normalizer>=3.4
    clevercsv>=0.8
    rapidfuzz>=3.9
    pandera>=0.20
    scipy>=1.13
    scikit-learn>=1.5
    pyyaml>=6.0
    """,

    "setup.py": """
    from setuptools import setup, find_packages
    from pathlib import Path

    BASE_DIR = Path(__file__).parent
    README = (BASE_DIR / "README.md").read_text(encoding="utf-8")

    def read_requirements(path: str) -> list[str]:
        req_path = BASE_DIR / path
        if not req_path.exists():
            return []
        lines = []
        for line in req_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        return lines

    setup(
        name="audit-engine",
        version="0.1.0",
        description="Column-level data audit engine for master reports and feature-engineering reports",
        long_description=README,
        long_description_content_type="text/markdown",
        author="Your Name",
        python_requires=">=3.10",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        include_package_data=True,
        install_requires=read_requirements("requirements.txt"),
        extras_require={
            "profiling": ["ydata-profiling>=4.9"],
            "advanced": ["deepchecks>=0.19", "pyod>=2.0", "ftfy>=6.3", "dateparser>=1.2"],
            "web": ["streamlit>=1.44"],
            "dev": ["pytest>=8.2", "pytest-cov>=5.0", "ruff>=0.6", "mypy>=1.11"],
        },
        entry_points={
            "console_scripts": [
                "audit-engine=audit_engine.cli:main",
            ]
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
    """,

    "pyproject.toml": """
    [build-system]
    requires = ["setuptools>=69", "wheel"]
    build-backend = "setuptools.build_meta"

    [tool.setuptools]
    package-dir = {"" = "src"}

    [tool.setuptools.packages.find]
    where = ["src"]

    [tool.pytest.ini_options]
    testpaths = ["tests"]

    [tool.ruff]
    line-length = 100
    target-version = "py310"

    [tool.mypy]
    python_version = "3.10"
    ignore_missing_imports = true
    """,

    "configs/default.yaml": """
    target_col: null
    date_col: null
    id_col: null

    export_csv: true
    export_json: true
    export_html: false
    """,

    "configs/thresholds.yaml": """
    missing_warn: 0.10
    missing_high: 0.30
    missing_severe: 0.60

    unique_ratio_id_like: 0.98

    numeric_parse_threshold: 0.90
    datetime_parse_threshold: 0.90
    bool_parse_threshold: 0.95

    rare_category_threshold: 0.01
    high_cardinality_threshold: 50

    outlier_iqr_warn_pct: 0.01
    outlier_iqr_high_pct: 0.05

    skew_warn: 1.0
    skew_high: 2.0

    zero_heavy_threshold: 0.80
    corr_high: 0.90
    """,

    "configs/master_report_fields.yaml": """
    identity:
      - column
      - current_dtype
      - suggested_dtype
      - semantic_type
      - semantic_confidence

    missingness:
      - missing_count
      - missing_pct
      - mixed_null_tokens_flag
      - missing_indicator_candidate

    numeric:
      - skewness
      - outlier_pct_iqr
      - zero_pct
      - scaling_candidate
      - log_transform_candidate

    categorical:
      - cardinality
      - rare_label_count
      - dirty_label_flag
      - encoding_hint

    final:
      - severity
      - quality_score
      - final_recommendation
    """,

    "configs/fe_rules.yaml": """
    rules:
      - name: drop_identifier
        when:
          semantic_type: identifier
          unique_ratio_gte: 0.98
        action:
          keep_drop_review: drop
          final_recommendation: drop identifier column from modeling

      - name: median_plus_indicator
        when:
          semantic_type: numeric_continuous
          missing_pct_gte: 0.30
        action:
          missing_action: median_plus_indicator
    """,

    "scripts/run_master_report.py": """
    from audit_engine.pipelines.master_pipeline import run_master_pipeline

    if __name__ == "__main__":
        run_master_pipeline()
    """,

    "scripts/run_fe_report.py": """
    from audit_engine.pipelines.fe_pipeline import run_fe_pipeline

    if __name__ == "__main__":
        run_fe_pipeline()
    """,

    "scripts/run_full_audit.py": """
    from audit_engine.pipelines.full_pipeline import run_full_pipeline

    if __name__ == "__main__":
        run_full_pipeline()
    """,

    "tests/test_ingest.py": """
    from audit_engine.ingest.loader import load_dataframe

    def test_module_import():
        assert callable(load_dataframe)
    """,

    "tests/test_profiles.py": """
    from audit_engine.profiling.column_profile import build_column_profiles

    def test_module_import():
        assert callable(build_column_profiles)
    """,

    "tests/test_signals.py": """
    from audit_engine.signals.semantic_signals import infer_semantic_types

    def test_module_import():
        assert callable(infer_semantic_types)
    """,

    "tests/test_rules.py": """
    from audit_engine.rules.fe_rule_engine import build_fe_actions

    def test_module_import():
        assert callable(build_fe_actions)
    """,

    "tests/test_report_builders.py": """
    from audit_engine.reports.master_report_builder import build_master_report
    from audit_engine.reports.fe_report_builder import build_fe_report

    def test_imports():
        assert callable(build_master_report)
        assert callable(build_fe_report)
    """,

    "src/audit_engine/__init__.py": """
    from audit_engine.pipelines.full_pipeline import run_full_audit
    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.pipelines.fe_pipeline import run_fe_report

    __all__ = ["run_full_audit", "run_master_report", "run_fe_report"]
    __version__ = "0.1.0"
    """,

    "src/audit_engine/cli.py": """
    import argparse
    from audit_engine.pipelines.full_pipeline import run_full_audit
    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.pipelines.fe_pipeline import run_fe_report

    def main():
        parser = argparse.ArgumentParser(prog="audit-engine")
        subparsers = parser.add_subparsers(dest="command", required=True)

        master = subparsers.add_parser("master")
        master.add_argument("file", nargs="?")

        fe = subparsers.add_parser("fe")
        fe.add_argument("file", nargs="?")

        full = subparsers.add_parser("full")
        full.add_argument("file", nargs="?")

        args = parser.parse_args()

        if args.command == "master":
            run_master_report(args.file)
        elif args.command == "fe":
            run_fe_report(args.file)
        elif args.command == "full":
            run_full_audit(args.file)

    if __name__ == "__main__":
        main()
    """,

    "src/audit_engine/core/__init__.py": "",
    "src/audit_engine/ingest/__init__.py": "",
    "src/audit_engine/profiling/__init__.py": "",
    "src/audit_engine/signals/__init__.py": "",
    "src/audit_engine/adapters/__init__.py": "",
    "src/audit_engine/rules/__init__.py": "",
    "src/audit_engine/reports/__init__.py": "",
    "src/audit_engine/pipelines/__init__.py": "",
    "src/audit_engine/utils/__init__.py": "",

    "src/audit_engine/core/config.py": """
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
    """,

    "src/audit_engine/core/enums.py": """
    from enum import Enum

    class Severity(str, Enum):
        low = "low"
        medium = "medium"
        high = "high"

    class SemanticType(str, Enum):
        identifier = "identifier"
        binary_flag = "binary_flag"
        categorical = "categorical"
        numeric_continuous = "numeric_continuous"
        numeric_discrete = "numeric_discrete"
        datetime = "datetime"
        text = "text"
        unknown = "unknown"
    """,

    "src/audit_engine/core/constants.py": """
    DEFAULT_OUTPUT_DIR = "outputs"
    DEFAULT_MASTER_REPORT_NAME = "master_report.csv"
    DEFAULT_FE_REPORT_NAME = "feature_engineering_report.csv"
    """,

    "src/audit_engine/core/exceptions.py": """
    class AuditEngineError(Exception):
        pass
    """,

    "src/audit_engine/core/logger.py": """
    import logging

    def get_logger(name: str) -> logging.Logger:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
        return logging.getLogger(name)
    """,

    "src/audit_engine/core/schemas.py": """
    from pydantic import BaseModel

    class ColumnProfileSchema(BaseModel):
        column: str
        current_dtype: str
        missing_count: int
        missing_pct: float
        unique_count: int
        unique_ratio: float
    """,

    "src/audit_engine/ingest/encoding_detector.py": """
    from pathlib import Path
    from charset_normalizer import from_path

    def detect_encoding(file_path: str | Path) -> str:
        result = from_path(str(file_path)).best()
        return result.encoding if result and result.encoding else "utf-8"
    """,

    "src/audit_engine/ingest/delimiter_detector.py": """
    import clevercsv

    def detect_delimiter(sample_text: str) -> str:
        dialect = clevercsv.Sniffer().sniff(sample_text)
        return getattr(dialect, "delimiter", ",")
    """,

    "src/audit_engine/ingest/loader.py": """
    from pathlib import Path
    import pandas as pd

    from audit_engine.ingest.encoding_detector import detect_encoding

    def load_dataframe(file_path: str | Path) -> pd.DataFrame:
        file_path = Path(file_path)
        encoding = detect_encoding(file_path)
        return pd.read_csv(file_path, encoding=encoding, low_memory=False)
    """,

    "src/audit_engine/ingest/metadata.py": """
    from pathlib import Path

    def get_file_metadata(file_path: str | Path) -> dict:
        p = Path(file_path)
        stat = p.stat()
        return {
            "file_name": p.name,
            "file_size_bytes": stat.st_size,
            "suffix": p.suffix.lower(),
        }
    """,

    "src/audit_engine/profiling/dataset_profile.py": """
    def build_dataset_profile(df):
        return {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
        }
    """,

    "src/audit_engine/profiling/column_profile.py": """
    import pandas as pd

    def build_column_profiles(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        n_rows = len(df) if len(df) else 1

        for col in df.columns:
            s = df[col]
            missing_count = int(s.isna().sum())
            unique_count = int(s.nunique(dropna=True))
            rows.append({
                "column": col,
                "current_dtype": str(s.dtype),
                "missing_count": missing_count,
                "missing_pct": round(missing_count / n_rows * 100, 4),
                "unique_count": unique_count,
                "unique_ratio": round(unique_count / n_rows, 6),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/profiling/parse_profile.py": """
    import pandas as pd

    def build_parse_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for col in df.columns:
            s = df[col].dropna().astype(str).str.strip()
            if len(s) == 0:
                rows.append({"column": col, "numeric_parse_ratio": 0.0, "datetime_parse_ratio": 0.0})
                continue
            num_ratio = pd.to_numeric(s, errors="coerce").notna().mean()
            dt_ratio = pd.to_datetime(s, errors="coerce").notna().mean()
            rows.append({
                "column": col,
                "numeric_parse_ratio": round(float(num_ratio), 4),
                "datetime_parse_ratio": round(float(dt_ratio), 4),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/profiling/string_profile.py": """
    import re
    import pandas as pd

    _special_re = re.compile(r"[^A-Za-z0-9\\s]")

    def build_string_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        obj_cols = df.select_dtypes(include=["object"]).columns
        for col in obj_cols:
            s = df[col].dropna().astype(str)
            if len(s) == 0:
                rows.append({"column": col, "avg_str_len": 0.0, "special_char_ratio": 0.0})
                continue
            avg_len = s.str.len().mean()
            sp_ratio = s.str.contains(_special_re, regex=True).mean()
            rows.append({
                "column": col,
                "avg_str_len": round(float(avg_len), 4),
                "special_char_ratio": round(float(sp_ratio), 4),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/profiling/null_profile.py": """
    import pandas as pd

    def build_null_profile(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for col in df.columns:
            s = df[col]
            rows.append({
                "column": col,
                "missing_count": int(s.isna().sum()),
                "missing_pct": round(float(s.isna().mean() * 100), 4),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/profiling/uniqueness_profile.py": """
    import pandas as pd

    def build_uniqueness_profile(df: pd.DataFrame) -> pd.DataFrame:
        n_rows = len(df) if len(df) else 1
        rows = []
        for col in df.columns:
            uniq = int(df[col].nunique(dropna=True))
            rows.append({
                "column": col,
                "unique_count": uniq,
                "unique_ratio": round(uniq / n_rows, 6),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/profiling/stats_cache.py": """
    from dataclasses import dataclass
    import pandas as pd

    @dataclass
    class StatsCache:
        df: pd.DataFrame
    """,

    "src/audit_engine/signals/dtype_signals.py": """
    import pandas as pd

    def build_dtype_signals(df: pd.DataFrame, parse_profile: pd.DataFrame) -> pd.DataFrame:
        out = parse_profile.copy()
        dtype_map = df.dtypes.astype(str).rename("current_dtype").reset_index().rename(columns={"index": "column"})
        out = out.merge(dtype_map, on="column", how="left")
        out["numeric_like_object_flag"] = (
            (out["current_dtype"] == "object") &
            (out["numeric_parse_ratio"] >= 0.90)
        )
        out["datetime_like_object_flag"] = (
            (out["current_dtype"] == "object") &
            (out["datetime_parse_ratio"] >= 0.90)
        )
        return out[["column", "current_dtype", "numeric_like_object_flag", "datetime_like_object_flag"]]
    """,

    "src/audit_engine/signals/semantic_signals.py": """
    import pandas as pd

    def infer_semantic_types(df: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
        rows = []
        dtype_map = {c: str(df[c].dtype) for c in df.columns}
        prof_map = profiles.set_index("column").to_dict(orient="index")

        for col in df.columns:
            meta = prof_map.get(col, {})
            dtype = dtype_map[col]
            unique_ratio = float(meta.get("unique_ratio", 0))
            missing_pct = float(meta.get("missing_pct", 0))

            if "id" in col.lower() and unique_ratio >= 0.98:
                semantic_type = "identifier"
                confidence = 0.95
            elif dtype.startswith("datetime"):
                semantic_type = "datetime"
                confidence = 0.98
            elif dtype in ("int64", "Int64", "float64", "float32", "int32"):
                semantic_type = "numeric_continuous"
                confidence = 0.75
            elif dtype == "object":
                semantic_type = "categorical"
                confidence = 0.65
            else:
                semantic_type = "unknown"
                confidence = 0.40

            rows.append({
                "column": col,
                "semantic_type": semantic_type,
                "semantic_confidence": confidence,
                "review_needed_flag": missing_pct > 30,
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/signals/key_signals.py": """
    import pandas as pd

    def build_key_signals(profile_df: pd.DataFrame) -> pd.DataFrame:
        out = profile_df[["column", "unique_ratio"]].copy()
        out["possible_primary_key_flag"] = out["unique_ratio"] >= 0.98
        out["possible_reference_key_flag"] = (out["unique_ratio"] > 0.05) & (out["unique_ratio"] < 0.98)
        return out
    """,

    "src/audit_engine/signals/schema_signals.py": """
    import pandas as pd

    def build_schema_signals(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
        all_cols = sorted(set(train_df.columns) | set(test_df.columns))
        rows = []
        for col in all_cols:
            in_train = col in train_df.columns
            in_test = col in test_df.columns
            train_dtype = str(train_df[col].dtype) if in_train else None
            test_dtype = str(test_df[col].dtype) if in_test else None
            rows.append({
                "column": col,
                "in_train": in_train,
                "in_test": in_test,
                "train_dtype": train_dtype,
                "test_dtype": test_dtype,
                "dtype_mismatch_flag": in_train and in_test and (train_dtype != test_dtype),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/signals/missingness_signals.py": """
    import pandas as pd

    def build_missingness_signals(profile_df: pd.DataFrame) -> pd.DataFrame:
        out = profile_df[["column", "missing_count", "missing_pct"]].copy()
        out["high_missingness_flag"] = out["missing_pct"] >= 30
        out["severe_missingness_flag"] = out["missing_pct"] >= 60
        out["missing_indicator_candidate"] = out["missing_pct"].between(5, 60, inclusive="both")
        return out
    """,

    "src/audit_engine/signals/categorical_signals.py": """
    import pandas as pd

    def build_categorical_signals(df: pd.DataFrame, profile_df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        prof_map = profile_df.set_index("column").to_dict(orient="index")
        for col in df.columns:
            if str(df[col].dtype) != "object":
                continue
            unique_count = int(prof_map.get(col, {}).get("unique_count", 0))
            rows.append({
                "column": col,
                "cardinality": unique_count,
                "high_cardinality_flag": unique_count > 50,
                "encoding_hint": "one_hot" if unique_count <= 15 else "review_target_or_frequency",
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/signals/numeric_signals.py": """
    import numpy as np
    import pandas as pd

    def build_numeric_signals(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                outlier_pct = 0.0
            else:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                outlier_pct = float(((s < lower) | (s > upper)).mean() * 100)
            skewness = float(s.skew()) if len(s) > 2 else 0.0
            zero_pct = float((s == 0).mean() * 100)
            rows.append({
                "column": col,
                "outlier_pct_iqr": round(outlier_pct, 4),
                "skewness": round(skewness, 4),
                "zero_pct": round(zero_pct, 4),
                "scaling_candidate": abs(skewness) < 2 and s.nunique() > 5,
                "log_transform_candidate": abs(skewness) >= 1 and (s >= 0).all(),
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/signals/datetime_signals.py": """
    import pandas as pd

    def build_datetime_signals(df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        dt_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
        for col in dt_cols:
            s = df[col]
            rows.append({
                "column": col,
                "min_date": s.min(),
                "max_date": s.max(),
                "datetime_flag": True,
            })
        return pd.DataFrame(rows)
    """,

    "src/audit_engine/signals/string_cleanliness_signals.py": """
    import pandas as pd

    def build_string_cleanliness_signals(string_profile_df: pd.DataFrame) -> pd.DataFrame:
        out = string_profile_df.copy()
        out["special_character_flag"] = out["special_char_ratio"] > 0.10
        out["long_text_flag"] = out["avg_str_len"] > 40
        return out
    """,

    "src/audit_engine/signals/leakage_signals.py": """
    import pandas as pd

    def build_leakage_signals(df: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame({"column": list(df.columns), "leakage_review_flag": [False] * len(df.columns)})
    """,

    "src/audit_engine/signals/train_test_shift_signals.py": """
    import pandas as pd

    def build_train_test_shift_signals(train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
        cols = sorted(set(train_df.columns) & set(test_df.columns))
        return pd.DataFrame({"column": cols, "train_test_shift_review_flag": [False] * len(cols)})
    """,

    "src/audit_engine/signals/quality_score_signals.py": """
    import pandas as pd

    def build_quality_scores(master_df: pd.DataFrame) -> pd.DataFrame:
        out = master_df[["column"]].copy()
        score = pd.Series(100, index=out.index, dtype=float)
        if "missing_pct" in master_df.columns:
            score -= master_df["missing_pct"].fillna(0).clip(0, 100) * 0.2
        if "special_character_flag" in master_df.columns:
            score -= master_df["special_character_flag"].fillna(False).astype(int) * 5
        if "high_cardinality_flag" in master_df.columns:
            score -= master_df["high_cardinality_flag"].fillna(False).astype(int) * 3
        out["quality_score"] = score.clip(lower=0).round(2)
        return out
    """,

    "src/audit_engine/adapters/pandera_adapter.py": """
    def run_pandera_checks(df):
        return {"status": "not_implemented"}
    """,

    "src/audit_engine/adapters/ydata_adapter.py": """
    def generate_ydata_profile(df, output_path=None):
        return {"status": "not_implemented"}
    """,

    "src/audit_engine/adapters/deepchecks_adapter.py": """
    def run_deepchecks(df):
        return {"status": "not_implemented"}
    """,

    "src/audit_engine/adapters/pyod_adapter.py": """
    def run_pyod(df):
        return {"status": "not_implemented"}
    """,

    "src/audit_engine/adapters/rapidfuzz_adapter.py": """
    def detect_dirty_label_clusters(values):
        return []
    """,

    "src/audit_engine/rules/severity_engine.py": """
    import pandas as pd

    def assign_severity(master_df: pd.DataFrame) -> pd.DataFrame:
        out = master_df[["column"]].copy()
        severity = []
        for _, row in master_df.iterrows():
            if row.get("severe_missingness_flag", False):
                severity.append("high")
            elif row.get("high_missingness_flag", False) or row.get("special_character_flag", False):
                severity.append("medium")
            else:
                severity.append("low")
        out["severity"] = severity
        return out
    """,

    "src/audit_engine/rules/master_rule_engine.py": """
    def apply_master_rules(master_df):
        return master_df
    """,

    "src/audit_engine/rules/fe_rule_engine.py": """
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
    """,

    "src/audit_engine/rules/recommendation_engine.py": """
    def build_recommendations(master_df):
        return master_df
    """,

    "src/audit_engine/reports/master_report_builder.py": """
    from functools import reduce
    import pandas as pd

    def build_master_report(frames: list[pd.DataFrame]) -> pd.DataFrame:
        valid_frames = [df for df in frames if df is not None and not df.empty]
        if not valid_frames:
            return pd.DataFrame()
        return reduce(lambda left, right: left.merge(right, on="column", how="outer"), valid_frames)
    """,

    "src/audit_engine/reports/fe_report_builder.py": """
    import pandas as pd

    def build_fe_report(fe_df: pd.DataFrame) -> pd.DataFrame:
        return fe_df.sort_values(["priority", "column"]).reset_index(drop=True)
    """,

    "src/audit_engine/reports/summary_builder.py": """
    def build_summary(master_df, fe_df):
        return {
            "column_count": int(len(master_df)),
            "high_priority_columns": int((fe_df["priority"] == "high").sum()) if "priority" in fe_df.columns else 0,
        }
    """,

    "src/audit_engine/reports/csv_exporter.py": """
    from pathlib import Path

    def export_csv(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    """,

    "src/audit_engine/reports/json_exporter.py": """
    from pathlib import Path

    def export_json(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_json(path, orient="records", indent=2)
    """,

    "src/audit_engine/reports/html_exporter.py": """
    from pathlib import Path

    def export_html(df, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(df.to_html(index=False), encoding="utf-8")
    """,

    "src/audit_engine/pipelines/master_pipeline.py": """
    from pathlib import Path
    import sys

    from audit_engine.ingest.loader import load_dataframe
    from audit_engine.profiling.column_profile import build_column_profiles
    from audit_engine.profiling.parse_profile import build_parse_profile
    from audit_engine.profiling.string_profile import build_string_profile
    from audit_engine.signals.dtype_signals import build_dtype_signals
    from audit_engine.signals.semantic_signals import infer_semantic_types
    from audit_engine.signals.key_signals import build_key_signals
    from audit_engine.signals.missingness_signals import build_missingness_signals
    from audit_engine.signals.categorical_signals import build_categorical_signals
    from audit_engine.signals.numeric_signals import build_numeric_signals
    from audit_engine.signals.datetime_signals import build_datetime_signals
    from audit_engine.signals.string_cleanliness_signals import build_string_cleanliness_signals
    from audit_engine.reports.master_report_builder import build_master_report
    from audit_engine.reports.csv_exporter import export_csv

    def run_master_report(file_path: str | None = None):
        if file_path is None:
            if len(sys.argv) < 2:
                print("Usage: python scripts/run_master_report.py <csv_file>")
                return
            file_path = sys.argv[1]

        df = load_dataframe(file_path)

        profile_df = build_column_profiles(df)
        parse_df = build_parse_profile(df)
        string_df = build_string_profile(df)

        frames = [
            profile_df,
            build_dtype_signals(df, parse_df),
            infer_semantic_types(df, profile_df),
            build_key_signals(profile_df),
            build_missingness_signals(profile_df),
            build_categorical_signals(df, profile_df),
            build_numeric_signals(df),
            build_datetime_signals(df),
            build_string_cleanliness_signals(string_df),
        ]

        master_df = build_master_report(frames)

        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "master_report.csv"
        export_csv(master_df, out_path)

        print(f"Master report saved to: {out_path}")
        return master_df
    """,

    "src/audit_engine/pipelines/fe_pipeline.py": """
    from pathlib import Path
    import sys

    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.rules.fe_rule_engine import build_fe_actions
    from audit_engine.reports.fe_report_builder import build_fe_report
    from audit_engine.reports.csv_exporter import export_csv

    def run_fe_pipeline(file_path: str | None = None):
        if file_path is None:
            if len(sys.argv) < 2:
                print("Usage: python scripts/run_fe_report.py <csv_file>")
                return
            file_path = sys.argv[1]

        master_df = run_master_report(file_path)
        fe_df = build_fe_actions(master_df)
        fe_df = build_fe_report(fe_df)

        out_dir = Path("outputs")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "feature_engineering_report.csv"
        export_csv(fe_df, out_path)

        print(f"Feature engineering report saved to: {out_path}")
        return fe_df

    def run_fe_report(file_path: str | None = None):
        return run_fe_pipeline(file_path)
    """,

    "src/audit_engine/pipelines/full_pipeline.py": """
    from audit_engine.pipelines.master_pipeline import run_master_report
    from audit_engine.pipelines.fe_pipeline import run_fe_pipeline

    def run_full_pipeline(file_path: str | None = None):
        master_df = run_master_report(file_path)
        fe_df = run_fe_pipeline(file_path)
        return {"master_report": master_df, "fe_report": fe_df}

    def run_full_audit(file_path: str | None = None):
        return run_full_pipeline(file_path)
    """,

    "src/audit_engine/utils/dataframe_utils.py": """
    def left_join_on_column(left, right):
        return left.merge(right, on="column", how="left")
    """,

    "src/audit_engine/utils/text_utils.py": """
    def safe_strip(value):
        return value.strip() if isinstance(value, str) else value
    """,

    "src/audit_engine/utils/date_utils.py": """
    def is_date_col(name: str) -> bool:
        lowered = name.lower()
        return "date" in lowered or "time" in lowered
    """,

    "src/audit_engine/utils/numeric_utils.py": """
    def is_zero_heavy(zero_pct: float, threshold: float = 80.0) -> bool:
        return zero_pct >= threshold
    """,

    "src/audit_engine/utils/hashing_utils.py": """
    import hashlib

    def sha256_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    """,
}


def write_file(base: Path, rel_path: str, content: str, force: bool) -> str:
    target = base / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not force:
        return f"SKIP   {rel_path}"

    target.write_text(normalize(content), encoding="utf-8")
    return f"WRITE  {rel_path}"


def main():
    parser = argparse.ArgumentParser(description="Create audit-engine project scaffold in current directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    base = Path.cwd()

    print(f"Scaffolding project in: {base}")
    print("")

    for rel_dir in DIRS:
        dir_path = base / rel_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"DIR    {rel_dir}")

    print("")
    for rel_path, content in FILES.items():
        print(write_file(base, rel_path, content, force=args.force))

    print("")
    print("Done.")
    print("Next steps:")
    print("1) python -m venv .venv")
    print("2) pip install -e .[dev]")
    print("3) python scripts/run_full_audit.py <your_csv_file>")


if __name__ == "__main__":
    main()