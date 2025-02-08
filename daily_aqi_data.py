import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup

# Base URL
BASE_URL = "https://www.iqair.com"
headers = {
    "User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"
}

# Set Sri Lanka timezone (GMT+5:30)
sl_timezone = timezone(timedelta(hours=5, minutes=30))

# Get the main Sri Lanka page to extract province links
def get_all_stations():
    station_data = []
    main_url = f"{BASE_URL}/sri-lanka"
    response = requests.get(main_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        province_list = soup.find('ul', class_='state-list')

        if province_list:
            province_links = {}

            for item in province_list.find_all('li', class_='state-list__item'):
                link_tag = item.find('a')
                if link_tag:
                    province_name = link_tag.text.strip()
                    province_url = BASE_URL + link_tag['href']
                    province_links[province_name] = province_url

            for province, url in province_links.items():
                prov_response = requests.get(url, headers=headers)
                if prov_response.status_code == 200:
                    prov_soup = BeautifulSoup(prov_response.text, 'html.parser')
                    station_list = prov_soup.find('ul', class_='location-list')

                    if station_list:
                        for station in station_list.find_all('li', class_='location-item'):
                            city = station.find(
                                'span', class_='location-item__name').text.strip()
                            aqi = int(station.find(
                                'span', class_='location-item__value').text.strip())
                            station_data.append({"City": city, "AQI": aqi})

    return station_data

# Generate time intervals for a full day (every 5 minutes)
def generate_time_intervals():
    start_time = datetime.strptime("00:00", "%H:%M")
    time_intervals = []
    for i in range(288):  # 24 hours * 60 minutes / 5-minute intervals = 288 intervals
        time_intervals.append(
            (start_time + timedelta(minutes=5 * i)).strftime("%H:%M"))
    return time_intervals

# Fetch AQI data for the stations and fill in the table
def fetch_aqi_data():
    times = generate_time_intervals()  # Generate time intervals every 5 minutes
    all_station_data = get_all_stations()

    # Ensure the directory exists before saving the file
    os.makedirs("daily_aqi_data", exist_ok=True)

    # Start fresh at the beginning of each day
    date_str = datetime.now(sl_timezone).strftime("%Y-%m-%d")  # Use Sri Lanka timezone
    file_path = f"daily_aqi_data/SL_Daily_AQI_{date_str}.xlsx"

    # If file does not exist, create it
    if not os.path.exists(file_path):
        # Prepare the first row (times) and the first column (cities)
        time_row = ["City/Time"] + times  # First row with time slots
        city_column = [station["City"] for station in all_station_data]

        # Create a DataFrame with the first column as 'City/Time'
        data = {"City/Time": city_column}
        
        # Fill the first column (00:00) with AQI data
        data["00:00"] = [station["AQI"] for station in all_station_data]  # Fill 00:00 with AQI data

        # Add additional time columns with None or empty values initially
        for i, time in enumerate(times[1:]):  # Start from the second time slot (00:05 onwards)
            data[time] = [None] * len(city_column)

        # Convert to DataFrame and save as the first day's data
        df = pd.DataFrame(data)

        # Save the data to the Excel file
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="All Cities", index=False, header=time_row)

        print(f"✅ Fresh data file created for {date_str}")
    
    else:
        # If file already exists, add a new column with AQI data for the next 5-minute interval
        existing_data = pd.read_excel(file_path, sheet_name="All Cities", header=0)

        # Get the latest time column (e.g., '00:05', '00:10', etc.)
        latest_time_column = [col for col in existing_data.columns if col != "City/Time"]
        latest_time_column = max(latest_time_column, default="00:00")

        # Check if 00:00 already exists and avoid filling it again
        if latest_time_column != "00:00":
            # Get the next time slot (e.g., '00:05')
            next_time = (datetime.strptime(latest_time_column, "%H:%M") + timedelta(minutes=5)).strftime("%H:%M")
        else:
            # If it's the first run of the day, skip updating 00:00
            next_time = "00:05"

        # Add a new column with AQI data for the next time slot
        existing_data[next_time] = None  # Add the new time column with None values initially

        # Fill the AQI data for this new time slot
        for i, row in existing_data.iterrows():
            for station in all_station_data:
                if row["City/Time"] == station["City"]:
                    existing_data.at[i, next_time] = station["AQI"]
                    break

        # Save the updated data to the Excel file
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            existing_data.to_excel(writer, sheet_name="All Cities", index=False)

        print(f"✅ AQI data for {next_time} added to {file_path}")

# Run the data fetch function
fetch_aqi_data()
