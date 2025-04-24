#!/usr/bin/env python3
"""
Interactive Sidereal Astrological Calculator

This script interactively calculates sidereal ascendant and houses for a birth time and location.
It uses:
- pyswisseph for astronomical calculations
- OpenCage for geocoding
- timezonefinder + pytz for timezone handling
"""

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

# OpenCage API Key
OPENCAGE_API_KEY = "e1f13894399d48c7bdfe76c245a5568f"

def get_user_input():
    """Get birth details from user input."""
    print("\n===== Birth Details Input =====\n")
    
    # Get birth date
    while True:
        date_str = input("Enter birth date (YYYY-MM-DD): ")
        try:
            # Validate date format
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    
    # Get birth time
    while True:
        time_str = input("Enter birth time (HH:MM): ")
        try:
            # Validate time format
            datetime.datetime.strptime(time_str, "%H:%M")
            break
        except ValueError:
            print("Invalid time format. Please use HH:MM (24-hour format).")
    
    # Get location
    city = input("Enter birth city: ")
    country = input("Enter birth country: ")
    
    return date_str, time_str, city, country

def get_coordinates(city, country):
    """Get latitude and longitude for a location using OpenCage Geocoding API."""
    print("\n===== Geocoding Location =====\n")
    
    url = "https://api.opencagedata.com/geocode/v1/json"
    query = f"{city}, {country}"
    
    params = {
        "q": query,
        "key": OPENCAGE_API_KEY,
        "limit": 1,
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code != 200 or len(data["results"]) == 0:
            print(f"Error: Could not geocode location '{query}'")
            print(f"Response: {data}")
            return None, None
        
        location = data["results"][0]["geometry"]
        formatted_location = data["results"][0]["formatted"]
        print(f"Found location: {formatted_location}")
        
        return location["lat"], location["lng"]
    
    except Exception as e:
        print(f"Error connecting to geocoding service: {e}")
        return None, None

def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates using timezonefinder."""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    
    if not timezone_str:
        print(f"Error: Could not determine timezone for coordinates: {latitude}, {longitude}")
        return None
        
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
        second = 0  # Default seconds to 0
        
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
        return None

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
    # Ensure longitude is within 0-360 range
    longitude = longitude % 360
    
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
    print("\n===== Calculating Astrological Data =====\n")
    
    # Set the ephemeris path
    ephe_path = os.path.join(os.getcwd(), "ephe")
    if os.path.exists(ephe_path):
        swe.set_ephe_path(ephe_path)
        print(f"Using ephemeris files from: {ephe_path}")
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

def calculate_planets(jd):
    """Calculate positions of major planets using Swiss Ephemeris."""
    # Dictionary of planets with their Swiss Ephemeris IDs
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }
    
    # Get ayanamsa
    ayanamsa = swe.get_ayanamsa(jd)
    
    results = []
    
    # Calculate each planet
    for planet_name, planet_id in planets.items():
        # Calculate planet position
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        ret, result = swe.calc_ut(jd, planet_id, flags)
        
        # Extract longitude and speed
        longitude = result[0]
        speed = result[3]  # daily speed in longitude
        
        # Convert tropical to sidereal
        sidereal_longitude = longitude - ayanamsa
        if sidereal_longitude < 0:
            sidereal_longitude += 360
        
        # Determine if planet is retrograde
        is_retrograde = speed < 0
        
        # Add to results
        results.append({
            "name": planet_name,
            "longitude": sidereal_longitude,
            "formatted": format_longitude(sidereal_longitude),
            "retrograde": is_retrograde
        })
    
    # Calculate North Node (Rahu) and South Node (Ketu)
    flags = swe.FLG_SWIEPH
    ret, result = swe.calc_ut(jd, swe.MEAN_NODE, flags)
    
    # True North Node (Rahu)
    rahu_longitude = result[0] - ayanamsa
    if rahu_longitude < 0:
        rahu_longitude += 360
    
    # South Node (Ketu) is 180° opposite to North Node
    ketu_longitude = (rahu_longitude + 180) % 360
    
    results.append({
        "name": "Rahu (North Node)",
        "longitude": rahu_longitude,
        "formatted": format_longitude(rahu_longitude),
        "retrograde": False
    })
    
    results.append({
        "name": "Ketu (South Node)",
        "longitude": ketu_longitude,
        "formatted": format_longitude(ketu_longitude),
        "retrograde": False
    })
    
    return results

def main():
    """Main function to run the script."""
    print("\n============================")
    print("SIDEREAL ASTROLOGICAL CALCULATOR")
    print("============================\n")
    print("This program calculates sidereal ascendant, houses, and planetary positions")
    print("using Swiss Ephemeris with the Lahiri ayanamsa.\n")
    
    # Step 1: Get user input
    date_str, time_str, city, country = get_user_input()
    
    # Step 2: Get coordinates
    latitude, longitude = get_coordinates(city, country)
    if latitude is None or longitude is None:
        print("Error: Could not determine coordinates. Exiting.")
        return
    
    print(f"Coordinates: {latitude}, {longitude}")
    
    # Step 3: Get timezone
    timezone_str = get_timezone_from_coordinates(latitude, longitude)
    if timezone_str is None:
        print("Error: Could not determine timezone. Exiting.")
        return
    
    print(f"Timezone: {timezone_str}")
    
    # Step 4: Convert to UTC
    utc_datetime = local_to_utc(date_str, time_str, timezone_str)
    if utc_datetime is None:
        print("Error: Could not convert to UTC. Exiting.")
        return
    
    # Step 5: Calculate Julian Day
    jd = calculate_julian_day(utc_datetime)
    
    # Step 6: Calculate houses and ascendant
    result = calculate_houses_and_ascendant(jd, latitude, longitude)
    
    # Step 7: Calculate planets
    planets = calculate_planets(jd)
    
    # Step 8: Print the results
    print("\n===== ASTROLOGICAL CHART RESULTS =====\n")
    print(f"Birth Details: {date_str} {time_str}, {city}, {country}")
    print(f"Coordinates: {latitude}, {longitude}")
    print(f"Timezone: {timezone_str}")
    print(f"\nTropical Ascendant: {format_longitude(result['tropical_ascendant'])}")
    print(f"Sidereal Ascendant (Lahiri): {result['ascendant_formatted']}")
    
    print("\nHouses (Whole Sign System, Sidereal):")
    for house in result["houses"]:
        print(f"House {house['house_num']}: {house['formatted']}")
    
    print("\nPlanets (Sidereal, Lahiri Ayanamsa):")
    for planet in planets:
        retrograde_symbol = " (R)" if planet["retrograde"] else ""
        print(f"{planet['name']}: {planet['formatted']}{retrograde_symbol}")

if __name__ == "__main__":
    main()