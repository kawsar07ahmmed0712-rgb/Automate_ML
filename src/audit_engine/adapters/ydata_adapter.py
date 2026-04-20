from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_ydata_profile(df, output_path: str | Path | None = None) -> dict[str, Any]:
    """
    Generates ydata-profiling HTML report if package is installed.
    """
    try:
        from ydata_profiling import ProfileReport
    except Exception as exc:
        return {
            "ydata_profile_generated": False,
            "ydata_profile_path": None,
            "ydata_profile_error": f"Import failed: {exc}",
        }

    try:
        profile = ProfileReport(
            df,
            title="Audit Engine Profiling Report",
            explorative=True,
            minimal=False,
            progress_bar=False,
        )

        saved_path = None
        if output_path is not None:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            profile.to_file(output_path)
            saved_path = str(output_path)

        return {
            "ydata_profile_generated": True,
            "ydata_profile_path": saved_path,
            "ydata_profile_error": None,
        }
    except Exception as exc:
        return {
            "ydata_profile_generated": False,
            "ydata_profile_path": None,
            "ydata_profile_error": str(exc),
        }