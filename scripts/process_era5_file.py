from pathlib import Path
import argparse
import zipfile

import numpy as np
import pandas as pd
import xarray as xr

RAW_DIR = Path("data/raw")
OUTPUT_CSV = Path("data/weather_new_rows.csv")


def find_var(datasets, candidates):
    for ds in datasets:
        for candidate in candidates:
            if candidate in ds.data_vars:
                return ds[candidate]
    available = sorted({name for ds in datasets for name in ds.data_vars})
    raise KeyError(f"None of these variables found: {candidates}. Available: {available}")


def dataset_paths(path):
    if zipfile.is_zipfile(path):
        extract_dir = path.with_suffix("")
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(path) as archive:
            archive.extractall(extract_dir)

        candidates = [
            candidate
            for candidate in extract_dir.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in {".nc", ".netcdf"}
        ]

        if not candidates:
            raise FileNotFoundError(f"No NetCDF file found inside ZIP archive: {path}")

        return sorted(candidates)

    return [path]


def open_datasets(path):
    paths = dataset_paths(path)
    return [xr.open_dataset(p, engine="netcdf4") for p in paths]


def spatial_temporal_mean(data_array):
    return float(data_array.mean(dim=list(data_array.dims), skipna=True).values)


def process_file(path, year, month):
    datasets = open_datasets(path)

    u10 = find_var(datasets, ["u10", "10m_u_component_of_wind"])
    v10 = find_var(datasets, ["v10", "10m_v_component_of_wind"])
    t2m = find_var(datasets, ["t2m", "2m_temperature"])
    tp = find_var(datasets, ["tp", "total_precipitation"])

    wind_speed = np.sqrt(u10 ** 2 + v10 ** 2)
    wind_value = spatial_temporal_mean(wind_speed)

    temp_value = spatial_temporal_mean(t2m) - 273.15

    # ERA5 total_precipitation is metres of water equivalent per time step.
    # Average across grid cells first, then sum over time.
    # Convert monthly total from metres to mm, then express as mm/day.
    spatial_dims = [dim for dim in tp.dims if dim.lower() in {"latitude", "longitude", "lat", "lon"}]
    time_dims = [dim for dim in tp.dims if dim not in spatial_dims]

    tp_spatial_mean = tp.mean(dim=spatial_dims, skipna=True) if spatial_dims else tp
    tp_mm_total = float(tp_spatial_mean.sum(dim=time_dims, skipna=True).values) * 1000.0

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
        help="Path to ERA5 NetCDF or ZIP file. Defaults to data/raw/era5_YYYY_MM.nc",
    )
    args = parser.parse_args()

    input_path = args.input or RAW_DIR / f"era5_{args.year}_{args.month:02d}.nc"

    if not input_path.exists():
        raise FileNotFoundError(f"Missing ERA5 file: {input_path}")

    df = process_file(input_path, args.year, args.month)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote {len(df)} rows to {OUTPUT_CSV}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
