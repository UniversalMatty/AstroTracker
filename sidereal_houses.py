#!/usr/bin/env python3
"""
Sidereal Houses Calculator

This script calculates sidereal ascendant and houses for a given birth time and location.
It uses pyswisseph for astronomical calculations, OpenCage for geocoding,
and timezonefinder + pytz for timezone handling.

Requirements:
- pyswisseph
- timezonefinder
- pytz
- requests
"""

import sys
import os
import datetime
import requests
import swisseph as swe
import pytz
from timezonefinder import TimezoneFinder

# Constants
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", 
    "Leo", "Virgo", "Libra", "Scorpio", 
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_coordinates(city, country, api_key):
    """Get latitude and longitude for a location using OpenCage Geocoding API."""
    url = "https://api.opencagedata.com/geocode/v1/json"
    query = f"{city}, {country}"
    
    params = {
        "q": query,
        "key": api_key,
        "limit": 1,
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code != 200 or len(data["results"]) == 0:
        print(f"Error: Could not geocode location '{query}'")
        print(f"Response: {data}")
        sys.exit(1)
    
    location = data["results"][0]["geometry"]
    formatted_location = data["results"][0]["formatted"]
    print(f"Found location: {formatted_location}")
    
    return location["lat"], location["lng"]

def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates using timezonefinder."""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    
    if not timezone_str:
        print(f"Error: Could not determine timezone for coordinates: {latitude}, {longitude}")
        sys.exit(1)
        
    return timezone_str

def local_to_utc(date_str, time_str, timezone_str):
    """Convert local time to UTC using pytz."""
    try:
        # Parse the date and time strings
        date_parts = [int(x) for x in date_str.split('-')]
        time_parts = [int(x) for x in time_str.split(':')]
        
        if len(date_parts) != 3 or len(time_parts) < 2:
            raise ValueError("Invalid date or time format")
            
        year, month, day = date_parts
        hour, minute = time_parts[0], time_parts[1]
        second = time_parts[2] if len(time_parts) > 2 else 0
        
        # Create datetime object in the local timezone
        local_timezone = pytz.timezone(timezone_str)
        local_datetime = local_timezone.localize(
            datetime.datetime(year, month, day, hour, minute, second)
        )
        
        # Convert to UTC
        utc_datetime = local_datetime.astimezone(pytz.UTC)
        
        print(f"Local time: {local_datetime}")
        print(f"UTC time: {utc_datetime}")
        
        return utc_datetime
        
    except Exception as e:
        print(f"Error converting time to UTC: {e}")
        sys.exit(1)

def calculate_julian_day(utc_datetime):
    """Calculate Julian Day for the given UTC datetime."""
    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day
    hour = utc_datetime.hour
    minute = utc_datetime.minute
    second = utc_datetime.second
    
    # Calculate Julian day using Swiss Ephemeris
    jd = swe.julday(year, month, day, hour + minute/60.0 + second/3600.0)
    
    print(f"Julian Day: {jd}")
    return jd

def format_longitude(longitude):
    """Format longitude in degrees to zodiac sign and degrees."""
    sign_num = int(longitude / 30) % 12
    sign_deg = longitude % 30
    
    sign_name = ZODIAC_SIGNS[sign_num]
    return f"{sign_name} {sign_deg:.2f}°"

def calculate_houses_and_ascendant(jd, latitude, longitude):
    """
    Calculate house cusps and ascendant using Swiss Ephemeris.
    
    Args:
        jd: Julian Day number
        latitude: Geographic latitude in decimal degrees
        longitude: Geographic longitude in decimal degrees
        
    Returns:
        Dictionary with ascendant and houses information
    """
    # Set the ephemeris path
    ephe_path = os.path.join(os.getcwd(), "ephe")
    if os.path.exists(ephe_path):
        swe.set_ephe_path(ephe_path)
    else:
        print(f"Warning: Ephemeris path not found at {ephe_path}")
        swe.set_ephe_path()  # Use default path
    
    # Set ayanamsa to Lahiri
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Get the ayanamsa value (precession correction)
    ayanamsa = swe.get_ayanamsa(jd)
    print(f"Ayanamsa (Lahiri): {ayanamsa:.6f}°")
    
    # Calculate houses in tropical zodiac first
    # Using Placidus house system ('P') for accurate ascendant calculation
    houses_cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
    
    # Extract the ascendant from ascmc[0]
    tropical_ascendant = ascmc[0]
    
    # Convert tropical ascendant to sidereal
    sidereal_ascendant = tropical_ascendant - ayanamsa
    if sidereal_ascendant < 0:
        sidereal_ascendant += 360
    
    # For whole sign houses, each house cusp is 30° apart, starting from the ascendant sign
    asc_sign_num = int(sidereal_ascendant / 30)
    whole_sign_houses = []
    
    for i in range(12):
        house_num = (asc_sign_num + i) % 12
        house_cusp = house_num * 30.0
        whole_sign_houses.append(house_cusp)
    
    # Prepare the result
    result = {
        "tropical_ascendant": tropical_ascendant,
        "sidereal_ascendant": sidereal_ascendant,
        "ascendant_formatted": format_longitude(sidereal_ascendant),
        "houses": []
    }
    
    # Format the houses
    for i, cusp in enumerate(whole_sign_houses):
        house_num = i + 1
        result["houses"].append({
            "house_num": house_num,
            "longitude": cusp,
            "formatted": format_longitude(cusp)
        })
    
    return result

def main():
    """Main function to run the script."""
    if len(sys.argv) < 6:
        print("Usage: python sidereal_houses.py <date> <time> <city> <country> <api_key>")
        print("Example: python sidereal_houses.py 1990-01-01 12:30 London 'United Kingdom' your_api_key_here")
        sys.exit(1)
    
    date_str = sys.argv[1]  # Format: YYYY-MM-DD
    time_str = sys.argv[2]  # Format: HH:MM or HH:MM:SS
    city = sys.argv[3]
    country = sys.argv[4]
    api_key = sys.argv[5]  # OpenCage API key
    
    print(f"\n===== Calculating for {date_str} {time_str}, {city}, {country} =====\n")
    
    # Step 1: Get coordinates using OpenCage
    latitude, longitude = get_coordinates(city, country, api_key)
    print(f"Coordinates: {latitude}, {longitude}")
    
    # Step 2: Get timezone for the location
    timezone_str = get_timezone_from_coordinates(latitude, longitude)
    print(f"Timezone: {timezone_str}")
    
    # Step 3: Convert local time to UTC
    utc_datetime = local_to_utc(date_str, time_str, timezone_str)
    
    # Step 4: Calculate Julian Day
    jd = calculate_julian_day(utc_datetime)
    
    # Step 5: Calculate houses and ascendant
    result = calculate_houses_and_ascendant(jd, latitude, longitude)
    
    # Step 6: Print the results
    print("\n===== RESULTS =====\n")
    print(f"Tropical Ascendant: {format_longitude(result['tropical_ascendant'])}")
    print(f"Sidereal Ascendant (Lahiri): {result['ascendant_formatted']}")
    
    print("\nHouses (Whole Sign System, Sidereal):")
    for house in result["houses"]:
        print(f"House {house['house_num']}: {house['formatted']}")

if __name__ == "__main__":
    main()