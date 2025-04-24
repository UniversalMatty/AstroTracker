"""
Swiss Ephemeris-based astrological calculations.
Uses the swisseph library for accurate astronomical calculations.
"""
import os
import swisseph as swe
import logging
from datetime import datetime, timezone

# Set up Swiss Ephemeris
# Path to ephemeris files - use the root directory where SE1 files are stored
EPHE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
swe.set_ephe_path(EPHE_PATH)

# Initialize SwissEph with the correct files
try:
    # Force Swiss Ephemeris to use the .se1 files for calculations
    swe.set_ephe_path(EPHE_PATH)
    # Use Swiss Ephemeris files instead of JPL
    swe.SWISSEPH = True
    # Set the sidereal mode to Lahiri ayanamsa 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    logging.info(f"Swiss Ephemeris initialized with path: {EPHE_PATH}")
    logging.info(f"Available .se1 files: {[f for f in os.listdir(EPHE_PATH) if f.endswith('.se1')]}")
except Exception as e:
    logging.error(f"Failed to initialize Swiss Ephemeris: {str(e)}")

def calculate_jd_ut(date_str, time_str=None):
    """Calculate Julian Day (JD) in Universal Time from date and time strings"""
    try:
        if time_str:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        else:
            dt = datetime.strptime(f"{date_str} 12:00", "%Y-%m-%d %H:%M")  # Noon if no time
        
        # Convert to UTC
        dt_utc = dt.replace(tzinfo=timezone.utc)
        
        # Calculate Julian Day
        year, month, day = dt.year, dt.month, dt.day
        hour = dt.hour + dt.minute / 60.0
        
        # Use swisseph to get Julian day
        jd_ut = swe.julday(year, month, day, hour)
        
        return jd_ut
    except Exception as e:
        logging.error(f"Error calculating Julian Day: {str(e)}")
        raise

def calculate_ayanamsa(jd_ut):
    """Calculate Lahiri ayanamsa for a given Julian Day"""
    try:
        # Set to Lahiri ayanamsa mode (SIDM_LAHIRI = 1)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Get ayanamsa value for the given date
        ayanamsa = swe.get_ayanamsa(jd_ut)
        
        # For verification, calculate ayanamsa using hardcoded values
        # Lahiri ayanamsa uses 23°15' at January 1, 1950 as the reference point
        # With a rate of 50.3 seconds per year
        ref_jd = 2433282.5  # JD for January 1, 1950
        ref_ayanamsa = 23.15  # 23°15'
        seconds_per_year = 50.3 / 3600.0  # Convert to degrees
        days_per_year = 365.25
        years = (jd_ut - ref_jd) / days_per_year
        manual_ayanamsa = ref_ayanamsa + (years * seconds_per_year)
        
        logging.debug(f"Lahiri ayanamsa for JD {jd_ut}: {ayanamsa}")
        logging.debug(f"Manual approximation of Lahiri ayanamsa: {manual_ayanamsa}")
        
        # In case the swe.get_ayanamsa() fails, return our manual calculation instead
        if ayanamsa < 20 or ayanamsa > 30:  # Sanity check for reasonable values
            logging.warning(f"Suspicious ayanamsa value from Swiss Ephemeris: {ayanamsa}. Using manual calculation.")
            return manual_ayanamsa
        
        return ayanamsa
    except Exception as e:
        logging.error(f"Error calculating Lahiri ayanamsa: {str(e)}")
        # Calculate dynamically based on the Julian day
        # Using Lahiri reference values
        ref_jd = 2433282.5  # JD for January 1, 1950
        ref_ayanamsa = 23.15  # 23°15'
        seconds_per_year = 50.3 / 3600.0  # Convert to degrees
        days_per_year = 365.25
        years = (jd_ut - ref_jd) / days_per_year
        return ref_ayanamsa + (years * seconds_per_year)

