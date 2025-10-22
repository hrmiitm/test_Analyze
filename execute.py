#!/usr/bin/env python3
"""
execute.py
Reads data.csv, computes a small summary and prints JSON to stdout.
Compatible with Python 3.11+ and pandas 2.3.

NOTE: This script intentionally does not write result.json to disk; CI captures stdout
and redirects it to result.json (python execute.py > result.json).
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict

import pandas as pd


def safe_read_csv(path: str) -> pd.DataFrame:
    # Read CSV robustly; try common encodings if needed
    try:
        return pd.read_csv(path)
    except Exception:
        # Try with utf-8-sig and latin1 fallback
        try:
            return pd.read_csv(path, encoding='utf-8-sig')
        except Exception:
            return pd.read_csv(path, encoding='latin1')


def summarize_df(df: pd.DataFrame) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    out['row_count'] = int(len(df))
    out['columns'] = list(df.columns)

    # For numeric columns compute count, sum, mean, min, max
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    stats = {}
    for col in numeric:
        series = df[col].dropna()
        stats[col] = {
            'count': int(series.count()),
            'sum': float(series.sum()) if not series.empty else 0.0,
            'mean': float(series.mean()) if not series.empty else None,
            'min': float(series.min()) if not series.empty else None,
            'max': float(series.max()) if not series.empty else None,
        }
    out['numeric_summary'] = stats

    # If there is a 'name' or 'category' column, include value counts for first string column
    string_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if string_cols:
        first = string_cols[0]
        out['top_values_for_{}'.format(first)] = (
            df[first].value_counts(dropna=True).head(10).to_dict()
        )

    # Provide first 20 rows as records (helpful for quick inspection)
    out['preview'] = df.head(20).to_dict(orient='records')
    return out


def main(argv: list[str]) -> int:
    csv_path = 'data.csv'

    try:
        df = safe_read_csv(csv_path)
    except FileNotFoundError:
        print(json.dumps({"error": f"File not found: {csv_path}"}))
        return 1
    except Exception as exc:
        print(json.dumps({"error": f"Failed to read {csv_path}: {exc}"}))
        return 2

    summary = summarize_df(df)

    # Dump to stdout
    json.dump(summary, sys.stdout, indent=2, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
