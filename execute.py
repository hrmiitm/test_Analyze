"""Process sales data and output summary JSON.
Reads data.csv from the repository root.
Compatible with Python 3.11+ and pandas 2.3.
"""
import json
import pandas as pd


def main():
    # Read the CSV (converted from the provided Excel file)
    df = pd.read_csv("data.csv", parse_dates=["date"])  # expects a column named 'date'

    # Compute revenue
    df["revenue"] = df["units"] * df["price"]

    # row_count
    row_count = len(df)

    # regions: count of distinct regions
    regions_count = int(df["region"].nunique())

    # top_n_products_by_revenue (n=3)
    n = 3
    top_products = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    top_products_list = [
        {"product": row["product"], "revenue": float(row["revenue"]) }
        for _, row in top_products.iterrows()
    ]

    # rolling_7d_revenue_by_region: for each region, compute daily revenue and then
    # calculate 7-day time-based rolling mean and keep the latest value per region.
    df = df.sort_values(["region", "date"])  # ensure sorted
    daily_rev = (
        df.groupby(["region", "date"])["revenue"]
        .sum()
        .reset_index()
        .sort_values(["region", "date"])  # ensure sorted for rolling
    )

    # Compute 7-day rolling mean of revenue per region.
    # We'll group by region, set date as index and apply a time-based rolling window.
    rolling_series = (
        daily_rev.groupby("region")
        .apply(lambda g: g.set_index("date")["revenue"].rolling("7D").mean())
        .reset_index(level=0, drop=True)
    )

    # Align rolling results back into daily_rev
    daily_rev["rolling_7d_revenue"] = rolling_series.values

    # Take the last available rolling value per region
    last_rolling = daily_rev.sort_values(["region", "date"]).groupby("region").tail(1)

    rolling_summary = {}
    for _, row in last_rolling.iterrows():
        val = row["rolling_7d_revenue"]
        # JSON cannot represent NaN; use None for missing
        if pd.isna(val):
            rolling_summary[row["region"]] = None
        else:
            rolling_summary[row["region"]] = float(val)

    result = {
        "row_count": int(row_count),
        "regions": int(regions_count),
        "top_n_products_by_revenue": top_products_list,
        "rolling_7d_revenue_by_region": rolling_summary,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
