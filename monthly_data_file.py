import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Config
DAILY_FOLDER = "charts"
MONTHLY_FOLDER = "monthly_charts"
os.makedirs(MONTHLY_FOLDER, exist_ok=True)

# Determine previous month (e.g., if today is April 1 → target March)
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
prev_month = first_day_this_month - pd.DateOffset(days=1)
prev_month_str = prev_month.strftime("%Y-%m")

# Store pivoted AQI data here
aqi_dict = {}

for file in os.listdir(DAILY_FOLDER):
    if file.endswith(".xlsx") and file.startswith(f"SL_AQI_{prev_month_str}"):
        file_path = os.path.join(DAILY_FOLDER, file)
        try:
            df = pd.read_excel(file_path, sheet_name="All Cities")
            
            # Extract full timestamp from filename
            timestamp_str = file.replace(".xlsx", "").split("SL_AQI_")[-1]
            timestamp_fmt = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
            col_label = timestamp_fmt.strftime("%Y-%m-%d %H:%M")  # or %H:%M:%S if you want precision

            for _, row in df.iterrows():
                station = row.get("City")
                aqi = row.get("AQI")
                if station not in aqi_dict:
                    aqi_dict[station] = {}
                aqi_dict[station][col_label] = aqi

        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

# Convert to DataFrame
df_pivoted = pd.DataFrame.from_dict(aqi_dict, orient="index").sort_index()
df_pivoted.index.name = "City"

# Save the file
if not df_pivoted.empty:
    out_path = os.path.join(MONTHLY_FOLDER, f"SL_AQI_Timeseries_{prev_month_str}.xlsx")
    df_pivoted.to_excel(out_path)
    print(f"✅ Pivoted monthly AQI timeseries saved: {out_path}")
else:
    print("⚠️ No AQI data found for the previous month.")