def calculate_houses(jd_ut, latitude, longitude, house_system=b'W'):
    """
    Calculate house cusps and ascendant using Swiss Ephemeris.
    
    Parameters:
    - jd_ut: Julian Day in Universal Time
    - latitude: Geographic latitude in decimal degrees
    - longitude: Geographic longitude in decimal degrees
    - house_system: House system to use. Default is 'W' for Whole Sign houses.
                    Can also use 'E' for Equal Houses. No other house systems are supported.
    
    Returns a tuple of (houses, ascmc) where:
    - houses: List of house cusps
    - ascmc: List of special points (ascendant, midheaven, etc.)
    """
    try:
        # Validate house system (only Whole Sign and Equal House are supported)
        if house_system not in [b'W', b'E']:
            logging.warning(f"Unsupported house system: {house_system}. Using Whole Sign (W) instead.")
            house_system = b'W'
            
        # Calculate houses using houses_ex for more detailed data
        # Parameters:
        # jd_ut: Julian day in UT
        # lat: Latitude
        # lon: Longitude
        # hsys: House system ('W' for Whole Sign, 'E' for Equal)
        # flags: 0 for default behavior
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_system, 0)
        
        # The ascendant is the first element of ascmc
        asc_degree = ascmc[0]
        
        # First get tropical values
        tropical_asc_sign = get_zodiac_sign(asc_degree)
        tropical_degree_in_sign = asc_degree % 30
        
        # Convert to sidereal
        ayanamsa = calculate_ayanamsa(jd_ut)
        sidereal_asc = (asc_degree - ayanamsa) % 360
        sidereal_asc_sign = get_zodiac_sign(sidereal_asc)
        sidereal_degree_in_sign = sidereal_asc % 30
        
        # Log the raw values for debugging
        logging.debug(f"Swiss Ephemeris ascendant (tropical): {tropical_degree_in_sign:.2f}° {tropical_asc_sign}")
        logging.debug(f"Swiss Ephemeris ascendant (sidereal): {sidereal_degree_in_sign:.2f}° {sidereal_asc_sign}")
        
        return cusps, ascmc
    except Exception as e:
        logging.error(f"Error calculating houses with Swiss Ephemeris: {str(e)}")
        raise

def calculate_house_cusps(jd_ut, latitude, longitude):
    """
    Calculate sidereal house cusps using Swiss Ephemeris with Equal Houses.
    
    Parameters:
    - jd_ut: Julian Day in Universal Time
    - latitude: Geographic latitude in decimal degrees
    - longitude: Geographic longitude in decimal degrees
    
    Returns a dictionary with:
    - ascendant: Sidereal ascendant information
    - houses: List of house cusp information
    """
    try:
        # Always use Equal Houses (b'E') as specified
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'E', 0)
        
        # Get the ascendant (first point in ascmc)
        tropical_asc = ascmc[0]
        
        # Convert to sidereal using Lahiri ayanamsa
        ayanamsa = calculate_ayanamsa(jd_ut)
        
        # Calculate sidereal ascendant
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        sidereal_asc_sign = get_zodiac_sign(sidereal_asc)
        sidereal_asc_degree = sidereal_asc % 30
        
        # Format ascendant
        ascendant = {
            'longitude': sidereal_asc,
            'sign': sidereal_asc_sign,
            'degree': sidereal_asc_degree,
            'formatted': f"{sidereal_asc_sign} {sidereal_asc_degree:.2f}°"
        }
        
        # Calculate and format house cusps (for Equal Houses)
        houses = []
        for i in range(1, 13):  # 12 houses
            # Convert tropical cusp to sidereal
            tropical_cusp = cusps[i]
            sidereal_cusp = (tropical_cusp - ayanamsa) % 360
            sign = get_zodiac_sign(sidereal_cusp)
            degree = sidereal_cusp % 30
            
            houses.append({
                'house': i,
                'longitude': sidereal_cusp,
                'sign': sign,
                'degree': degree,
                'formatted': f"{sign} {degree:.2f}°"
            })
        
        return {
            'ascendant': ascendant,
            'houses': houses
        }
        
    except Exception as e:
        logging.error(f"Error calculating house cusps: {str(e)}")
        raise

def tropical_to_sidereal(longitude, jd_ut):
    """Convert tropical longitude to sidereal using Krishnamurti ayanamsa"""
    try:
        ayanamsa = calculate_ayanamsa(jd_ut)
        sidereal_longitude = (longitude - ayanamsa) % 360
        return sidereal_longitude
    except Exception as e:
        logging.error(f"Error converting tropical to sidereal: {str(e)}")
        raise

