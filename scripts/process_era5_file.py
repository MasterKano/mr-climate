from pathlib import Path
import argparse

import numpy as np
import pandas as pd
import xarray as xr

RAW_DIR = Path("data/raw")
OUTPUT_CSV = Path("data/weather_new_rows.csv")


def find_var(ds, candidates):
    for candidate in candidates:
        if candidate in ds.data_vars:
            return candidate
    raise KeyError(f"None of these variables found: {candidates}. Available: {list(ds.data_vars)}")


def spatial_temporal_mean(data_array):
    dims = list(data_array.dims)
    return float(data_array.mean(dim=dims, skipna=True).values)


def process_file(path, year, month):
    ds = xr.open_dataset(path)

    u_name = find_var(ds, ["u10", "10m_u_component_of_wind"])
    v_name = find_var(ds, ["v10", "10m_v_component_of_wind"])
    t_name = find_var(ds, ["t2m", "2m_temperature"])
    tp_name = find_var(ds, ["tp", "total_precipitation"])

    wind_speed = np.sqrt(ds[u_name] ** 2 + ds[v_name] ** 2)
    wind_value = spatial_temporal_mean(wind_speed)

    temp_value = spatial_temporal_mean(ds[t_name]) - 273.15

    # ERA5 total_precipitation is metres of water equivalent per time step.
    # Convert to mm, then average daily total across the month.
    tp_mm_total = float(ds[tp_name].sum(skipna=True).values) * 1000.0
    days_in_month = pd.Period(f"{year}-{month:02d}").days_in_month
    rain_value = tp_mm_total / days_in_month

    date_str = f"{year}-{month:02d}-01"

    rows = [
        {
            "year": year,
            "month": month,
            "date": date_str,
            "variable": "wind",
            "value": wind_value,
            "unit": "m/s",
            "source_workbook": str(path),
            "source_sheet": "Wind",
        },
        {
            "year": year,
            "month": month,
            "date": date_str,
            "variable": "rain",
            "value": rain_value,
            "unit": "mm/d",
            "source_workbook": str(path),
            "source_sheet": "Rain",
        },
        {
            "year": year,
            "month": month,
            "date": date_str,
            "variable": "temp",
            "value": temp_value,
            "unit": "deg_c",
            "source_workbook": str(path),
            "source_sheet": "Temp",
        },
    ]

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("month", type=int)
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to ERA5 NetCDF file. Defaults to data/raw/era5_YYYY_MM.nc",
    )
    args = parser.parse_args()

    input_path = args.input or RAW_DIR / f"era5_{args.year}_{args.month:02d}.nc"

    if not input_path.exists():
        raise FileNotFoundError(f"Missing ERA5 NetCDF file: {input_path}")

    df = process_file(input_path, args.year, args.month)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote {len(df)} rows to {OUTPUT_CSV}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
