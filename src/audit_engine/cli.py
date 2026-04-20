from __future__ import annotations

import argparse

from audit_engine.pipelines.full_pipeline import run_full_pipeline


def main():
    parser = argparse.ArgumentParser(prog="audit-engine")

    parser.add_argument("file", help="Path to train/input CSV file")
    parser.add_argument("--test-file", default=None, help="Optional test CSV file for schema comparison")
    parser.add_argument("--target", default=None, help="Target column name")
    parser.add_argument("--date", default=None, help="Date column name")
    parser.add_argument("--id-col", default=None, help="ID column name")
    parser.add_argument("--outdir", default="outputs", help="Output directory")
    parser.add_argument("--thresholds", default="configs/thresholds.yaml", help="Threshold config YAML path")

    args = parser.parse_args()

    run_full_pipeline(
        file_path=args.file,
        test_file_path=args.test_file,
        target_col=args.target,
        date_col=args.date,
        id_col=args.id_col,
        out_dir=args.outdir,
        thresholds_path=args.thresholds,
    )


if __name__ == "__main__":
    main()