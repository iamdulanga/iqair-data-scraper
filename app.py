import os
from flask import Flask, render_template, send_file
from datetime import datetime
import pandas as pd
import folium
from geopy.geocoders import Nominatim
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Folders where the files will be stored
MAPS_FOLDER = 'maps'
CHARTS_FOLDER = 'charts'

# Ensure directories exist
os.makedirs(MAPS_FOLDER, exist_ok=True)
os.makedirs(CHARTS_FOLDER, exist_ok=True)

# Function to generate charts (same as your previous code for charts)
def generate_chart():
    base_url = "https://www.iqair.com"
    headers = {"User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"}
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

            most_polluted_cities = []

            for province, url in province_links.items():
                prov_response = requests.get(url, headers=headers)
                if prov_response.status_code == 200:
                    prov_soup = BeautifulSoup(prov_response.text, 'html.parser')
                    station_list = prov_soup.find('ul', class_='location-list')

                    if station_list:
                        province_data = []
                        for station in station_list.find_all('li', class_='location-item'):
                            city = station.find('span', class_='location-item__name').text.strip()
                            aqi = station.find('span', class_='location-item__value').text.strip()
                            province_data.append((city, int(aqi)))
                        if province_data:
                            most_polluted = max(province_data, key=lambda x: x[1])
                            most_polluted_cities.append({
                                "Province": province,
                                "City": most_polluted[0],
                                "AQI": most_polluted[1]
                            })

            df_most_polluted = pd.DataFrame(most_polluted_cities)
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_path = f"{CHARTS_FOLDER}/Sri_Lanka_AQI_Chart_{current_time}.xlsx"
            df_most_polluted.to_excel(file_path, index=False)
            return file_path
    return None

# Function to generate maps (same as your previous code for maps)
def generate_map():
    base_url = "https://www.iqair.com"
    headers = {"User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"}
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

            most_polluted_cities = []
            for province, url in province_links.items():
                prov_response = requests.get(url, headers=headers)
                if prov_response.status_code == 200:
                    prov_soup = BeautifulSoup(prov_response.text, 'html.parser')
                    station_list = prov_soup.find('ul', class_='location-list')

                    if station_list:
                        province_data = []
                        for station in station_list.find_all('li', class_='location-item'):
                            city = station.find('span', class_='location-item__name').text.strip()
                            aqi = station.find('span', class_='location-item__value').text.strip()
                            province_data.append((city, int(aqi)))

                        if province_data:
                            most_polluted = max(province_data, key=lambda x: x[1])
                            most_polluted_cities.append({
                                "Province": province,
                                "City": most_polluted[0],
                                "AQI": most_polluted[1]
                            })

            df_most_polluted = pd.DataFrame(most_polluted_cities)
            geolocator = Nominatim(user_agent="sri_lanka_aqi_map")
            def get_coordinates(city):
                try:
                    location = geolocator.geocode(city + ", Sri Lanka")
                    if location:
                        return location.latitude, location.longitude
                except:
                    return None, None
                return None, None

            df_most_polluted["Latitude"], df_most_polluted["Longitude"] = zip(
                *df_most_polluted["City"].apply(get_coordinates)
            )

            sri_lanka_map = folium.Map(location=[7.8731, 80.7718], zoom_start=7)

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

            for _, row in df_most_polluted.iterrows():
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

            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            map_file = f"{MAPS_FOLDER}/Sri_Lanka_AQI_Map_{current_time}.html"
            sri_lanka_map.save(map_file)
            return map_file
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_chart')
def generate_chart_view():
    file_path = generate_chart()
    return file_path if file_path else "Failed to generate chart."

@app.route('/generate_map')
def generate_map_view():
    file_path = generate_map()
    return file_path if file_path else "Failed to generate map."

@app.route('/list_files')
def list_files():
    maps_files = os.listdir(MAPS_FOLDER)
    charts_files = os.listdir(CHARTS_FOLDER)
    return {"maps": maps_files, "charts": charts_files}

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    folder_path = MAPS_FOLDER if folder == 'maps' else CHARTS_FOLDER
    file_path = os.path.join(folder_path, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
