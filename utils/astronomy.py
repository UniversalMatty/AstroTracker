import ephem
import math
from datetime import datetime
import logging
from ephemerides_data import get_ephemerides_for_date

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
# Using Lahiri ayanamsa (Indian standard)
# The Lahiri ayanamsa increases by approximately 50.3 seconds per year
AYANAMSA = 23.85  # Default value (will be dynamically calculated)

def calculate_lahiri_ayanamsa(date_str):
    """
    Calculate the Lahiri ayanamsa for a given date.
    The Lahiri ayanamsa was approximately 23°15' on Jan 1, 1950,
    and increases by about 50.3 seconds per year.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        The Lahiri ayanamsa value in degrees for the given date
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Reference: Lahiri ayanamsa was 23.15 degrees on January 1, 1950
        reference_date = datetime(1950, 1, 1)
        reference_ayanamsa = 23.15
        
        # Calculate years since reference date
        years_diff = (dt - reference_date).days / 365.25
        
        # Ayanamsa increases by about 50.3 seconds of arc per year
        # Convert to degrees: 50.3 seconds = 50.3/3600 degrees
        increase = years_diff * (50.3 / 3600)
        
        # Calculate current ayanamsa
        ayanamsa = reference_ayanamsa + increase
        
        return ayanamsa
    except Exception as e:
        logging.error(f"Error calculating Lahiri ayanamsa: {str(e)}")
        # Return the default value if calculation fails
        return 23.85  # Default value

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

def calculate_planet_positions(date_str, time_str, longitude, latitude, ephemerides_data=None, use_calibration=False):
    """
    Calculate planetary positions for a given date, time, and location.
    Uses sidereal calculations for accurate astrological readings.
    
    Parameters:
    - date_str: Date string in YYYY-MM-DD format
    - time_str: Time string in HH:MM format
    - longitude: Geographic longitude in decimal degrees
    - latitude: Geographic latitude in decimal degrees
    - ephemerides_data: Optional ephemerides data to use instead of PyEphem calculations
    - use_calibration: Whether to use a special calibration to match reference charts
    
    Returns a list of dictionaries with planetary data
    """
    try:
        planets_data = []
        
        # First try using Swiss Ephemeris for more accurate calculations
        try:
            from utils.swisseph import (
                calculate_jd_ut, 
                calculate_planet_position, 
                calculate_lunar_nodes,
                get_zodiac_sign,
                calculate_ayanamsa,
                tropical_to_sidereal
            )
            import swisseph as swe
            
            # Get Julian Day
            jd_ut = calculate_jd_ut(date_str, time_str)
            
            # Get the ayanamsa value for this date
            krishnamurti_ayanamsa = calculate_ayanamsa(jd_ut)
            logging.debug(f"Krishnamurti ayanamsa for {date_str}: {krishnamurti_ayanamsa:.4f}°")
            
            # Define planet IDs and their names
            # Using direct values instead of constants:
            # Sun=0, Moon=1, Mercury=2, Venus=3, Mars=4, Jupiter=5, Saturn=6, Uranus=7, Neptune=8, Pluto=9
            planet_info = {
                0: "Sun",
                1: "Moon",
                2: "Mercury",
                3: "Venus",
                4: "Mars",
                5: "Jupiter",
                6: "Saturn",
                7: "Uranus",
                8: "Neptune",
                9: "Pluto"
            }
            
            # Calculate positions for each planet
            for planet_id, planet_name in planet_info.items():
                try:
                    tropical_longitude, sidereal_longitude, retrograde = calculate_planet_position(planet_id, jd_ut)
                    
                    # Double-check sidereal longitude by doing direct conversion (for maximum accuracy)
                    verified_sidereal = tropical_to_sidereal(tropical_longitude, jd_ut)
                    
                    # Use the verified sidereal value
                    sidereal_longitude = verified_sidereal
                    
                    # Get zodiac sign and position within sign
                    sign = get_zodiac_sign(sidereal_longitude)
                    degree_in_sign = sidereal_longitude % 30
                    
                    # Format degrees in DMS format for display
                    degree_int = int(degree_in_sign)
                    minutes_float = (degree_in_sign - degree_int) * 60
                    minutes_int = int(minutes_float)
                    seconds_int = int((minutes_float - minutes_int) * 60)
                    
                    # For display, show degrees, minutes, and seconds
                    formatted_dms = f"{sign} {degree_int}° {minutes_int}' {seconds_int}\""
                    
                    planet_data = {
                        "name": planet_name,
                        "longitude": sidereal_longitude,
                        "sign": sign,
                        "retrograde": retrograde,
                        "formatted_position": formatted_dms + ('R' if retrograde else '')
                    }
                    
                    planets_data.append(planet_data)
                    
                except Exception as e:
                    logging.error(f"Error calculating {planet_name} position: {str(e)}")
                    continue
            
            # Calculate Lunar Nodes (Rahu and Ketu)
            try:
                rahu_longitude, ketu_longitude = calculate_lunar_nodes(jd_ut)
                
                # Rahu (North Node)
                rahu_sign = get_zodiac_sign(rahu_longitude)
                rahu_degree = rahu_longitude % 30
                
                # Format DMS for Rahu
                rahu_degree_int = int(rahu_degree)
                rahu_minutes_float = (rahu_degree - rahu_degree_int) * 60
                rahu_minutes_int = int(rahu_minutes_float)
                rahu_seconds_int = int((rahu_minutes_float - rahu_minutes_int) * 60)
                
                rahu_data = {
                    "name": "Rahu",
                    "longitude": rahu_longitude,
                    "sign": rahu_sign,
                    "retrograde": True,  # Rahu is always considered retrograde in Vedic astrology
                    "formatted_position": f"{rahu_sign} {rahu_degree_int}° {rahu_minutes_int}' {rahu_seconds_int}\"R"
                }
                
                # Ketu (South Node)
                ketu_sign = get_zodiac_sign(ketu_longitude)
                ketu_degree = ketu_longitude % 30
                
                # Format DMS for Ketu
                ketu_degree_int = int(ketu_degree)
                ketu_minutes_float = (ketu_degree - ketu_degree_int) * 60
                ketu_minutes_int = int(ketu_minutes_float)
                ketu_seconds_int = int((ketu_minutes_float - ketu_minutes_int) * 60)
                
                ketu_data = {
                    "name": "Ketu",
                    "longitude": ketu_longitude,
                    "sign": ketu_sign,
                    "retrograde": True,  # Ketu is always considered retrograde in Vedic astrology
                    "formatted_position": f"{ketu_sign} {ketu_degree_int}° {ketu_minutes_int}' {ketu_seconds_int}\"R"
                }
                
                planets_data.append(rahu_data)
                planets_data.append(ketu_data)
                
            except Exception as e:
                logging.error(f"Error calculating lunar nodes: {str(e)}")
            
            # Return the Swiss Ephemeris results if we got this far
            if planets_data:
                logging.debug("Using Swiss Ephemeris for planetary calculations")
                return planets_data
                
        except Exception as swiss_error:
            # If Swiss Ephemeris fails, log the error and fall back to ephemerides data or PyEphem
            logging.warning(f"Swiss Ephemeris calculation failed: {str(swiss_error)}. Falling back to database or PyEphem.")
        
        # Reset planets data for fallback methods
        planets_data = []
        
        # First check if we have ephemerides data in our database
        db_ephemerides = get_ephemerides_for_date(date_str)
        if db_ephemerides:
            logging.debug(f"Using ephemerides from database for date: {date_str}")
            ephemerides_data = db_ephemerides
            
        # If we have ephemerides data (from parameter or database), use it
        if ephemerides_data:
            # Set retrograde status for specific planets in the ephemerides
            # In Vedic astrology, these planets are typically considered retrograde
            retrograde_planets = {
                "Jupiter": True,
                "Saturn": True, 
                "Mercury": False,
                "Venus": False,
                "Mars": False
            }
            
            # Process each planet from the ephemerides
            for planet_name, longitude in ephemerides_data.items():
                # Default retrograde to False (Sun, Moon, Rahu, Ketu are never retrograde)
                retrograde = False
                
                # For traditional planets, use our retrograde mapping
                if planet_name in retrograde_planets:
                    retrograde = retrograde_planets[planet_name]

                # Format the data
                planets_data.append({
                    'name': planet_name,
                    'longitude': longitude,
                    'formatted_position': format_longitude(longitude),
                    'sign': get_zodiac_sign(longitude),
                    'retrograde': retrograde
                })
                
            # Return early if we're using ephemerides data
            logging.debug(f"Using ephemerides data for planets: {list(ephemerides_data.keys())}")
            return planets_data
        
        # If we don't have ephemerides data, calculate using PyEphem
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
        
        # Calculate the dynamic Lahiri ayanamsa for the birth date
        dynamic_ayanamsa = calculate_lahiri_ayanamsa(date_str)
        logging.debug(f"Using dynamic Lahiri ayanamsa: {dynamic_ayanamsa} for date {date_str}")
        
        # Calculate position for each planet
        for planet_name, planet_obj in PLANETS.items():
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
            sidereal_longitude = (longitude - dynamic_ayanamsa) % 360
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
                
                # Apply sidereal correction using the same dynamic ayanamsa
                tomorrow_longitude = (tomorrow_longitude - dynamic_ayanamsa) % 360
                
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
            
        # Calculate North Node (Rahu) and South Node (Ketu)
        try:
            # We can access moon orbital elements to get the North Node position
            # The mean ascending node of the Moon's orbit is needed for Rahu
            # Reference: http://www.stjarnhimlen.se/comp/ppcomp.html#19
            
            # Get the current Julian date
            jd = ephem.julian_date(observer.date)
            
            # Calculate the position of the Moon's mean ascending node
            # Simplified formula from astronomical algorithms
            # Mean ecliptic longitude of ascending node: 
            T = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000
            # Mean ecliptic longitude of ascending node (degrees)
            N = 125.04452 - 1934.136261 * T + 0.0020708 * T**2 + T**3 / 450000.0
            # Normalize to 0-360 degrees
            N = N % 360
            
            # Convert to sidereal by applying ayanamsa
            rahu_longitude = (N - dynamic_ayanamsa) % 360
            
            # Ketu (South Node) is always 180° opposite to Rahu
            ketu_longitude = (rahu_longitude + 180) % 360
            
            # Add Rahu and Ketu to the results
            planets_data.append({
                'name': 'Rahu',
                'longitude': rahu_longitude,
                'formatted_position': format_longitude(rahu_longitude),
                'sign': get_zodiac_sign(rahu_longitude),
                'retrograde': True  # Nodes are traditionally considered retrograde
            })
            
            planets_data.append({
                'name': 'Ketu',
                'longitude': ketu_longitude,
                'formatted_position': format_longitude(ketu_longitude),
                'sign': get_zodiac_sign(ketu_longitude),
                'retrograde': True  # Nodes are traditionally considered retrograde
            })
            
            logging.debug(f"Calculated Rahu at {rahu_longitude} degrees ({get_zodiac_sign(rahu_longitude)})")
            logging.debug(f"Calculated Ketu at {ketu_longitude} degrees ({get_zodiac_sign(ketu_longitude)})")
            
        except Exception as e:
            logging.error(f"Error calculating lunar nodes: {str(e)}")
        
        return planets_data
        
    except Exception as e:
        logging.error(f"Error calculating planet positions: {str(e)}")
        raise
