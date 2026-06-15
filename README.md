# mr-climate

Python pipeline for updating the Wind/Rain/Temp Excel workbook from a CSV source of truth.

## Files

- data/weather_history.csv = source of truth
- workbook/Wind Rain Temp (Active).xlsx = workbook template
- workbook/Wind Rain Temp (Generated).xlsx = generated output, ignored by Git
- data/raw/ = raw ERA5 NetCDF downloads, ignored by Git

## Setup

Run:
source /workspaces/mr-climate/.venv/bin/activate
python -m pip install -r requirements.txt

## Local pipeline

Run:
python scripts/run_pipeline.py

Expected final line:
Pipeline OK

## Full dry-run pipeline

Run:
python scripts/run_pipeline.py --full

This builds the next ERA5 request without downloading data, then validates and regenerates the workbook.

## Live ERA5 download

Only run when Copernicus CDS is stable:
python scripts/fetch_weather.py --download

If it returns HTTP 500 or starts retrying for 120 seconds, stop with Ctrl+C.

## Process downloaded file

Example for May 2026:
python scripts/process_era5_file.py 2026 5

This writes:
data/weather_new_rows.csv

## Append new weather rows

After reviewing data/weather_new_rows.csv:
python scripts/append_new_rows.py
python scripts/run_pipeline.py

## Manual fallback

If ERA5 is unavailable, copy data/weather_new_rows_template.csv to data/weather_new_rows.csv, fill wind/rain/temp values, then run:
python scripts/append_new_rows.py
python scripts/run_pipeline.py

## Do not commit

Never commit .venv/, ~/.cdsapirc, data/raw/, *.nc, or generated workbook files.
