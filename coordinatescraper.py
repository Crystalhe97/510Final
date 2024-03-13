import requests
from db import get_db_conn

def fetch_job_locations():
    """Fetch job locations from the database."""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT my_row_id, Job_location FROM newtable WHERE latitude IS NULL OR longitude IS NULL")
    job_locations = cursor.fetchall()
    cursor.close()
    conn.close()
    return job_locations

def fetch_geolocation(location_name):
    """Fetch geolocation (latitude and longitude) for a given location name."""
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'JobLocationScraper 1.0'
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return {
                'latitude': data[0]['lat'],
                'longitude': data[0]['lon']
            }
    return None

def update_job_location_with_coordinates(my_row_id, latitude, longitude):
    """Update the job location with latitude and longitude in the database."""
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE newtable SET latitude = %s, longitude = %s WHERE my_row_id = %s", (latitude, longitude, my_row_id))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    job_locations = fetch_job_locations()
    for my_row_id, location in job_locations:
        geolocation = fetch_geolocation(location)
        if geolocation:
            update_job_location_with_coordinates(my_row_id, geolocation['latitude'], geolocation['longitude'])

if __name__ == "__main__":
    main()
