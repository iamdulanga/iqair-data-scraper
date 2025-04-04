import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuration
DAILY_FOLDER = "charts"
MONTHLY_FOLDER = "monthly_charts"
os.makedirs(MONTHLY_FOLDER, exist_ok=True)

# Determine previous month (e.g., if today is April 1, target March)
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
prev_month = first_day_this_month - pd.DateOffset(days=1)
prev_month_str = prev_month.strftime("%Y-%m")

# Data container
all_cities_frames = []

# Process each daily file in the folder
for file in os.listdir(DAILY_FOLDER):
    if file.endswith(".xlsx") and prev_month_str in file:
        file_path = os.path.join(DAILY_FOLDER, file)
        try:
            df_all = pd.read_excel(file_path, sheet_name="All Cities")
            all_cities_frames.append(df_all)
        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")

# Save combined file
if all_cities_frames:
    monthly_file = os.path.join(MONTHLY_FOLDER, f"SL_AQI_Monthly_{prev_month_str}.xlsx")
    df_combined = pd.concat(all_cities_frames, ignore_index=True)
    df_combined.to_excel(monthly_file, sheet_name="All Cities", index=False)
    print(f"✅ Monthly AQI data saved: {monthly_file}")
else:
    print("⚠️ No daily AQI files found for the previous month.")
