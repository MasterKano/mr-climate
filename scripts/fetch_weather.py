from pathlib import Path
from datetime import date

import pandas as pd

HISTORY_CSV = Path("data/weather_history.csv")
OUTPUT_CSV = Path("data/weather_new_rows.csv")

VARIABLES = {
    "wind": {
        "cds_variables": ["10m_u_component_of_wind", "10m_v_component_of_wind"],
        "unit": "m/s",
    },
    "rain": {
        "cds_variables": ["total_precipitation"],
        "unit": "mm/d",
    },
    "temp": {
        "cds_variables": ["2m_temperature"],
        "unit": "deg_c",
    },
}

# Bounding box currently matches the ERA5 test area:
# North, West, South, East
AREA = [48, 5, 45, 11]


def get_latest_history_month():
    df = pd.read_csv(HISTORY_CSV)

    grouped = (
        df.groupby(["year", "month"])["variable"]
        .nunique()
        .reset_index(name="variable_count")
    )

    complete = grouped[grouped["variable_count"] == 3].sort_values(["year", "month"])

    if complete.empty:
        raise ValueError("No complete historical months found")

    latest = complete.iloc[-1]
    return int(latest["year"]), int(latest["month"])


def next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def main():
    latest_year, latest_month = get_latest_history_month()
    target_year, target_month = next_month(latest_year, latest_month)

    print(f"Latest complete history month: {latest_year}-{latest_month:02d}")
    print(f"Next target month: {target_year}-{target_month:02d}")
    print("Fetch step not implemented yet. API structure placeholder only.")
    print(f"Target area: {AREA}")
    print(f"Variables: {', '.join(VARIABLES.keys())}")


if __name__ == "__main__":
    main()
