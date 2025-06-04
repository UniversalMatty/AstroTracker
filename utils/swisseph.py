"""
Swiss Ephemeris-based astrological calculations.
Uses the swisseph library for accurate astronomical calculations.
"""
import os
import swisseph as swe
import logging
from datetime import datetime, timezone

# Set up Swiss Ephemeris
# Path to ephemeris files - point directly to the ephe directory where SE1 files are stored
EPHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ephe")
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
                    Can also use 'E' for Equal Houses, or 'P' for Placidus.
    
    Returns a tuple of (houses, ascmc) where:
    - houses: List of house cusps
    - ascmc: List of special points (ascendant, midheaven, etc.)
    """
    try:
        # Validate house system 
        house_flag_map = {
            "Placidus": b'P',
            "Equal Houses": b'E',
            "Whole Sign": b'W'
        }
        
        # If house_system is a string key from the map, get the corresponding byte flag
        if isinstance(house_system, str) and house_system in house_flag_map:
            house_flag = house_flag_map[house_system]
        else:
            # If it's already a byte flag or an unrecognized value, use it directly
            house_flag = house_system
        
        # Ensure we have a valid house system flag 
        if house_flag not in [b'W', b'E', b'P']:
            logging.warning(f"Unsupported house system: {house_system}. Using Whole Sign (W) instead.")
            house_flag = b'W'
            
        # Calculate houses using houses_ex for more detailed data
        # Parameters:
        # jd_ut: Julian day in UT
        # lat: Latitude
        # lon: Longitude
        # hsys: House system flag (b'W', b'E', or b'P')
        # flags: 0 for default behavior
        cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_flag, 0)
        
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

def calculate_house_cusps(jd_ut, latitude, longitude, house_system="Equal Houses"):
    """
    Calculate sidereal house cusps using Swiss Ephemeris.
    
    Parameters:
    - jd_ut: Julian Day in Universal Time
    - latitude: Geographic latitude in decimal degrees
    - longitude: Geographic longitude in decimal degrees
    - house_system: House system to use (string): "Equal Houses", "Whole Sign", or "Placidus"
    
    Returns a dictionary with:
    - ascendant: Sidereal ascendant information
    - houses: List of house cusp information
    """
    try:
        # Debug info
        logging.debug(f"Calculating house cusps with JD: {jd_ut}, Lat: {latitude}, Long: {longitude}, House system: {house_system}")
        
        # House system mapping
        house_flag_map = {
            "Placidus": b'P',
            "Equal Houses": b'E',
            "Whole Sign": b'W'
        }
        
        # Get the correct house system flag
        house_flag = house_flag_map.get(house_system, b'E')  # Default to Equal Houses if not specified
        
        # First calculate the ascendant (Lagna)
        import swisseph as swe
        
        # Set path to ephemeris files if not already done
        try:
            swe.set_ephe_path(EPHE_PATH)
        except:
            logging.warning("Could not set ephemeris path, continuing with defaults")
        
        # Set sidereal mode to Lahiri
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
        except:
            logging.warning("Could not set sidereal mode, continuing with tropical calculations")
        
        try:
            # Using standard houses calculation with the specified house system
            logging.debug(f"Calculating houses with: jd_ut={jd_ut}, latitude={latitude}, longitude={longitude}, house_flag={house_flag}")
            houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, house_flag, 0)
            logging.debug(f"Raw houses result: {houses}")
            logging.debug(f"Raw ascmc result: {ascmc}")
            
            if ascmc and len(ascmc) > 0:
                tropical_asc = ascmc[0]  # Ascendant is first element
                logging.debug(f"Successfully retrieved ascendant: {tropical_asc}")
            else:
                logging.error("ascmc array is empty or invalid!")
                # In case of error, use a default value
                tropical_asc = 0.0
                logging.debug(f"Using default ascendant: {tropical_asc}")
            
            # Get ayanamsa for this date
            ayanamsa = calculate_ayanamsa(jd_ut)
            logging.debug(f"Using ayanamsa: {ayanamsa}")
            
            # Convert to sidereal
            sidereal_asc = (tropical_asc - ayanamsa) % 360
            sidereal_asc_sign = get_zodiac_sign(sidereal_asc)
            sidereal_asc_degree = sidereal_asc % 30
            
            # Get ruler for the sign
            ruler = get_sign_ruler(sidereal_asc_sign)
            
            # Add detailed logging for debugging
            logging.debug(f"Ascendant calculation details:")
            logging.debug(f"  - Tropical ascendant: {tropical_asc:.2f}°")
            logging.debug(f"  - Ayanamsa: {ayanamsa:.2f}°")
            logging.debug(f"  - Sidereal ascendant: {sidereal_asc:.2f}°")
            logging.debug(f"  - Zodiac sign: {sidereal_asc_sign}")
            logging.debug(f"  - Degree in sign: {sidereal_asc_degree:.2f}°")
            
            # Format ascendant
            ascendant = {
                'longitude': sidereal_asc,
                'sign': sidereal_asc_sign,
                'degree': sidereal_asc_degree,
                'formatted': f"{sidereal_asc_sign} {sidereal_asc_degree:.2f}° ({ruler})"
            }
            
            logging.debug(f"Ascendant: {ascendant['formatted']}")
            
            # Calculate houses based on the house system
            houses_result = []
            
            if house_system == "Whole Sign":
                # For Whole Sign houses, the 1st house starts at 0° of the sign that contains the ascendant
                asc_sign_num = int(sidereal_asc / 30)
                logging.debug(f"Ascendant sign number: {asc_sign_num}")
                
                # The first house (1) always starts at the beginning (0°) of the sign that contains the ascendant
                for i in range(1, 13):  # 12 houses
                    # Each house is an entire sign, starting with the ascendant sign for house 1
                    house_sign_num = (asc_sign_num + i - 1) % 12
                    house_longitude = house_sign_num * 30  # Each house starts at 0° of its sign
                    sign = get_zodiac_sign(house_longitude)
                    degree = 0  # Always 0 degrees for Whole Sign houses
                    
                    ruler = get_sign_ruler(sign)
                    
                    # Special case for house 1 - it should match the ascendant sign
                    if i == 1:
                        logging.debug(f"House 1 matches ascendant sign: {sidereal_asc_sign}")
                        # We ensure house 1 is set to the same sign as the ascendant
                        sign = sidereal_asc_sign
                    
                    houses_result.append({
                        'house': i,
                        'longitude': house_longitude,
                        'sign': sign,
                        'degree': degree,
                        'formatted': f"{sign} {degree:.2f}° ({ruler})"
                    })
                    logging.debug(f"House {i}: {sign} {degree:.2f}°")
            else:
                # For Equal Houses and Placidus, use the house cusps from Swiss Ephemeris
                for i in range(0, 12):  # 12 houses, 0-indexed loop
                    house_num = i + 1  # Convert to 1-indexed house number for display
                    
                    try:
                        # For some Swiss Ephemeris versions, the houses array is 13 elements 
                        # (elements 1-12 are the houses, element 0 is unused)
                        # For others, it might be 12 elements (0-11)
                        # We need to handle both cases safely
                        
                        try:
                            # Try to access the house position at index i+1 (1-indexed)
                            # This will work for the Swiss Ephemeris versions where houses is a 13-element array
                            if i+1 < len(houses):
                                tropical_house_longitude = houses[i+1]
                                logging.debug(f"Using house position from index {i+1}")
                            # If houses is only 12 elements (0-indexed), try index i instead
                            elif i < len(houses):
                                tropical_house_longitude = houses[i]
                                logging.debug(f"Using house position from index {i}")
                            else:
                                # Fallback if both indices are out of range
                                raise IndexError(f"House index {i+1} and {i} out of range for houses array length {len(houses)}")
                                
                            # Convert to sidereal
                            house_longitude = (tropical_house_longitude - ayanamsa) % 360
                            sign = get_zodiac_sign(house_longitude)
                            degree = house_longitude % 30
                        except Exception as e:
                            # Fallback calculation if we can't get the house position
                            logging.error(f"Error accessing house position: {str(e)}")
                            house_longitude = (sidereal_asc + (i*30)) % 360
                            sign = get_zodiac_sign(house_longitude)
                            degree = house_longitude % 30
                            logging.debug(f"Using fallback house position {house_longitude:.2f}°")
                        
                        # Special case for house 1
                        if house_num == 1:
                            # For consistency, in Equal Houses and Placidus, the first house should
                            # start at the exact ascendant point, not at the beginning of the sign
                            logging.debug(f"Adjusting house 1 to match ascendant: {sidereal_asc_sign} {sidereal_asc_degree:.2f}°")
                            
                            # We'll use the exact ascendant details for better accuracy
                            house_longitude = sidereal_asc
                            sign = sidereal_asc_sign
                            degree = sidereal_asc_degree
                        
                        ruler = get_sign_ruler(sign)
                        houses_result.append({
                            'house': house_num, 
                            'longitude': house_longitude,
                            'sign': sign,
                            'degree': degree,
                            'formatted': f"{sign} {degree:.2f}° ({ruler})"
                        })
                        logging.debug(f"House {house_num}: {sign} {degree:.2f}°")
                    except Exception as e:
                        logging.error(f"Error processing house {house_num}: {str(e)}")
                        # Create a default house in case of error
                        sign = get_zodiac_sign((sidereal_asc + (i*30)) % 360)
                        ruler = get_sign_ruler(sign)
                        houses_result.append({
                            'house': house_num,
                            'longitude': (sidereal_asc + (i*30)) % 360,
                            'sign': sign,
                            'degree': 0,
                            'formatted': f"{sign} 0.00° ({ruler})"
                        })
            
            return {
                'ascendant': ascendant,
                'houses': houses_result
            }
            
        except Exception as e:
            logging.error(f"Error in houses calculation: {str(e)}")
            # Fall back to manual equal houses calculation
            raise
            
    except Exception as e:
        logging.error(f"Error calculating house cusps: {str(e)}")
        # If everything fails, we'll create a basic template with placeholders
        # This ensures the UI won't break even if calculations fail
        
        # For the placeholder values, we'll create a simple Aries ascendant chart
        # with houses that follow in zodiacal order
        sign = 'Aries'
        ruler = get_sign_ruler(sign)
        
        # Mark this as a placeholder to show it's not actual calculated data
        ascendant = {
            'longitude': 0,
            'sign': sign,
            'degree': 0,
            'formatted': f"{sign} 0.00° ({ruler}) [placeholder]"
        }
        
        houses = []
        
        # Create houses in zodiacal order, starting with Aries for house 1
        for i in range(1, 13):
            house_longitude = (i-1) * 30  # Simple 30-degree spacing
            sign = get_zodiac_sign(house_longitude)
            degree = 0
            
            ruler = get_sign_ruler(sign)
            houses.append({
                'house': i,
                'longitude': house_longitude,
                'sign': sign,
                'degree': degree,
                'formatted': f"{sign} 0.00° ({ruler}) [placeholder]"
            })
        
        return {
            'ascendant': ascendant,
            'houses': houses
        }

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

def calculate_houses_and_ascendant(jd_ut, latitude, longitude, house_system=b'W'):
    """
    Calculate house cusps and ascendant using Swiss Ephemeris.
    
    Parameters:
        jd_ut: Julian Day in Universal Time
        latitude: Geographic latitude in decimal degrees
        longitude: Geographic longitude in decimal degrees
        house_system: House system to use. Default is 'W' for Whole Sign houses.
                    Can also use 'E' for Equal Houses, or 'P' for Placidus.
    
    Returns a dictionary with:
    - houses: List of house dictionaries
    - ascendant_longitude: Sidereal ascendant longitude
    - tropical_ascendant: Tropical ascendant longitude
    - ayanamsa: The ayanamsa value used
    - calculation_method: Description of the calculation method used
    """
    try:
        # Get the houses and ascendant/midheaven from Swiss Ephemeris
        cusps, ascmc = calculate_houses(jd_ut, latitude, longitude, house_system)
        
        # The ascendant is the first element of ascmc
        tropical_asc = ascmc[0]
        
        # Calculate ayanamsa for this Julian Day
        ayanamsa = calculate_ayanamsa(jd_ut)
        
        # Convert tropical ascendant to sidereal
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        
        # Get the sign of the sidereal ascendant
        sidereal_asc_sign = get_zodiac_sign(sidereal_asc)
        
        # Calculate houses in the Whole Sign system (the sign containing the ascendant is the 1st house)
        houses = []
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", 
            "Leo", "Virgo", "Libra", "Scorpio", 
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_index = signs.index(sidereal_asc_sign)
        
        for i in range(12):
            house_num = i + 1
            current_sign_index = (sign_index + i) % 12
            current_sign = signs[current_sign_index]
            
            house = {
                "house": house_num,
                "sign": current_sign,
                "degree": 0.0,  # In Whole Sign system, houses start at 0° of the sign
                "formatted": f"{current_sign}"
            }
            houses.append(house)
        
        # Return all the calculation details for maximum transparency
        return {
            "houses": houses,
            "ascendant_longitude": sidereal_asc,
            "tropical_ascendant": tropical_asc,
            "ayanamsa": ayanamsa,
            "ascendant_sign": sidereal_asc_sign,
            "ascendant_degree": sidereal_asc % 30,
            "ascendant_formatted": format_longitude_dms(sidereal_asc),
            "calculation_method": "Swiss Ephemeris (Lahiri Ayanamsa)"
        }
        
    except Exception as e:
        logging.error(f"Error calculating houses and ascendant: {str(e)}")
        raise

def get_sign_ruler(sign):
    """
    Get the modern planetary ruler of a zodiac sign.
    
    Parameters:
    - sign: Zodiac sign name
    
    Returns the ruling planet as a string.
    """
    rulers = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Pluto",  # Modern ruler (Mars is traditional)
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Uranus",  # Modern ruler (Saturn is traditional)
        "Pisces": "Neptune"  # Modern ruler (Jupiter is traditional)
    }
    return rulers.get(sign, "Unknown")

def julian_day_from_datetime(dt_utc):
    """Return Julian Day (UT) for a timezone-aware UTC datetime."""
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def get_sidereal_ascendant(jd_ut, latitude, longitude):
    """Calculate sidereal ascendant using Lahiri ayanamsa."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses, ascmc = swe.houses(jd_ut, latitude, longitude)
    tropical_asc = ascmc[0]
    ayanamsa = swe.get_ayanamsa(jd_ut)
    return (tropical_asc - ayanamsa) % 360
