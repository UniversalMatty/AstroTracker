import requests
import logging
import os

def get_coordinates(city, country):
    """
    Get latitude and longitude for a given city and country using OpenCage Geocoding API.
    Returns a tuple of (longitude, latitude) or None if the coordinates couldn't be determined.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("OPENCAGE_KEY")
        if not api_key:
            logging.error("OPENCAGE_KEY environment variable not set")
            return None
            
        # Construct the query
        query = f"{city}, {country}"
        
        # Using OpenCage API for geocoding
        url = "https://api.opencagedata.com/geocode/v1/json"
        
        params = {
            "q": query,
            "key": api_key,
            "limit": 1,
            "no_annotations": 1
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data and data['results'] and len(data['results']) > 0:
            result = data['results'][0]
            latitude = float(result['geometry']['lat'])
            longitude = float(result['geometry']['lng'])
            logging.debug(f"Found coordinates for {query}: {longitude}, {latitude}")
            return (longitude, latitude)
        else:
            logging.warning(f"No coordinates found for {query}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting coordinates: {str(e)}")
        return None
