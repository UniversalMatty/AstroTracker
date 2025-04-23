import ephem
import math
from datetime import datetime
import logging

# Planets and their corresponding PyEphem objects
PLANETS = {
    'Sun': ephem.Sun(),
    'Moon': ephem.Moon(),
    'Mercury': ephem.Mercury(),
    'Venus': ephem.Venus(),
    'Mars': ephem.Mars(),
    'Jupiter': ephem.Jupiter(),
    'Saturn': ephem.Saturn(),
    'Uranus': ephem.Uranus(),
    'Neptune': ephem.Neptune(),
    'Pluto': ephem.Pluto()
}

# Ayanamsa (precession correction) for sidereal calculations
# Using Lahiri ayanamsa as a default
# The value changes slightly each year (about 1 degree every 72 years)
# For 1990s-2020s, it's approximately 23.85 degrees (as of 2023)
AYANAMSA = 23.85  # Lahiri Ayanamsa for current era

def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds format"""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return d, m, s

def get_zodiac_sign(longitude):
    """Get zodiac sign from longitude in degrees"""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio", 
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_index = int(longitude / 30)
    return signs[sign_index % 12]

def format_longitude(longitude):
    """Format longitude in degrees to a human-readable format with zodiac sign"""
    sign = get_zodiac_sign(longitude)
    pos_in_sign = longitude % 30
    d, m, s = degrees_to_dms(pos_in_sign)
    return f"{sign} {d}° {m}' {int(s)}\""

def calculate_planet_positions(date_str, time_str, longitude, latitude, ephemerides_data=None):
    """
    Calculate planetary positions for a given date, time, and location.
    Uses sidereal calculations for accurate astrological readings.
    
    Parameters:
    - date_str: Date string in YYYY-MM-DD format
    - time_str: Time string in HH:MM format
    - longitude: Geographic longitude in decimal degrees
    - latitude: Geographic latitude in decimal degrees
    - ephemerides_data: Optional ephemerides data to use instead of PyEphem calculations
    
    Returns a list of dictionaries with planetary data
    """
    try:
        # Create observer object with location data
        observer = ephem.Observer()
        observer.lon = str(longitude)
        observer.lat = str(latitude)
        
        # Parse date and time
        if time_str:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            dt = datetime.strptime(f"{date_str} 12:00", "%Y-%m-%d %H:%M")  # Noon if no time provided
        
        observer.date = dt.strftime("%Y/%m/%d %H:%M:%S")
        
        planets_data = []
        
        # Calculate position for each planet
        for planet_name, planet_obj in PLANETS.items():
            # Check if we have custom ephemerides data for this planet
            if ephemerides_data and planet_name in ephemerides_data:
                # Use provided ephemerides data
                longitude = float(ephemerides_data[planet_name])
                
                # Assume retrograde status from ephemerides if available
                retrograde = ephemerides_data.get(f"{planet_name}_retrograde", False)
            else:
                # Calculate using PyEphem
                planet_obj.compute(observer)
                
                # Get longitude in degrees - use ecliptic longitude (lon) instead of hlon
                # hlon is not a standard attribute in ephem objects
                logging.debug(f"Calculating position for: {planet_name}")
                
                # Check available attributes on the planet object
                if hasattr(planet_obj, 'a_ra'):
                    ra = planet_obj.a_ra
                    logging.debug(f"{planet_name} a_ra: {math.degrees(ra)}")
                if hasattr(planet_obj, 'g_ra'):
                    ra = planet_obj.g_ra
                    logging.debug(f"{planet_name} g_ra: {math.degrees(ra)}")
                if hasattr(planet_obj, 'ra'):
                    ra = planet_obj.ra
                    logging.debug(f"{planet_name} ra: {math.degrees(ra)}")
                
                # Get ecliptic longitude from equatorial coordinates
                # PyEphem doesn't directly provide ecliptic longitude for planets
                # We need to convert from right ascension (RA) and declination to ecliptic longitude
                
                # Convert equatorial coordinates to ecliptic
                ecl = ephem.Ecliptic(planet_obj.ra, planet_obj.dec)
                longitude = math.degrees(ecl.lon)
                logging.debug(f"{planet_name} ecliptic longitude (raw): {longitude}")
                
                # Adjust for sidereal calculation by subtracting ayanamsa
                sidereal_longitude = (longitude - AYANAMSA) % 360
                logging.debug(f"{planet_name} tropical: {longitude}, sidereal: {sidereal_longitude}, sign: {get_zodiac_sign(sidereal_longitude)}")
                longitude = sidereal_longitude
                
                # Determine if planet is retrograde (except Sun and Moon)
                retrograde = False
                if planet_name not in ["Sun", "Moon"]:
                    # A simple way to detect retrograde is to check the planet's position a day later
                    observer_tomorrow = ephem.Observer()
                    observer_tomorrow.lon = observer.lon
                    observer_tomorrow.lat = observer.lat
                    
                    # Add one day to the current date
                    current_date = ephem.Date(observer.date)
                    observer_tomorrow.date = ephem.Date(current_date + 1)
                    
                    planet_obj_copy = getattr(ephem, planet_name)()
                    planet_obj_copy.compute(observer_tomorrow)
                    
                    # Get tomorrow's longitude using the same method as current day
                    # Convert equatorial coordinates to ecliptic
                    ecl_tomorrow = ephem.Ecliptic(planet_obj_copy.ra, planet_obj_copy.dec)
                    tomorrow_longitude = math.degrees(ecl_tomorrow.lon)
                    logging.debug(f"{planet_name} tomorrow's ecliptic longitude (raw): {tomorrow_longitude}")
                    
                    # Apply sidereal correction
                    tomorrow_longitude = (tomorrow_longitude - AYANAMSA) % 360
                    
                    logging.debug(f"{planet_name} tomorrow: {tomorrow_longitude}, today: {longitude}")
                    
                    # If longitude tomorrow is less than today (accounting for 0/360 boundary)
                    if (tomorrow_longitude < longitude and 
                        abs(tomorrow_longitude - longitude) < 180) or \
                       (tomorrow_longitude > longitude and 
                        abs(tomorrow_longitude - longitude) > 180):
                        retrograde = True
                        logging.debug(f"{planet_name} is RETROGRADE")
            
            # Format the data
            planets_data.append({
                'name': planet_name,
                'longitude': longitude,
                'formatted_position': format_longitude(longitude),
                'sign': get_zodiac_sign(longitude),
                'retrograde': retrograde
            })
        
        return planets_data
        
    except Exception as e:
        logging.error(f"Error calculating planet positions: {str(e)}")
        raise
