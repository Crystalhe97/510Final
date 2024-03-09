import csv
import requests
import pandas as pd
from tqdm import tqdm  # tqdm is optional, used for progress bar

def get_location(address):
    """Get latitude and longitude for an address using Nominatim API."""
    params = {'q': address, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'YourAppName/1.0'}  # Replace 'YourAppName/1.0' with your actual app name
    response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

# Load the original CSV
df = pd.read_csv('LinkedIn Job Scraper _by Search_(1).csv')

# Remove duplicates for efficiency
unique_locations = df['Job_location'].unique()

# Prepare a dictionary to map locations to coordinates
location_coords = {}
for location in tqdm(unique_locations):  # tqdm is optional, for progress indication
    if location and location != 'Unknown':  # Check if location is not NaN or 'Unknown'
        lat, lon = get_location(location)
        location_coords[location] = (lat, lon)
    else:
        location_coords[location] = (None, None)

# Map coordinates back to the original DataFrame
df['Latitude'] = df['Job_location'].apply(lambda x: location_coords[x][0] if x in location_coords else None)
df['Longitude'] = df['Job_location'].apply(lambda x: location_coords[x][1] if x in location_coords else None)

# Save the enhanced DataFrame
df.to_csv('Enhanced_LinkedIn_Job_Listings.csv', index=False)
