"""
execute.py
Reads data.xlsx and produces a JSON summary to stdout.
Designed for Python 3.11+ and pandas 2.3+.
"""

import json
from pathlib import Path

import pandas as pd


def main():
    # Ensure file exists
    data_path = Path("data.xlsx")
    if not data_path.exists():
        raise FileNotFoundError("data.xlsx not found in repository root")

    # Read the data
    df = pd.read_excel(data_path)

    # Basic validation of expected columns
    expected_cols = {"date", "region", "product", "units", "price"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing expected columns: {missing}")

    # Compute revenue
    df["revenue"] = df["units"] * df["price"]

    # row_count
    row_count = len(df)

    # regions: count of distinct regions
    regions_count = int(df["region"].nunique())

    # top_n_products_by_revenue (n=3)
    n = 3
    top_products = (
        df.groupby("product", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(n)
    )
    top_products_list = [
        {"product": row["product"], "revenue": float(row["revenue"]) if pd.notna(row["revenue"]) else None}
        for _, row in top_products.iterrows()
    ]

    # rolling_7d_revenue_by_region: for each region, last value of 7-day moving average of daily revenue
    df["date"] = pd.to_datetime(df["date"])  # ensure datetime

    daily_rev = (
        df.groupby(["region", "date"], as_index=False)["revenue"]
        .sum()
        .sort_values(["region", "date"])
    )

    rolling_summary = {}

    for region, grp in daily_rev.groupby("region"):
        # Ensure sorted by date
        grp = grp.sort_values("date").set_index("date")["revenue"]

        # Compute rolling 7-day mean. Using time-based rolling window; works with datetime index.
        # This returns a Series indexed by date.
        rolled = grp.rolling("7D").mean()

        # Prefer the last non-NaN value; if none, set None
        if rolled.dropna().empty:
            last_val = None
        else:
            last_val = float(rolled.dropna().iloc[-1])

        rolling_summary[region] = last_val

    result = {
        "row_count": int(row_count),
        "regions": int(regions_count),
        "top_n_products_by_revenue": top_products_list,
        "rolling_7d_revenue_by_region": rolling_summary,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
