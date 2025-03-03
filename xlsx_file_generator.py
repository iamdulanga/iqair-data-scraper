import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone, timedelta

# Ensure the 'charts' folder exists
def ensure_folder_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Create 'charts' folder if it doesn't exist
ensure_folder_exists("charts")

# Base URL
base_url = "https://www.iqair.com"

# Define headers to avoid getting blocked
headers = {
    "User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"
}

# Get the main Sri Lanka page to extract province links
main_url = f"{base_url}/sri-lanka"
response = requests.get(main_url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find province list container
    province_list = soup.find('ul', class_='location-list')

    if province_list:
        province_links = {}

        # Extract province names and URLs
        for item in province_list.find_all('li', class_='location-item'):
            link_tag = item.find('a')
            if link_tag:
                province_name = link_tag.find('span', class_='location-item__name').text.strip()
                province_url = base_url + link_tag['href']
                province_links[province_name] = province_url

        # Lists to store data
        all_cities = []
        most_polluted_cities = []

        # Now scrape each province for city AQI data
        for province, url in province_links.items():
            prov_response = requests.get(url, headers=headers)
            if prov_response.status_code == 200:
                prov_soup = BeautifulSoup(prov_response.text, 'html.parser')

                # Find the station list container
                station_list = prov_soup.find('ul', class_='location-list')

                if station_list:
                    province_data = []  # Store all cities in this province

                    for station in station_list.find_all('li', class_='location-item'):
                        city = station.find(
                            'span', class_='location-item__name').text.strip()
                        aqi_text = station.find(
                            'span', class_='location-item__value').text.strip()

                        # Handle empty AQI values gracefully
                        aqi = int(aqi_text) if aqi_text.isdigit() else None

                        # Append to overall data if AQI is valid
                        if aqi is not None:
                            all_cities.append(
                                {"Province": province, "City": city, "AQI": aqi})
                            province_data.append((city, aqi))

                    # Get the most polluted city in this province
                    if province_data:
                        most_polluted = max(province_data, key=lambda x: x[1])
                        most_polluted_cities.append({
                            "Province": province,
                            "City": most_polluted[0],
                            "AQI": most_polluted[1]
                        })

        # Convert data to DataFrames
        df_all_cities = pd.DataFrame(all_cities)
        df_most_polluted = pd.DataFrame(most_polluted_cities)

        # Set Sri Lanka timezone (GMT+5:30)
        sl_time = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime(
            "%Y-%m-%d_%H-%M-%S")

        # Save to Excel with the corrected timestamp
        file_path = f"charts/SL_AQI_{sl_time}.xlsx"
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df_all_cities.to_excel(
                writer, sheet_name="All Cities", index=False)
            df_most_polluted.to_excel(
                writer, sheet_name="Most Polluted Cities", index=False)

        print(f"✅ Data successfully saved to {file_path}")
    else:
        print("No province list found on the page.")
else:
    print(
        f"Failed to retrieve the main page. Status code: {response.status_code}")
