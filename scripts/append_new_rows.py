from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
history_path = ROOT / "data" / "weather_history.csv"
new_rows_path = ROOT / "data" / "weather_new_rows.csv"

KEYS = ["year", "month", "variable"]


def main():
    if not new_rows_path.exists():
        raise FileNotFoundError(f"Missing new rows file: {new_rows_path}")

    history = pd.read_csv(history_path)
    new_rows = pd.read_csv(new_rows_path)

    required = {"year", "month", "date", "variable", "value", "unit", "source_workbook", "source_sheet"}
    missing = required - set(new_rows.columns)
    if missing:
        raise ValueError(f"New rows file is missing columns: {sorted(missing)}")

    new_rows = new_rows.sort_values(KEYS).copy()

    duplicated_new = new_rows[new_rows.duplicated(KEYS, keep=False)]
    if not duplicated_new.empty:
        raise ValueError(f"Duplicate rows inside new rows file:\n{duplicated_new}")

    existing_keys = history[KEYS].astype(str).agg("|".join, axis=1)
    incoming_keys = new_rows[KEYS].astype(str).agg("|".join, axis=1)

    rows_to_add = new_rows[~incoming_keys.isin(existing_keys)].copy()

    if rows_to_add.empty:
        target_months = new_rows[["year", "month"]].drop_duplicates().to_dict("records")
        print(f"No new rows to append. Already present: {target_months}")
        return

    combined = pd.concat([history, rows_to_add], ignore_index=True)
    combined = combined.sort_values(["year", "month", "variable"]).reset_index(drop=True)

    duplicated_combined = combined[combined.duplicated(KEYS, keep=False)]
    if not duplicated_combined.empty:
        raise ValueError(f"Duplicate year/month/variable rows found after append:\n{duplicated_combined}")

    combined.to_csv(history_path, index=False)
    print(f"Appended {len(rows_to_add)} rows")
    print(f"History rows: {len(history)} -> {len(combined)}")


if __name__ == "__main__":
    main()
