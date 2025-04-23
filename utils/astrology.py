import math
from datetime import datetime
import ephem
import logging
from utils.astronomy import degrees_to_dms, get_zodiac_sign, calculate_lahiri_ayanamsa

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
            
            # Calculate Ascendant using PyEphem
            # Create a fixed body to represent the ascendant
            # In astronomical terms, the ascendant is the point on the ecliptic
            # that is rising on the eastern horizon at a given time and location
            
            # We'll use a direct calculation approach for the ascendant using the sidereal time

            # Get local sidereal time from observer
            sidereal_time = observer.sidereal_time()
            
            # The standard formula for converting sidereal time to ascendant:
            # First, calculate RAMC (Right Ascension of Medium Coeli)
            RAMC = sidereal_time
            
            # Standard obliquity of the ecliptic - average value as of J2000.0
            # This is approximately 23.4 degrees or about 0.4 radians
            # We need a fixed value that works with PyEphem
            obliquity = math.radians(23.4392911)  # Standard value for J2000
            
            # Convert observer's geographical latitude to radians
            latitude_rad = float(observer.lat)  # PyEphem stores lat in radians
            
            # Calculate ascendant using spherical trigonometry formula
            # The ascendant formula: tan(asc) = -cos(RAMC) / (sin(RAMC) * cos(obl) + tan(lat) * sin(obl))
            num = -math.cos(RAMC)
            den = (math.sin(RAMC) * math.cos(obliquity) + 
                  math.tan(latitude_rad) * math.sin(obliquity))
            
            # Use atan2 to get the correct quadrant
            asc_lon = math.atan2(num, den)
            
            # Convert to degrees and normalize to 0-360 range
            ascendant_tropical = math.degrees(asc_lon) % 360
            
            # Calculate the Lahiri ayanamsa dynamically for the birth date
            dynamic_ayanamsa = calculate_lahiri_ayanamsa(date_str)
            logging.debug(f"Using Lahiri ayanamsa: {dynamic_ayanamsa} degrees for date {date_str}")
            
            # Convert to Sidereal Ascendant by applying the calculated Ayanamsa
            ascendant_sidereal = (ascendant_tropical - dynamic_ayanamsa) % 360
            
            logging.debug(f"Calculated ascendant: tropical = {ascendant_tropical:.5f}°, sidereal = {ascendant_sidereal:.5f}°")
        
        # Get the sign of the Ascendant
        ascendant_sign = get_zodiac_sign(ascendant_sidereal)
        ascendant_sign_index = ["Aries", "Taurus", "Gemini", "Cancer", 
                               "Leo", "Virgo", "Libra", "Scorpio", 
                               "Sagittarius", "Capricorn", "Aquarius", "Pisces"].index(ascendant_sign)
        
        # In whole sign system, each house corresponds to one sign
        houses = []
        for i in range(12):
            house_number = i + 1
            sign_index = (ascendant_sign_index + i) % 12
            signs = ["Aries", "Taurus", "Gemini", "Cancer", 
                     "Leo", "Virgo", "Libra", "Scorpio", 
                     "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            sign = signs[sign_index]
            
            # In whole sign system, house cusp is the beginning of the sign
            cusp_longitude = sign_index * 30
            
            houses.append({
                'house_number': house_number,
                'sign': sign,
                'cusp_longitude': cusp_longitude,
                'formatted_position': f"{sign} 0°"
            })
        
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
    
    # Nakshatra rulers (deities)
    rulers = [
        "Ashwini Kumaras", "Yama", "Agni", 
        "Brahma", "Soma", "Rudra", 
        "Aditi", "Brihaspati", "Sarpa", 
        "Pitrs", "Bhaga", "Aryaman", 
        "Savitar", "Tvashtr", "Vayu", 
        "Indra-Agni", "Mitra", "Indra", 
        "Nirriti", "Apas", "Vishvakarma", 
        "Vishnu", "Vasus", "Varuna", 
        "Ajaikapada", "Ahir Budhnya", "Pushan"
    ]
    
    # Symbol or characteristics
    symbols = [
        "Horse's head", "Yoni", "Razor/Flame", 
        "Cart/Wheeled vehicle", "Deer head", "Teardrop", 
        "Bow", "Flower", "Serpent", 
        "Throne", "Front of a bed", "Back of a bed", 
        "Hand", "Pearl/Jewel", "Coral", 
        "Potter's wheel", "Lotus", "Earring/Umbrella", 
        "Tied roots", "Fan", "Elephant tusk", 
        "Trident", "Drum", "Empty circle", 
        "Two-faced man", "Two men carrying a bier", "Fish"
    ]
    
    # Each nakshatra spans 13 degrees and 20 minutes (13.33333... degrees)
    nakshatra_span = 360 / 27  # = 13.33333...
    
    # Calculate nakshatra index (0-26)
    nakshatra_index = int(longitude / nakshatra_span) % 27
    
    # Calculate position within nakshatra (0-100%)
    position_in_nakshatra = (longitude % nakshatra_span) / nakshatra_span * 100
    
    return {
        'name': nakshatras[nakshatra_index],
        'ruler': rulers[nakshatra_index],
        'symbol': symbols[nakshatra_index],
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
