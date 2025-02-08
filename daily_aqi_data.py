import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

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

    all_cities = []
    for station in all_station_data:
        city_data = {"City/Time": station["City"]}

        # Replicate AQI value for all 5-minute intervals
        for time in times:
            city_data[time] = station["AQI"]

        all_cities.append(city_data)

    # Convert to DataFrame and save to Excel
    df = pd.DataFrame(all_cities)
    date_str = datetime.now(sl_timezone).strftime("%Y-%m-%d")  # Use Sri Lanka timezone
    file_path = f"daily_aqi_data/SL_Daily_AQI_{date_str}.xlsx"

    # Check if the file already exists and append new data if needed
    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path, sheet_name="All Cities")
        df = pd.concat([existing_data, df], ignore_index=True)

    # Save the data to the Excel file
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="All Cities", index=False)

    print(f"✅ Data successfully saved to {file_path}")

# Run the data fetch function
fetch_aqi_data()
