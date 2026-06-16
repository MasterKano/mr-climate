from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
history_path = ROOT / "data" / "weather_history.csv"
feed_path = ROOT / "data" / "weather_excel_feed.csv"

df = pd.read_csv(history_path)
df = df[df["year"] >= 2026].copy()
df = df.sort_values(["year", "month", "variable"])

columns = ["year", "month", "date", "variable", "value", "unit"]
df[columns].to_csv(feed_path, index=False)

print(f"Wrote {len(df)} rows to {feed_path}")
