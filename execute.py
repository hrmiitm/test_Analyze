#!/usr/bin/env python3
"""
execute.py

Reads data.csv (converted from the provided data.xlsx) and writes a JSON summary to stdout.
Designed for Python 3.11+ and pandas 2.3.

The script is defensive: it works with arbitrary CSVs and summarizes numeric columns and basic counts.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

import pandas as pd


def summarize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute a simple summary for the dataframe.

    - rows: list of records (converted to native Python types)
    - row_count: number of rows
    - numeric_summary: sum and mean for each numeric column
    - top_values: for non-numeric columns, up to 5 most frequent values
    """
    result: Dict[str, Any] = {}

    # rows
    try:
        rows = df.where(pd.notnull(df), None).to_dict(orient="records")
    except Exception:
        # Fallback: convert via values
        rows = [dict(zip(df.columns.tolist(), row)) for row in df.values]

    result["rows"] = rows
    result["row_count"] = len(df)

    # Numeric summary
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    numeric_summary: Dict[str, Dict[str, Any]] = {}
    for col in numeric:
        series = pd.to_numeric(df[col], errors="coerce")
        total = series.sum(skipna=True)
        mean = series.mean(skipna=True)
        numeric_summary[col] = {"sum": None if pd.isna(total) else float(total), "mean": None if pd.isna(mean) else float(mean)}

    result["numeric_summary"] = numeric_summary

    # Top values for non-numeric columns
    non_numeric = df.select_dtypes(exclude=["number"]).columns.tolist()
    top_values: Dict[str, Any] = {}
    for col in non_numeric:
        try:
            counts = df[col].value_counts(dropna=False).head(5)
            top_values[col] = [{"value": (None if (pd.isna(v) and v != v) else v), "count": int(c)} for v, c in counts.items()]
        except Exception:
            top_values[col] = []

    result["top_values"] = top_values

    return result


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:]) if argv is None else argv

    input_path = "data.csv"

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found. Make sure data.csv is present.", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error reading {input_path}: {exc}", file=sys.stderr)
        return 3

    summary = summarize_dataframe(df)

    # Write JSON to stdout
    json.dump(summary, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
