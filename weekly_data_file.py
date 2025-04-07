import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Folders
DAILY_FOLDER = "charts"
WEEKLY_FOLDER = "weekly_charts"
os.makedirs(WEEKLY_FOLDER, exist_ok=True)

# Get today's date (assumed to be Monday)
today = datetime.today()
last_monday = today - timedelta(days=today.weekday() + 7)
last_sunday = last_monday + timedelta(days=6)

start_str = last_monday.strftime("%Y-%m-%d")
end_str = last_sunday.strftime("%Y-%m-%d")

# Collect all timestamps in that week
aqi_dict = {}

for file in os.listdir(DAILY_FOLDER):
    if not file.endswith(".xlsx") or not file.startswith("SL_AQI_"):
        print(f"⚠️ Skipped file: {file} (invalid format or naming)")
        continue

    try:
        timestamp_str = file.replace(".xlsx", "").split("SL_AQI_")[-1]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

        if last_monday <= timestamp <= last_sunday + timedelta(days=1):
            file_path = os.path.join(DAILY_FOLDER, file)
            df = pd.read_excel(file_path, sheet_name="All Cities")
            col_label = timestamp.strftime("%Y-%m-%d %H:%M")

            for _, row in df.iterrows():
                station = row.get("City")
                aqi = row.get("AQI")
                if station not in aqi_dict:
                    aqi_dict[station] = {}
                aqi_dict[station][col_label] = aqi

    except ValueError as ve:
        print(f"❌ Timestamp format error in {file}: {ve}")
    except pd.errors.EmptyDataError as ede:
        print(f"❌ No data in {file}: {ede}")
    except Exception as e:
        print(f"❌ Error processing {file}: {e}")

# Build and save
df_pivoted = pd.DataFrame.from_dict(aqi_dict, orient="index").sort_index()
df_pivoted.index.name = "City"

if not df_pivoted.empty:
    out_name = f"AQI_Weekly_{start_str}_to_{end_str}.xlsx"
    out_path = os.path.join(WEEKLY_FOLDER, out_name)
    df_pivoted.to_excel(out_path)
    print(f"✅ Weekly AQI timeseries saved: {out_path}")

else:
    print("⚠️ No AQI data found for last week.")
