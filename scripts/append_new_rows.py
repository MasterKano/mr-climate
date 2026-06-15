from pathlib import Path
import pandas as pd

HISTORY_CSV = Path("data/weather_history.csv")
NEW_ROWS_CSV = Path("data/weather_new_rows.csv")
EXPECTED_VARIABLES = {"wind", "rain", "temp"}


def main():
    if not NEW_ROWS_CSV.exists():
        raise FileNotFoundError(
            f"Missing {NEW_ROWS_CSV}. Create it with columns: "
            "year,month,date,variable,value,unit,source_workbook,source_sheet"
        )

    history = pd.read_csv(HISTORY_CSV)
    new_rows = pd.read_csv(NEW_ROWS_CSV)

    required_columns = list(history.columns)
    missing = set(required_columns) - set(new_rows.columns)
    if missing:
        raise ValueError(f"New rows file is missing columns: {sorted(missing)}")

    new_rows = new_rows[required_columns]

    variables = set(new_rows["variable"].unique())
    if variables != EXPECTED_VARIABLES:
        raise ValueError(f"New rows must contain exactly wind, rain, temp. Found: {sorted(variables)}")

    periods = new_rows[["year", "month"]].drop_duplicates()
    if len(periods) != 1:
        raise ValueError("New rows must contain exactly one year/month period")

    combined = pd.concat([history, new_rows], ignore_index=True)

    duplicates = combined[combined.duplicated(subset=["year", "month", "variable"], keep=False)]
    if not duplicates.empty:
        raise ValueError(f"Duplicate year/month/variable rows found:\n{duplicates}")

    combined = combined.sort_values(["year", "month", "variable"]).reset_index(drop=True)
    combined.to_csv(HISTORY_CSV, index=False)

    period = periods.iloc[0]
    print(f"Appended {len(new_rows)} rows to {HISTORY_CSV}")
    print(f"Added month: {int(period['year'])}-{int(period['month']):02d}")


if __name__ == "__main__":
    main()
