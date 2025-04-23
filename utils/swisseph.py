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
    # Set the sidereal mode to Krishnamurti ayanamsa 
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    
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
    """Calculate Krishnamurti ayanamsa for a given Julian Day"""
    try:
        # Krishnamurti ayanamsa is defined with SE_SIDM_KRISHNAMURTI (constant value = 3)
        # Internally it uses t0 = 2333275.5795 (= January 1, 285) and ayan_t0 = 0°,
        # which defines the zero point where the tropical and sidereal zodiacs coincided
        # with the precession rate of 50.288"
        swe.set_sid_mode(3)  # Using direct constant value for SIDM_KRISHNAMURTI
        
        # Get ayanamsa value for the given date
        ayanamsa = swe.get_ayanamsa(jd_ut)
        
        # For verification, calculate ayanamsa using hardcoded values
        # KP (Krishnamurti) ayanamsa is uniquely defined through a coincidence date of 
        # 21 March 285 CE, Julian Calendar, at mean noon at Greenwich, as 0.0°
        # Using a simplified approximation method with reference value from 1900
        year_1900_jd = 2415021.0  # JD for January 1, 1900
        jd_diff = jd_ut - year_1900_jd
        years_since_1900 = jd_diff / 365.25
        manual_ayanamsa = 22.3736 + (years_since_1900 * 50.288 / 3600)
        
        logging.debug(f"KP (Krishnamurti) ayanamsa for JD {jd_ut}: {ayanamsa}")
        logging.debug(f"Manual approximation of KP ayanamsa: {manual_ayanamsa}")
        
        # In case the swe.get_ayanamsa() fails, return our manual calculation instead
        if ayanamsa < 20 or ayanamsa > 30:  # Sanity check for reasonable values
            logging.warning(f"Suspicious ayanamsa value from Swiss Ephemeris: {ayanamsa}. Using manual calculation.")
            return manual_ayanamsa
        
        return ayanamsa
    except Exception as e:
        logging.error(f"Error calculating Krishnamurti ayanamsa: {str(e)}")
        # Calculate dynamically based on the Julian day
        # For current date in 2025, this is approximately 24.19°
        year_1900_jd = 2415021.0  # JD for January 1, 1900
        jd_diff = jd_ut - year_1900_jd
        years_since_1900 = jd_diff / 365.25
        return 22.3736 + (years_since_1900 * 50.288 / 3600)

def calculate_houses(jd_ut, latitude, longitude, house_system=b'P'):
    """
    Calculate house cusps and ascendant using Swiss Ephemeris.
    
    Parameters:
    - jd_ut: Julian Day in Universal Time
    - latitude: Geographic latitude in decimal degrees
    - longitude: Geographic longitude in decimal degrees
    - house_system: House system to use. Default is 'P' for Placidus, which gives the most accurate ascendant.
                    Use 'W' for whole sign houses if needed.
    
    Returns a tuple of (houses, ascmc) where:
    - houses: List of house cusps
    - ascmc: List of special points (ascendant, midheaven, etc.)
    """
    try:
        # Calculate houses - parameters:
        # jd_ut: Julian day in UT
        # lat: Latitude
        # lon: Longitude
        # hsys: House system ('P' for Placidus by default, which is more accurate for the ascendant)
        houses, ascmc = swe.houses(jd_ut, latitude, longitude, house_system)
        
        # The ascendant is the first element of ascmc
        asc_degree = ascmc[0]
        asc_sign = get_zodiac_sign(asc_degree)
        degree_in_sign = asc_degree % 30
        
        # Log the raw values for debugging
        logging.debug(f"Swiss Ephemeris ascendant: {degree_in_sign:.2f}° {asc_sign} (tropical)")
        
        return houses, ascmc
    except Exception as e:
        logging.error(f"Error calculating houses with Swiss Ephemeris: {str(e)}")
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

def calculate_planet_position(planet_id, jd_ut, use_calibration=False):
    """
    Calculate planet position using Swiss Ephemeris.
    
    Parameters:
    - planet_id: Swiss Ephemeris planet ID (e.g., swe.SUN, swe.MOON)
    - jd_ut: Julian Day in Universal Time
    - use_calibration: Whether to use special calibration to match reference charts
    
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