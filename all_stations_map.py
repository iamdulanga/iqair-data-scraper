import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from datetime import datetime, timezone, timedelta
from folium.plugins import FloatImage

# Constants
BASE_URL = "https://www.iqair.com"
HEADERS = {"User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"}

# External URL for the color index image (update with your actual GitHub raw URL)
COLOR_INDEX_URL = "https://raw.githubusercontent.com/DulangaDasanayake/iqair-data-scraper/main/assets/aqi_mini.png"

def get_province_links():
    """Retrieve province links for Sri Lanka from IQAir."""
    main_url = f"{BASE_URL}/sri-lanka"
    response = requests.get(main_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Failed to retrieve the main page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    province_list = soup.find("ul", class_="state-list")

    if not province_list:
        print("No province list found on the page.")
        return None

    province_links = {}
    for item in province_list.find_all("li", class_="state-list__item"):
        link_tag = item.find("a")
        if link_tag:
            province_name = link_tag.text.strip()
            province_url = BASE_URL + link_tag["href"]
            province_links[province_name] = province_url

    return province_links

def get_all_station_data(province_links):
    """Scrape station data (city and AQI) for each province."""
    all_station_data = []

    for province, url in province_links.items():
        prov_response = requests.get(url, headers=HEADERS)
        if prov_response.status_code != 200:
            continue

        prov_soup = BeautifulSoup(prov_response.text, "html.parser")
        station_list = prov_soup.find("ul", class_="location-list")

        if station_list:
            for station in station_list.find_all("li", class_="location-item"):
                city_tag = station.find("span", class_="location-item__name")
                aqi_tag = station.find("span", class_="location-item__value")
                if city_tag and aqi_tag:
                    city = city_tag.text.strip()
                    try:
                        aqi = int(aqi_tag.text.strip())
                    except ValueError:
                        continue
                    all_station_data.append(
                        {"Province": province, "City": city, "AQI": aqi}
                    )

    return all_station_data

def get_coordinates(geolocator, city):
    """Get latitude and longitude for a given city."""
    try:
        location = geolocator.geocode(city + ", Sri Lanka")
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

def get_aqi_color(aqi):
    """Return marker color based on AQI value."""
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

def get_aqi_message(aqi):
    """Return a descriptive message for the given AQI value."""
    if aqi <= 50:
        return "Good: Air quality is satisfactory."
    elif aqi <= 100:
        return "Moderate: Air quality is acceptable."
    elif aqi <= 150:
        return "Unhealthy for sensitive groups: Some may experience effects."
    elif aqi <= 200:
        return "Unhealthy: Everyone may begin to experience effects."
    elif aqi <= 300:
        return "Very Unhealthy: Health warnings of emergency conditions."
    else:
        return "Hazardous: Health alert—serious effects possible."

def main():
    # Retrieve province links and station data
    province_links = get_province_links()
    if not province_links:
        return

    all_station_data = get_all_station_data(province_links)
    if not all_station_data:
        print("No station data found.")
        return

    df_all_stations = pd.DataFrame(all_station_data)

    # Geocode cities to obtain latitude and longitude
    geolocator = Nominatim(user_agent="sri_lanka_aqi_map")
    df_all_stations["Latitude"], df_all_stations["Longitude"] = zip(
        *df_all_stations["City"].apply(lambda city: get_coordinates(geolocator, city))
    )

    # Create the base map centered on Sri Lanka
    sri_lanka_map = folium.Map(location=[7.8731, 80.7718], zoom_start=7)

    # Add markers with styled tooltips
    for _, row in df_all_stations.iterrows():
        if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
            color = get_aqi_color(row["AQI"])

            # tooltip HTML content
            tooltip_html = f"""
            <div style="font-family: 'Helvetica', Arial, sans-serif;
                        border-radius: 8px;
                        overflow: hidden;
                        width: 240px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
              <div style="background: linear-gradient(135deg, {color} 0%, #cc1200 100%);
                          color: #fff;
                          padding: 8px;">
                <div style="font-size: 12px; text-align: center;">
                  {datetime.now().strftime("On %B %d, %Y, %I:%M:%S %p GMT")}
                </div>
                <div style="font-size: 14px; font-weight: bold; text-align: center; margin-top: 4px;">
                  {row['City']}
                </div>
                <div style="font-size: 48px; font-weight: bold; text-align: center; line-height: 1;">
                  {row['AQI']}
                </div>
              </div>
              <div style="background-color: #fff; color: #333; padding: 8px; font-size: 12px; text-align: center;">
                {get_aqi_message(row['AQI'])}
              </div>
            </div>
            """
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="background-color:{color};
                                width:30px; height:30px;
                                border-radius:50%;
                                text-align:center;
                                font-weight:bold;
                                color:black;
                                line-height:30px;">
                      {row['AQI']}
                    </div>
                    """
                ),
                tooltip=folium.Tooltip(tooltip_html),
            ).add_to(sri_lanka_map)

    # Add the color index image using the external URL
    FloatImage(COLOR_INDEX_URL, bottom=5, right=5).add_to(sri_lanka_map)

    # Format current time in Sri Lanka timezone (GMT+5:30)
    sl_time = datetime.now(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d_%H-%M-%S")

    # Ensure the output directory exists
    output_dir = "all_stations_maps"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the map as an HTML file
    map_file = os.path.join(output_dir, f"SL_All_Stations_AQI_Map_{sl_time}.html")
    sri_lanka_map.save(map_file)
    print(f"✅ Interactive map saved as {map_file}")

if __name__ == "__main__":
    main()
