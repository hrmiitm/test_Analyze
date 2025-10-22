#!/usr/bin/env python3
"""
Reads data.csv (expected in the same directory), computes simple aggregations,
and writes a JSON object to stdout. Compatible with Python 3.11+ and pandas 2.3.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


def main() -> int:
    data_path = Path(__file__).with_name("data.csv")
    if not data_path.exists():
        print(f"Error: {data_path} not found", file=sys.stderr)
        return 2

    # Read CSV using pandas
    df = pd.read_csv(data_path)

    # Basic validation
    if df.empty:
        result = {"summary": {"rows": 0}, "rows": []}
        json.dump(result, sys.stdout, indent=2)
        return 0

    # Ensure numeric column 'amount' exists and is numeric
    if 'amount' in df.columns:
        # coerce errors to NaN then fill 0
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    else:
        df['amount'] = 0.0

    total_amount = float(df['amount'].sum())

    # Example aggregation by category if present
    if 'category' in df.columns:
        agg = df.groupby('category', dropna=False)['amount'].sum().reset_index()
        categories = [
            {"category": row['category'] if pd.notna(row['category']) else None, "amount": float(row['amount'])}
            for _, row in agg.iterrows()
        ]
    else:
        categories = []

    rows = []
    for _, row in df.iterrows():
        # Convert each row to serializable values
        obj = {}
        for col in df.columns:
            val = row[col]
            # Convert numpy types to native python types
            if pd.isna(val):
                obj[col] = None
            elif hasattr(val, 'item'):
                try:
                    obj[col] = val.item()
                except Exception:
                    obj[col] = str(val)
            else:
                obj[col] = val
        rows.append(obj)

    result = {
        "summary": {
            "rows": len(rows),
            "total_amount": total_amount,
        },
        "categories": categories,
        "rows": rows,
    }

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
