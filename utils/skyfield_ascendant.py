"""
Skyfield-based ascendant and houses calculator.
Uses the skyfield library for accurate astronomical calculations.
"""
import logging
from datetime import datetime
import pytz
from utils.utils import get_lahiri_ayanamsa
from skyfield.api import load, Topos
import numpy as np
from skyfield.constants import ERAD

# Initialize empty variables (will be set in the try block)
eph = None
ts = None

# Load the ephemeris data (de440s.bsp)
try:
    eph = load('de440s.bsp')
    ts = load.timescale()
    logging.info("Successfully loaded Skyfield ephemeris (de440s.bsp)")
except Exception as e:
    logging.error(f"Failed to load Skyfield ephemeris: {str(e)}")
    # Set default values that will cause failures to be handled properly
    from skyfield.api import load
    eph = {}
    ts = load.timescale()
    
def get_zodiac_sign(longitude):
    """Get zodiac sign from longitude in degrees (0-360)"""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio", 
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_index = int(longitude / 30) % 12
    return signs[sign_index]

def format_longitude_dms(longitude):
    """Format longitude in degrees, minutes, and seconds (DMS)."""
    # Normalize longitude to 0-360 range
    longitude = longitude % 360
    
    # Determine zodiac sign
    sign = get_zodiac_sign(longitude)
    
    # Calculate degrees, minutes, and seconds within sign
    degrees_in_sign = longitude % 30
    degree_int = int(degrees_in_sign)
    
    # Calculate minutes
    minutes_float = (degrees_in_sign - degree_int) * 60
    minutes_int = int(minutes_float)
    
    # Calculate seconds
    seconds_float = (minutes_float - minutes_int) * 60
    seconds_int = int(seconds_float)
    
    # Format the result: "Sign degrees°minutes'seconds""
    return f"{sign} {degree_int}°{minutes_int}'{seconds_int}\""



def calculate_ascendant(t, observer):
    """
    Calculate the ascendant (rising sign) using Skyfield.
    
    Args:
        t: Skyfield Time object
        observer: Skyfield Topos object for the observer's location
        
    Returns:
        Tropical longitude of the ascendant in degrees
    """
    try:
        # Get the observer's position
        earth = eph['earth']
        observer_position = earth + observer
        
        # Calculate Local Sidereal Time (LST)
        lst = t.gast # Greenwich Apparent Sidereal Time
        
        # Convert LST to degrees (from hours)
        lst_degrees = lst * 15.0
        
        # Calculate observer's longitude
        observer_longitude = float(observer.longitude.degrees)
        
        # Local Sidereal Time at the observer's location
        local_lst_degrees = (lst_degrees + observer_longitude) % 360
        
        # Calculate the RAMC (Right Ascension of the Midheaven)
        # RAMC = local LST
        ramc = local_lst_degrees
        
        # Calculate the obliquity of the ecliptic at this time
        earth_tilt = t.tt_calendar()[0]  # Extract the year
        obliquity = 23.4393 - 0.0000004 * (earth_tilt - 2000)
        
        # Observer's latitude in radians
        observer_latitude = float(observer.latitude.degrees) * np.pi / 180
        
        # Convert RAMC to ecliptic longitude (tropical ascendant)
        tan_ramc = np.tan(ramc * np.pi / 180)
        tan_obliquity = np.tan(obliquity * np.pi / 180)
        
        # Calculate the ecliptic longitude of the ascendant
        ascendant_radians = np.arctan2(
            np.cos(obliquity * np.pi / 180) * tan_ramc,
            np.cos(observer_latitude) * tan_obliquity + np.sin(observer_latitude) * np.sin(ramc * np.pi / 180)
        )
        
        # Convert to degrees and make positive
        ascendant_degrees = (ascendant_radians * 180 / np.pi) % 360
        
        # Print detailed debugging information
        logging.debug(f"Skyfield ascendant calculation parameters:")
        logging.debug(f"  - Observer location: {observer.latitude.degrees}°N, {observer.longitude.degrees}°E")
        logging.debug(f"  - Local Sidereal Time: {lst:.6f} hours ({local_lst_degrees:.6f}°)")
        logging.debug(f"  - Obliquity of ecliptic: {obliquity:.6f}°")
        logging.debug(f"  - Calculated tropical ascendant: {ascendant_degrees:.6f}°")
        
        return ascendant_degrees
        
    except Exception as e:
        logging.error(f"Error calculating ascendant with Skyfield: {str(e)}")
        raise

def calculate_houses_and_ascendant(date_str, time_str, latitude, longitude, timezone_str):
    """
    Calculate ascendant and houses using Skyfield.
    
    Args:
        date_str: Date string in 'YYYY-MM-DD' format
        time_str: Time string in 'HH:MM' format
        latitude: Geographic latitude in decimal degrees
        longitude: Geographic longitude in decimal degrees
        timezone_str: Timezone string (e.g., 'America/New_York')
        
    Returns:
        Dictionary with ascendant and houses information
    """
    try:
        # Parse birth date and time in the given timezone
        local_timezone = pytz.timezone(timezone_str)
        dt_str = f"{date_str} {time_str}"
        local_dt = local_timezone.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
        
        # Convert to UTC for Skyfield
        utc_dt = local_dt.astimezone(pytz.UTC)
        logging.debug(f"Local datetime: {local_dt.isoformat()}, UTC: {utc_dt.isoformat()}")
        
        # Create Skyfield time object
        t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day, 
                   utc_dt.hour, utc_dt.minute, utc_dt.second)
        
        # Create observer location
        observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
        
        # Calculate the tropical ascendant
        tropical_asc = calculate_ascendant(t, observer)
        
        # Calculate the Lahiri ayanamsa for this date
        ayanamsa = get_lahiri_ayanamsa(utc_dt)
        
        # Convert to sidereal (using Lahiri ayanamsa)
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        sidereal_asc_sign = get_zodiac_sign(sidereal_asc)
        sidereal_asc_degree = sidereal_asc % 30
        
        # Calculate houses using the Whole Sign system
        houses = []
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", 
            "Leo", "Virgo", "Libra", "Scorpio", 
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        # Find the index of the sign that contains the ascendant
        asc_sign_index = signs.index(sidereal_asc_sign)
        
        # Calculate the houses in Whole Sign system
        # The ascendant sign becomes the 1st house, and each subsequent sign becomes the next house
        for i in range(12):
            house_num = i + 1
            house_sign_index = (asc_sign_index + i) % 12
            house_sign = signs[house_sign_index]
            
            # In Whole Sign houses, each house starts at 0° of its sign
            house = {
                "house": house_num,
                "sign": house_sign,
                "degree": 0.0,
                "formatted": house_sign
            }
            
            houses.append(house)
            
        # Return all the calculation details
        result = {
            "houses": houses,
            "ascendant_longitude": sidereal_asc,
            "tropical_ascendant": tropical_asc,
            "ayanamsa": ayanamsa,
            "ascendant_sign": sidereal_asc_sign,
            "ascendant_degree": sidereal_asc_degree,
            "ascendant_formatted": format_longitude_dms(sidereal_asc),
            "calculation_method": "Skyfield (Lahiri Ayanamsa)"
        }
        
        logging.debug(f"Ascendant: {result['ascendant_formatted']}")
        logging.debug(f"Houses: {[h['formatted'] for h in houses]}")
        
        return result
        
    except Exception as e:
        logging.error(f"Error in calculate_houses_and_ascendant: {str(e)}")
        raise