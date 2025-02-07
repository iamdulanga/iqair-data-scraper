import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from time import sleep
from datetime import datetime, timezone, timedelta

# Create 'maps' folder if it doesn't exist
os.makedirs('maps', exist_ok=True)

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
    province_list = soup.find('ul', class_='state-list')

    if province_list:
        province_links = {}
        
        for item in province_list.find_all('li', class_='state-list__item'):
            link_tag = item.find('a')
            if link_tag:
                province_name = link_tag.text.strip()
                province_url = base_url + link_tag['href']
                province_links[province_name] = province_url

        all_station_data = []

        for province, url in province_links.items():
            prov_response = requests.get(url, headers=headers)
            if prov_response.status_code == 200:
                prov_soup = BeautifulSoup(prov_response.text, 'html.parser')
                station_list = prov_soup.find('ul', class_='location-list')

                if station_list:
                    for station in station_list.find_all('li', class_='location-item'):
                        city = station.find('span', class_='location-item__name').text.strip()
                        aqi = station.find('span', class_='location-item__value').text.strip()
                        all_station_data.append({"Province": province, "City": city, "AQI": int(aqi)})

        df_all_stations = pd.DataFrame(all_station_data)

        # Geocode cities to get latitude & longitude
        geolocator = Nominatim(user_agent="sri_lanka_aqi_map")
        def get_coordinates(city):
            try:
                location = geolocator.geocode(city + ", Sri Lanka")
                if location:
                    return location.latitude, location.longitude
            except:
                return None, None
            return None, None

        df_all_stations["Latitude"], df_all_stations["Longitude"] = zip(
            *df_all_stations["City"].apply(get_coordinates)
        )

        # Create Map
        sri_lanka_map = folium.Map(location=[7.8731, 80.7718], zoom_start=7)

        # Function to get AQI color
        def get_aqi_color(aqi):
            if aqi <= 50:
                return "green"
            elif aqi <= 100:
                return "yellow"
            elif aqi <= 150:
                return "orange"
            elif aqi <= 200:
                return "red"
            elif aqi <= 300:
                return "purple"
            else:
                return "maroon"

        # Add markers to the map
        for _, row in df_all_stations.iterrows():
            if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=8,
                    popup=f"{row['City']} (AQI: {row['AQI']})",
                    color=get_aqi_color(row["AQI"]),
                    fill=True,
                    fill_color=get_aqi_color(row["AQI"]),
                    fill_opacity=0.7,
                ).add_to(sri_lanka_map)

        # Set Sri Lanka timezone (GMT+5:30)
        sl_time = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d_%H-%M-%S")

        # Save the map as an HTML file in the 'maps' folder
        map_file = f"all_stations_maps/Sri_Lanka_AQI_Map_{sl_time}.html"
        sri_lanka_map.save(map_file)

        print(f"✅ Interactive map saved as {map_file}")
    else:
        print("No province list found on the page.")
else:
    print(f"Failed to retrieve the main page. Status code: {response.status_code}")
