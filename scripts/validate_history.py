from pathlib import Path
import pandas as pd

CSV_PATH = Path("data/weather_history.csv")
EXPECTED_VARIABLES = {"wind", "rain", "temp"}

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing CSV: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    required_columns = {
        "year",
        "month",
        "date",
        "variable",
        "value",
        "unit",
        "source_workbook",
        "source_sheet",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    variables = set(df["variable"].unique())
    if variables != EXPECTED_VARIABLES:
        raise ValueError(f"Unexpected variables: {sorted(variables)}")

    bad_months = df[~df["month"].between(1, 12)]
    if not bad_months.empty:
        raise ValueError("Found month values outside 1-12")

    duplicates = df[df.duplicated(subset=["year", "month", "variable"], keep=False)]
    if not duplicates.empty:
        raise ValueError(f"Found duplicate year/month/variable rows:\n{duplicates}")

    null_values = df[df["value"].isna()]
    if not null_values.empty:
        raise ValueError(f"Found null values:\n{null_values}")

    latest = df.sort_values(["year", "month"]).iloc[-1]
    latest_year = int(latest["year"])
    latest_month = int(latest["month"])

    latest_block = df[(df["year"] == latest_year) & (df["month"] == latest_month)]
    latest_variables = set(latest_block["variable"].unique())

    if latest_variables != EXPECTED_VARIABLES:
        raise ValueError(
            f"Latest month {latest_year}-{latest_month:02d} is incomplete: "
            f"{sorted(latest_variables)}"
        )

    print("Validation OK")
    print(f"Rows: {len(df)}")
    print(f"Variables: {', '.join(sorted(variables))}")
    print(f"Latest complete month: {latest_year}-{latest_month:02d}")


if __name__ == "__main__":
    main()
