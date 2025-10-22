"""
Simple script to read data.csv and emit a JSON summary to stdout.
Designed to run with Python 3.11+ and pandas 2.3.
"""

from __future__ import annotations

import json
import sys

import pandas as pd


def compute_summary(df: pd.DataFrame) -> dict:
    """Return a summary dictionary computed from dataframe.

    The returned object will be JSON-serializable and contain two keys:
    - rows: list of row dicts
    - by_product: total Revenue per Product
    """
    # Ensure Revenue is numeric (coerce non-numeric to NaN -> treat as 0)
    if "Revenue" in df.columns:
        # strip common characters then convert
        df["Revenue"] = (
            df["Revenue"].astype(str).str.replace(",", "", regex=False).str.replace("$", "", regex=False)
        )
        df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0.0)
    else:
        df["Revenue"] = 0.0

    rows = df.to_dict(orient="records")

    by_product = []
    if "Product" in df.columns:
        gb = df.groupby("Product", as_index=False)["Revenue"].sum()
        by_product = gb.to_dict(orient="records")

    return {"rows": rows, "by_product": by_product}


def main() -> int:
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        print(json.dumps({"error": "data.csv not found in repository"}, indent=2))
        return 1
    except Exception as exc:  # pragma: no cover - surface errors
        print(json.dumps({"error": f"Failed to read data.csv: {exc}"}, indent=2))
        return 1

    result = compute_summary(df)
    # Emit to stdout as JSON
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
