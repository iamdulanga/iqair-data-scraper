import requests
from bs4 import BeautifulSoup

# Define the URL of the IQAir page you want to scrape
url = "https://www.iqair.com/sri-lanka/central"

# Define a custom user-agent to identify your bot
headers = {
    "User-Agent": "MyBot/1.0 (https://example.com; contact@example.com)"
}

# Send a GET request to the website
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the station list container
    station_list = soup.find('ul', class_='location-list')  # Update this based on the actual HTML structure
    
    if station_list:
        # Extract all city names and AQI values
        cities = []
        aqi_values = []
        
        # Loop through each station item
        for station in station_list.find_all('li', class_='location-item'):  # Update this based on the actual HTML structure
            city = station.find('span', class_='location-item__name').text.strip()  # Update this based on the actual HTML structure
            aqi = station.find('span', class_='location-item__value').text.strip()  # Update this based on the actual HTML structure
            
            cities.append(city)
            aqi_values.append(aqi)
        
        # Combine cities and AQI values into a list of tuples
        data = list(zip(cities, aqi_values))
        
        # # Print the data
        # print("City\t\tAQI")
        # print("---------------------")
        # for city, aqi in data:
        #     print(f"{city}\t\t{aqi}")

        # Print the data with proper spacing
        print(f"{'City':<20}{'AQI'}")
        print("-" * 30)
        for city, aqi in data:
         print(f"{city:<20}{aqi}")

        
        # Find the most polluted city
        most_polluted = max(data, key=lambda x: int(x[1]))
        print(f"\nMost Polluted City: {most_polluted[0]} (AQI: {most_polluted[1]})")
    
    else:
        print("Station list not found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