def calculate_planet_position(planet_id, jd_ut):
    """
    Calculate planet position using Swiss Ephemeris.
    
    Parameters:
    - planet_id: Swiss Ephemeris planet ID (e.g., swe.SUN, swe.MOON)
    - jd_ut: Julian Day in Universal Time
    
    Returns a tuple of:
    - tropical_longitude: Longitude in tropical zodiac
    - sidereal_longitude: Longitude in sidereal zodiac (Krishnamurti ayanamsa)
    - retrograde: Boolean indicating if the planet is retrograde
    """
    try:
        # First set the ephemeris to tropical mode
        swe.set_sid_mode(0)  # 0 = tropical

        # Calculate planet position - flags:
        # SEFLG_SWIEPH: Use Swiss Ephemeris (value = 2)
        # SEFLG_SPEED: Include speed calculation for retrograde detection (value = 256)
        result = swe.calc_ut(jd_ut, planet_id, 2 | 256)
        
        # The result from swe.calc_ut might be a tuple of (position_tuple, flags)
        # or just a position tuple directly, depending on the Swiss Ephemeris version
        if isinstance(result, tuple):
            if len(result) == 2 and isinstance(result[0], tuple):
                # It's a tuple of (position_tuple, flags)
                position_data = result[0]
                tropical_longitude = position_data[0]
                speed = position_data[3]  # Daily speed in longitude
            elif len(result) >= 6:
                # It's directly a position tuple
                tropical_longitude = result[0]
                speed = result[3]  # Daily speed in longitude
            else:
                logging.error(f"Unexpected result format from swe.calc_ut: {result}")
                return 0.0, 0.0, False
                
            # Planet is retrograde if speed is negative
            retrograde = speed < 0
            
            # Convert to sidereal using our verified method
            ayanamsa = calculate_ayanamsa(jd_ut)
            sidereal_longitude = (tropical_longitude - ayanamsa) % 360
            
            return tropical_longitude, sidereal_longitude, retrograde
        else:
            logging.error(f"Invalid result format from swe.calc_ut: {result}")
            # Return default values for this error case
            return 0.0, 0.0, False
    except Exception as e:
        logging.error(f"Error calculating planet position: {str(e)}")
        # Return default values for error case
        return 0.0, 0.0, False

def calculate_lunar_nodes(jd_ut):
    """
    Calculate the positions of the North Node (Rahu) and South Node (Ketu).
    
    Parameters:
    - jd_ut: Julian Day in Universal Time
    
    Returns a tuple of:
    - rahu_longitude: Sidereal longitude of Rahu (North Node)
    - ketu_longitude: Sidereal longitude of Ketu (South Node)
    """
    try:
        # First set to tropical mode
        swe.set_sid_mode(0)
        
        # Calculate Mean North Node (Mean Node)
        # 11 is the Swiss Ephemeris constant for Mean Node
        result = swe.calc_ut(jd_ut, 11, 2)  # 2 = SEFLG_SWIEPH
        
        # Handle different potential return formats
        if isinstance(result, tuple):
            if len(result) == 2 and isinstance(result[0], tuple):
                # It's a tuple of (position_tuple, flags)
                rahu_tropical = result[0][0]
            elif len(result) >= 6:
                # It's directly a position tuple
                rahu_tropical = result[0]
            else:
                logging.error(f"Unexpected result format from swe.calc_ut for Node: {result}")
                return 0.0, 180.0
                
            # Convert to sidereal using ayanamsa
            ayanamsa = calculate_ayanamsa(jd_ut)
            rahu_sidereal = (rahu_tropical - ayanamsa) % 360
            
            # Ketu is always 180° opposite to Rahu
            ketu_sidereal = (rahu_sidereal + 180) % 360
            
            return rahu_sidereal, ketu_sidereal
        else:
            logging.error(f"Invalid result format from swe.calc_ut for Node: {result}")
            # Return default positions in case of error
            return 0.0, 180.0
    except Exception as e:
        logging.error(f"Error calculating lunar nodes: {str(e)}")
        # Return default positions in case of error
        return 0.0, 180.0

def get_zodiac_sign(longitude):
    """
    Get zodiac sign from longitude in degrees.
    
    Parameters:
    - longitude: Longitude in degrees (0-360)
    
    Returns the zodiac sign as a string.
    """
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer", 
        "Leo", "Virgo", "Libra", "Scorpio", 
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    sign_index = int(longitude / 30)
    return signs[sign_index % 12]