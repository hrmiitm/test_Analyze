#!/usr/bin/env python3
"""
execute.py

Reads data.csv (or data.xlsx if CSV not present), computes a small summary
and prints JSON to stdout. Intended to be run as:

  python execute.py > result.json

Requirements: Python 3.11+, pandas 2.3.x
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


def main() -> int:
    # Prefer CSV (converted from data.xlsx for this repository), but fall back to Excel
    csv_path = Path("data.csv")
    xlsx_path = Path("data.xlsx")

    if csv_path.exists():
        df = pd.read_csv(csv_path)
    elif xlsx_path.exists():
        df = pd.read_excel(xlsx_path)
    else:
        print("ERROR: data.csv or data.xlsx not found", file=sys.stderr)
        return 2

    # Basic validation
    if df.empty:
        payload = {"rows": 0, "columns": [], "summary": {}, "head": []}
        print(json.dumps(payload, indent=2))
        return 0

    # Prepare metadata
    meta = {
        "rows": int(len(df)),
        "columns": list(map(str, df.columns)),
    }

    # Head (first 10 rows) as records, ensure not to include non-serializable types
    try:
        head_records = df.head(10).replace({pd.NA: None}).to_dict(orient="records")
    except Exception:
        # fallback: convert via astype(str)
        head_records = df.head(10).astype(str).to_dict(orient="records")

    # Summary for numeric and categorical columns
    summary = {
        "numeric": {},
        "categorical": {},
    }

    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        ser = df[col].dropna()
        summary["numeric"][str(col)] = {
            "count": int(ser.count()),
            "sum": float(ser.sum()) if not ser.empty else 0.0,
            "mean": float(ser.mean()) if not ser.empty else 0.0,
            "min": float(ser.min()) if not ser.empty else None,
            "max": float(ser.max()) if not ser.empty else None,
        }

    # For object/ categorical columns provide top value counts
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in cat_cols:
        top = df[col].value_counts(dropna=True).head(5)
        summary["categorical"][str(col)] = [{"value": v, "count": int(c)} for v, c in top.items()]

    payload = {**meta, "summary": summary, "head": head_records}

    # Emit JSON to stdout
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
