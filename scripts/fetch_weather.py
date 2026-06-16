from pathlib import Path
import argparse
import calendar

import cdsapi
import pandas as pd

HISTORY_CSV = Path("data/weather_history.csv")
RAW_DIR = Path("data/raw")
OUTPUT_CSV = Path("data/weather_new_rows.csv")

DATASET = "reanalysis-era5-single-levels"

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

# North, West, South, East
AREA = [71, 4, 55, 32]


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


def build_request(year, month):
    _, days_in_month = calendar.monthrange(year, month)

    cds_variables = sorted(
        {
            variable_name
            for config in VARIABLES.values()
            for variable_name in config["cds_variables"]
        }
    )

    return {
        "product_type": ["reanalysis"],
        "variable": cds_variables,
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": [f"{day:02d}" for day in range(1, days_in_month + 1)],
        "time": [f"{hour:02d}:00" for hour in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Actually call the Copernicus API")
    parser.add_argument("--year", type=int, default=None, help="Target year. Defaults to next month after history.")
    parser.add_argument("--month", type=int, default=None, help="Target month. Defaults to next month after history.")
    args = parser.parse_args()

    latest_year, latest_month = get_latest_history_month()

    if args.year is None and args.month is None:
        target_year, target_month = next_month(latest_year, latest_month)
    elif args.year is not None and args.month is not None:
        target_year, target_month = args.year, args.month
    else:
        raise ValueError("Provide both --year and --month, or neither.")

    request = build_request(target_year, target_month)
    output_path = RAW_DIR / f"era5_{target_year}_{target_month:02d}.nc"

    print(f"Latest complete history month: {latest_year}-{latest_month:02d}")
    print(f"Next target month: {target_year}-{target_month:02d}")
    print(f"Dataset: {DATASET}")
    print(f"Output: {output_path}")
    print("Request:")
    for key, value in request.items():
        if key in {"day", "time"}:
            print(f"  {key}: {value[0]} ... {value[-1]} ({len(value)} items)")
        else:
            print(f"  {key}: {value}")

    if not args.download:
        print("Dry run only. Add --download to call Copernicus.")
        return

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client()
    client.retrieve(DATASET, request, str(output_path))

    print(f"Downloaded: {output_path}")
    print(f"Size bytes: {output_path.stat().st_size}")


if __name__ == "__main__":
    main()
