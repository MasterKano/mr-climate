````
# mr-climate

Automated monthly Nordic weather data pipeline for the Wind/Rain/Temp Excel workbook.

## Purpose

This project replaces manual monthly weather data collection with a reproducible Python and GitHub Actions workflow.

It fetches ERA5 weather data, processes it into monthly wind, rain and temperature values, updates the historical CSV source of truth, refreshes a public Excel feed, and updates the active reporting workbook.

## Data source and area

Source: Copernicus ERA5 single-level reanalysis.

Area definition is based on the KNMI Climate Explorer setup used for the historical workbook:

- North: 71°N
- West: 4°E
- South: 55°N
- East: 32°E

In CDS/ERA5 format:

```python
AREA = [71, 4, 55, 32]
````

Variables:

* Wind: 10m u/v wind components converted to wind speed, m/s
* Rain: total precipitation converted to mm/day
* Temperature: 2m temperature converted to °C

## Main outputs

* `data/weather_history.csv` = source of truth
* `data/weather_excel_feed.csv` = public Excel feed, 2026 onward
* `workbook/Wind Rain Temp (Active).xlsx` = active workbook
* `workbook/Wind Rain Temp (Generated).xlsx` = generated output, ignored by Git
* `data/raw/` = raw ERA5 NetCDF downloads, ignored by Git

## Public Excel feed

Excel can pull the live 2026+ data from:

```text
https://raw.githubusercontent.com/MasterKano/mr-climate/main/data/weather_excel_feed.csv
```

In Excel:

```text
Data → Get Data → From Web
```

## Scheduled automation

The monthly workflow runs via GitHub Actions:

```text
.github/workflows/monthly-update.yml
```

Schedule:

```text
06:00 UTC on the 10th day of each month
```

The workflow pulls the previous month, then updates:

* `data/weather_history.csv`
* `data/weather_excel_feed.csv`
* `workbook/Wind Rain Temp (Active).xlsx`

The workflow can also be run manually from:

```text
GitHub → Actions → Monthly Weather Update → Run workflow
```

## Setup

Run:

```bash
source /workspaces/mr-climate/.venv/bin/activate
python -m pip install -r requirements.txt
```

## Local pipeline

Run:

```bash
python scripts/run_pipeline.py
```

Expected final line:

```text
Pipeline OK
```

## Full dry-run pipeline

Run:

```bash
python scripts/run_pipeline.py --full
```

This builds the next ERA5 request without downloading data, then validates and regenerates the workbook.

## Live ERA5 download

For a specific month:

```bash
python scripts/fetch_weather.py --download --year 2026 --month 5
```

Without `--year` and `--month`, the script targets the next month after the latest complete historical month.

Only run live downloads when Copernicus CDS is stable. If it returns repeated server errors or long retries, stop with `Ctrl+C` and retry later.

## Process downloaded file

Example for May 2026:

```bash
python scripts/process_era5_file.py 2026 5
```

This writes:

```text
data/weather_new_rows.csv
```

## Append new weather rows

After reviewing `data/weather_new_rows.csv`:

```bash
python scripts/append_new_rows.py
python scripts/validate_history.py
python scripts/export_excel_feed.py
python scripts/update_workbook_from_csv.py
```

Then promote the generated workbook:

```bash
cp "workbook/Wind Rain Temp (Generated).xlsx" "workbook/Wind Rain Temp (Active).xlsx"
python scripts/compare_workbooks.py
```

## Manual fallback

If ERA5 is unavailable, copy:

```text
data/weather_new_rows_template.csv
```

to:

```text
data/weather_new_rows.csv
```

Fill wind/rain/temp values manually, then run:

```bash
python scripts/append_new_rows.py
python scripts/run_pipeline.py
```

## Do not commit

Never commit:

* `.venv/`
* `~/.cdsapirc`
* `data/raw/`
* `*.nc`
* `workbook/Wind Rain Temp (Generated).xlsx`
* `data/weather_new_rows.csv`

Secrets such as `CDSAPI_URL` and `CDSAPI_KEY` are stored in GitHub Actions secrets, not in the repository.

````

Then commit it:

```bash
cat > README.md <<'MD'
[paste the merged README content here]
MD

git add README.md
git commit -m "Update README with project overview and operation notes"
git push
git status
````
