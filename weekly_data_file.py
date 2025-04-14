import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# Set SLST timezone
SLST = pytz.timezone("Asia/Colombo")

# Folders
DAILY_FOLDER = "charts"
WEEKLY_FOLDER = "weekly_charts"
os.makedirs(WEEKLY_FOLDER, exist_ok=True)

# Get current time in SLST and calculate last week
today_sl = datetime.now(SLST)
last_monday_sl = today_sl - timedelta(days=today_sl.weekday() + 7)
last_sunday_sl = last_monday_sl + timedelta(days=6)
last_sunday_sl = last_sunday_sl.replace(hour=23, minute=59, second=59, microsecond=999999)


start_str = last_monday_sl.strftime("%Y-%m-%d")
end_str = last_sunday_sl.strftime("%Y-%m-%d")

# Collect all timestamps in that week
aqi_dict = {}

for file in os.listdir(DAILY_FOLDER):
    if not file.endswith(".xlsx") or not file.startswith("AQI_Data_"):
        print(f"⚠️ Skipped file: {file} (invalid format or naming)")
        continue

    try:
        timestamp_str = file.replace(".xlsx", "").split("AQI_Data_")[-1]
        # Parse as naive datetime (assumed local/UTC) and convert to SLST
        naive_dt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
        slst_dt = SLST.localize(naive_dt)

        if last_monday_sl <= slst_dt <= last_sunday_sl:
            file_path = os.path.join(DAILY_FOLDER, file)
            df = pd.read_excel(file_path, sheet_name="All Cities")
            col_label = slst_dt.strftime("%Y-%m-%d %H:%M")

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
