import requests
from bs4 import BeautifulSoup

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
    province_list = soup.find('ul', class_='state-list')
    
    if province_list:
        province_links = {}
        
        # Extract province names and URLs
        for item in province_list.find_all('li', class_='state-list__item'):
            link_tag = item.find('a')
            if link_tag:
                province_name = link_tag.text.strip()
                province_url = base_url + link_tag['href']
                province_links[province_name] = province_url
        
        # Now scrape each province for city AQI data
        for province, url in province_links.items():
            print(f"\n=== {province} ===\n")
            
            prov_response = requests.get(url, headers=headers)
            if prov_response.status_code == 200:
                prov_soup = BeautifulSoup(prov_response.text, 'html.parser')

                # Find the station list container
                station_list = prov_soup.find('ul', class_='location-list')
                
                if station_list:
                    data = []

                    # Extract city names and AQI values
                    for station in station_list.find_all('li', class_='location-item'):
                        city = station.find('span', class_='location-item__name').text.strip()
                        aqi = station.find('span', class_='location-item__value').text.strip()
                        data.append((city, aqi))

                    # Print the data
                    print(f"{'City':<20}{'AQI'}")
                    print("-" * 30)
                    for city, aqi in data:
                        print(f"{city:<20}{aqi}")

                    # Find the most polluted city in this province
                    if data:
                        most_polluted = max(data, key=lambda x: int(x[1]))
                        print(f"\nMost Polluted City: {most_polluted[0]} (AQI: {most_polluted[1]})")
                else:
                    print("No AQI data found for this province.")
            else:
                print(f"Failed to retrieve data for {province}. Status code: {prov_response.status_code}")
    else:
        print("No province list found on the page.")
else:
    print(f"Failed to retrieve the main page. Status code: {response.status_code}")
