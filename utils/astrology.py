import math
from datetime import datetime
import ephem
import logging
import swisseph as swe
from utils.astronomy import degrees_to_dms, get_zodiac_sign, calculate_lahiri_ayanamsa
from utils.swisseph import calculate_jd_ut, calculate_houses as swe_calculate_houses, get_zodiac_sign as swe_get_zodiac_sign

def calculate_houses(date_str, time_str, longitude, latitude, fixed_ascendant=None):
    """
    Calculate house cusps using whole sign system and sidereal calculations.
    
    In the whole sign system, each house corresponds to one sign of the zodiac,
    with the ascendant sign being the 1st house, the next sign the 2nd house, etc.
    
    Parameters:
    - date_str: Date string in YYYY-MM-DD format
    - time_str: Time string in HH:MM format (optional)
    - longitude: Geographic longitude in decimal degrees
    - latitude: Geographic latitude in decimal degrees
    - fixed_ascendant: Optional fixed ascendant position in degrees
    
    Returns a list of dictionaries with house data
    """
    try:
        # If a fixed_ascendant is provided, use it directly
        if fixed_ascendant is not None:
            ascendant_sidereal = fixed_ascendant
            logging.debug(f"Using fixed ascendant: {ascendant_sidereal} degrees")
        else:
            # Calculate Julian Day in Universal Time
            jd_ut = calculate_jd_ut(date_str, time_str)
            logging.debug(f"Calculated Julian Day UT: {jd_ut}")
            
            # Use Swiss Ephemeris to calculate houses and ascendant
            # This gives both tropical and sidereal values
            try:
                # Ensure the ayanamsa mode is set to Krishnamurti
                swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
                
                # Calculate houses and ascendant using Swiss Ephemeris with Placidus system
                # for accurate ascendant (lagna) position
                houses_cusps, ascmc = swe.houses(jd_ut, latitude, longitude, b'P')
                
                # The Ascendant is the first element of ascmc (tropical)
                ascendant_tropical = ascmc[0] 
                logging.debug(f"Swiss Ephemeris raw ascendant (tropical): {ascendant_tropical}")
                
                # For sidereal calculation, get ayanamsa value
                ayanamsa = swe.get_ayanamsa(jd_ut)
                logging.debug(f"Swiss Ephemeris Krishnamurti ayanamsa: {ayanamsa}")
                
                # In the traditional Vedic astrology calculation, the ayanamsa is customarily subtracted
                # from the tropical position to get the sidereal position
                ascendant_sidereal = (ascendant_tropical - ayanamsa) % 360
                logging.debug(f"Raw calculation: tropical {ascendant_tropical} - ayanamsa {ayanamsa} = sidereal {ascendant_sidereal}")
                
                # Get zodiac signs for detailed debugging
                tropical_sign = get_zodiac_sign(ascendant_tropical)
                sidereal_sign = get_zodiac_sign(ascendant_sidereal)
                tropical_degree = ascendant_tropical % 30
                sidereal_degree = ascendant_sidereal % 30
                
                logging.debug(f"Tropical Ascendant: {tropical_degree:.2f}° {tropical_sign}")
                logging.debug(f"Sidereal Ascendant: {sidereal_degree:.2f}° {sidereal_sign}")
                
                # Format for debugging
                asc_sign = get_zodiac_sign(ascendant_sidereal)
                asc_degree = ascendant_sidereal % 30
                logging.debug(f"Sidereal Ascendant: {asc_degree:.2f}° {asc_sign}")
                
                logging.debug(f"Swiss Ephemeris calculated ascendant: tropical = {ascendant_tropical:.5f}° ({swe_get_zodiac_sign(ascendant_tropical)}), sidereal = {ascendant_sidereal:.5f}° ({swe_get_zodiac_sign(ascendant_sidereal)})")
                
            except Exception as swe_error:
                # Fallback to PyEphem if Swiss Ephemeris fails
                logging.warning(f"Swiss Ephemeris calculation failed: {str(swe_error)}. Falling back to PyEphem.")
                
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
                
                # Calculate the Ascendant using PyEphem
                # Create a body representing the ecliptic point on the eastern horizon
                body = ephem.FixedBody()
                body._ra = 0  # Will be replaced
                body._dec = 0  # Will be replaced
                body._epoch = observer.date
                
                # Horizontal coordinates for eastern horizon
                az = math.pi/2  # 90° East
                alt = 0.0  # On horizon
                
                # Convert horizontal to equatorial
                ra, dec = observer.radec_of(az, alt)
                body._ra = ra
                body._dec = dec
                body.compute(observer)
                
                # Convert to ecliptic coordinates
                ecl = ephem.Ecliptic(body)
                ascendant_tropical = math.degrees(ecl.lon) % 360
                
                # We need to use the Krishnamurti ayanamsa for consistency
                # This is approximately 23.86° (current value) instead of the Lahiri ayanamsa
                krishnamurti_ayanamsa = 23.86  # Fixed value for Krishnamurti ayanamsa
                logging.debug(f"Using Krishnamurti ayanamsa for PyEphem fallback: {krishnamurti_ayanamsa}")
                
                # Convert to sidereal using Krishnamurti ayanamsa
                ascendant_sidereal = (ascendant_tropical - krishnamurti_ayanamsa) % 360
                
                logging.debug(f"PyEphem calculated ascendant: tropical = {ascendant_tropical:.5f}° ({get_zodiac_sign(ascendant_tropical)}), sidereal = {ascendant_sidereal:.5f}° ({get_zodiac_sign(ascendant_sidereal)})")
        
        # Display accurate ascendant degree in the result
        ascendant_sign = get_zodiac_sign(ascendant_sidereal)
        ascendant_degree = ascendant_sidereal % 30
        ascendant_display = f"{ascendant_sign} {ascendant_degree:.2f}°"
        
        # Create zodiac signs list for reference
        signs = ["Aries", "Taurus", "Gemini", "Cancer", 
                 "Leo", "Virgo", "Libra", "Scorpio", 
                 "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        # Get the sign index of the Ascendant (1st house)
        # For whole sign house system, we use the sign of the ascendant as the 1st house
        ascendant_sign_index = signs.index(ascendant_sign)
        
        # In whole sign system, each house corresponds to one sign
        houses = []
        for i in range(12):
            house_number = i + 1
            sign_index = (ascendant_sign_index + i) % 12
            sign = signs[sign_index]
            
            # In whole sign system, house cusp is the beginning of the sign
            cusp_longitude = sign_index * 30
            
            # For the first house (house_number = 1), add the exact ascendant longitude and display
            if house_number == 1:
                houses.append({
                    'house_number': house_number,
                    'sign': sign,
                    'cusp_longitude': cusp_longitude,
                    'ascendant_longitude': ascendant_sidereal,  # Exact ascendant position
                    'ascendant_degree': ascendant_degree,  # Degree within sign
                    'formatted_position': f"{sign} (Ascendant at {ascendant_degree:.2f}°)"
                })
            else:
                houses.append({
                    'house_number': house_number,
                    'sign': sign,
                    'cusp_longitude': cusp_longitude,
                    'formatted_position': f"{sign}"
                })
        
        # Add overall ascendant information for easy access
        ascendant_info = {
            'longitude': ascendant_sidereal,
            'sign': ascendant_sign,
            'degree': ascendant_degree,
            'formatted': ascendant_display
        }
        
        # Log the final house arrangement
        logging.debug(f"Ascendant: {ascendant_display}")
        logging.debug(f"House 1: {houses[0]['formatted_position']}")
        
        return houses
        
    except Exception as e:
        logging.error(f"Error calculating houses: {str(e)}")
        raise

def get_nakshatra(longitude):
    """
    Get the nakshatra (lunar mansion) for a given longitude.
    There are 27 nakshatras in total, each spanning 13°20' (13.33333... degrees).
    
    Parameters:
    - longitude: Sidereal longitude in degrees
    
    Returns a dictionary with nakshatra information
    """
    # Nakshatra names
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", 
        "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", 
        "Magha", "Purva Phalguni", "Uttara Phalguni", 
        "Hasta", "Chitra", "Swati", 
        "Vishakha", "Anuradha", "Jyeshtha", 
        "Mula", "Purva Ashadha", "Uttara Ashadha", 
        "Shravana", "Dhanishta", "Shatabhisha", 
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    # Nakshatra ruling planets (for Vedic astrology)
    ruling_planets = [
        "Ketu", "Venus", "Sun", 
        "Moon", "Mars", "Rahu", 
        "Jupiter", "Saturn", "Mercury", 
        "Ketu", "Venus", "Sun", 
        "Moon", "Mars", "Rahu", 
        "Jupiter", "Saturn", "Mercury", 
        "Ketu", "Venus", "Sun", 
        "Moon", "Mars", "Rahu", 
        "Jupiter", "Saturn", "Mercury"
    ]
    
    # Each nakshatra spans 13 degrees and 20 minutes (13.33333... degrees)
    nakshatra_span = 360 / 27  # = 13.33333...
    
    # Calculate nakshatra index (0-26)
    nakshatra_index = int(longitude / nakshatra_span) % 27
    
    # Calculate position within nakshatra (0-100%)
    position_in_nakshatra = (longitude % nakshatra_span) / nakshatra_span * 100
    
    return {
        'name': nakshatras[nakshatra_index],
        'ruling_planet': ruling_planets[nakshatra_index],
        'position': f"{position_in_nakshatra:.1f}%"
    }

def get_house_meanings():
    """
    Return a dictionary of house numbers and their astrological meanings.
    """
    return {
        1: "Self, physical body, personality, appearance, life approach",
        2: "Possessions, values, money, resources, self-worth",
        3: "Communication, siblings, short trips, early education, neighbors",
        4: "Home, family, roots, real estate, emotional foundation",
        5: "Creativity, romance, children, pleasure, self-expression",
        6: "Health, daily routines, service, work environment, skills",
        7: "Partnerships, marriage, contracts, open enemies, relationships",
        8: "Shared resources, transformation, sexuality, rebirth, others' money",
        9: "Higher education, philosophy, travel, spirituality, expansion",
        10: "Career, public reputation, authority, ambition, structure",
        11: "Friends, groups, hopes, wishes, collective support",
        12: "Unconscious, hidden strengths/weaknesses, spirituality, isolation"
    }
