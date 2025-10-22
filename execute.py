#!/usr/bin/env python3
"""
execute.py

Reads data.csv and produces a small JSON summary to stdout.
Designed to run on Python 3.11+ with pandas 2.3.x.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

import pandas as pd


def summarize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Create a JSON-serializable summary for the dataframe."""
    result: Dict[str, Any] = {}

    # Basic info
    result["row_count"] = int(len(df))
    result["columns"] = list(df.columns.astype(str))

    # Preview (first 10 rows)
    preview = df.head(10).to_dict(orient="records")
    # Ensure all values are JSON serializable (convert numpy types)
    def _to_python(o):
        try:
            if pd.isna(o):
                return None
        except Exception:
            pass
        if hasattr(o, "item"):
            try:
                return o.item()
            except Exception:
                pass
        return o

    preview_cleaned = [ {k: _to_python(v) for k, v in row.items()} for row in preview ]
    result["preview"] = preview_cleaned

    # Numeric summaries
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_summary: Dict[str, Dict[str, Any]] = {}
    for col in numeric:
        s = df[col].dropna()
        if len(s) == 0:
            numeric_summary[col] = {"count": 0}
            continue
        numeric_summary[col] = {
            "count": int(s.count()),
            "sum": float(s.sum()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "min": float(s.min()),
            "max": float(s.max()),
        }
    result["numeric_summary"] = numeric_summary

    # If there is a 'product' column, give totals per product as an example
    if "product" in df.columns and "revenue" in df.columns:
        try:
            grp = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
            result["total_revenue_by_product"] = {str(k): float(v) for k, v in grp.items()}
        except Exception:
            # don't fail just because grouping didn't work
            result["total_revenue_by_product"] = {}

    return result


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    input_path = "data.csv"

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(json.dumps({"error": f"{input_path} not found"}, indent=2))
        return 1
    except Exception as e:  # pragma: no cover - helpful message for unexpected parse errors
        print(json.dumps({"error": str(e)}))
        return 2

    summary = summarize_dataframe(df)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
