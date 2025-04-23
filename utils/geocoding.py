import requests
import logging
import os

def get_coordinates(city, country):
    """
    Get latitude and longitude for a given city and country using an external geocoding service.
    Returns a tuple of (longitude, latitude) or None if the coordinates couldn't be determined.
    """
    try:
        # Construct the query
        query = f"{city}, {country}"
        
        # Using OpenStreetMap Nominatim API for geocoding
        # Note: In production, you should use a proper API key-based service with better rate limits
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
        
        headers = {
            "User-Agent": "AstrologyCalculator/1.0"  # Required by Nominatim
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            latitude = float(data[0]['lat'])
            longitude = float(data[0]['lon'])
            logging.debug(f"Found coordinates for {query}: {longitude}, {latitude}")
            return (longitude, latitude)
        else:
            logging.warning(f"No coordinates found for {query}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting coordinates: {str(e)}")
        return None
