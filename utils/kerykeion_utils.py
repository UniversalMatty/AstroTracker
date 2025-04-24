"""
Kerykeion integration for astrological calculations.
Uses Kerykeion for accurate ascendant and house calculations.
"""
import logging
from datetime import datetime
from kerykeion import KrInstance

# Define our own degrees_to_dms function since the module structure has changed
def degrees_to_dms(degrees):
    """Convert decimal degrees to degrees, minutes, seconds"""
    d = int(degrees)
    m_float = (degrees - d) * 60
    m = int(m_float)
    s = int((m_float - m) * 60)
    return d, m, s

def calculate_lahiri_ayanamsa(date):
    """
    Calculate the Lahiri ayanamsa for a given date.
    The Lahiri ayanamsa was approximately 23°15' on Jan 1, 1950,
    and increases by about 50.3 seconds per year.
    
    Args:
        date: Date components as year, month, day
        
    Returns:
        The Lahiri ayanamsa value in degrees for the given date
    """
    year, month, day = date
    
    # Reference date: January 1, 1950
    ref_year = 1950
    ref_month = 1
    ref_day = 1
    ref_ayanamsa = 23.25  # 23°15' in decimal
    
    # Calculate years since reference date
    years_diff = year - ref_year
    
    # Adjust for partial year
    if month < ref_month or (month == ref_month and day < ref_day):
        years_diff -= 1
    
    # Ayanamsa increases by about 50.3 seconds per year (in degrees)
    seconds_per_year = 50.3 / 3600  # Convert to degrees
    
    # Calculate the ayanamsa
    ayanamsa = ref_ayanamsa + (years_diff * seconds_per_year)
    
    return ayanamsa

def calculate_kerykeion_chart(birth_date, birth_time, city, country, latitude=None, longitude=None):
    """
    Calculate a birth chart using Kerykeion.
    
    Args:
        birth_date: Date string in YYYY-MM-DD format
        birth_time: Time string in HH:MM format
        city: City name
        country: Country name or code
        latitude: Optional latitude (if city lookup fails)
        longitude: Optional longitude (if city lookup fails)
        
    Returns:
        Dictionary with chart details
    """
    try:
        # Parse date components
        year, month, day = map(int, birth_date.split('-'))
        
        # Parse time components (default to noon if not provided)
        hour, minute = 12, 0
        if birth_time:
            hour, minute = map(int, birth_time.split(':'))
        
        # Create the astrological chart with tropical zodiac
        chart = KrInstance(
            name="Subject",
            year=year, 
            month=month, 
            day=day,
            hour=hour, 
            minute=minute,
            city=city,
            nation=country,
            lat=latitude,
            lng=longitude,
            zodiac_type='Tropic'  # Use tropical zodiac and we'll apply Lahiri ayanamsa
        )
        
        # Calculate Lahiri ayanamsa for this date
        ayanamsa = calculate_lahiri_ayanamsa((year, month, day))
        logging.debug(f"Calculated Lahiri ayanamsa for {year}-{month}-{day}: {ayanamsa}°")
        
        # Extract the tropical ascendant
        tropical_ascendant = chart.first_house
        
        # Convert to sidereal (Lahiri ayanamsa)
        tropical_abs_pos = tropical_ascendant.abs_pos
        sidereal_abs_pos = (tropical_abs_pos - ayanamsa) % 360
        
        # Calculate the sign and position within sign
        sign_num = int(sidereal_abs_pos / 30)
        position_in_sign = sidereal_abs_pos % 30
        
        # Get sign abbreviation based on sign number
        sign_abbrs = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
        ascendant_sign = sign_abbrs[sign_num]
        
        # Map abbreviations to full sign names
        sign_map = {
            'Ari': 'Aries',
            'Tau': 'Taurus',
            'Gem': 'Gemini',
            'Can': 'Cancer',
            'Leo': 'Leo',
            'Vir': 'Virgo',
            'Lib': 'Libra',
            'Sco': 'Scorpio',
            'Sag': 'Sagittarius',
            'Cap': 'Capricorn',
            'Aqu': 'Aquarius',
            'Pis': 'Pisces'
        }
        
        # Get the full sign name
        full_sign_name = sign_map.get(ascendant_sign, ascendant_sign)
        
        # Format ascendant in degrees, minutes, seconds
        degrees, minutes, seconds = degrees_to_dms(position_in_sign)
        formatted_position = f"{full_sign_name} {degrees}°{minutes}'{seconds}\""
        
        logging.debug(f"Tropical ascendant: {tropical_ascendant.abs_pos}°, Ayanamsa: {ayanamsa}°, Sidereal: {sidereal_abs_pos}°")
        logging.debug(f"Sidereal ascendant: {full_sign_name} {degrees}°{minutes}'{seconds}\"")
        
        
        # Extract planet positions
        planets = []
        for planet in chart.planets_list:
            # Get planet details
            planet_name = planet.name
            tropical_position = planet.abs_pos
            retrograde = getattr(planet, 'retrograde', False)
            
            # Convert to sidereal
            sidereal_pos = (tropical_position - ayanamsa) % 360
            
            # Calculate sign
            sign_num = int(sidereal_pos / 30)
            position_in_sign = sidereal_pos % 30
            
            # Get sign abbreviation and full name
            sign_abbr = sign_abbrs[sign_num]
            full_sign = sign_map.get(sign_abbr, sign_abbr)
            
            # Format position in DMS
            deg, mins, secs = degrees_to_dms(position_in_sign)
            formatted_pos = f"{full_sign} {deg}°{mins}'{secs}\""
            if retrograde:
                formatted_pos += " (R)"
            
            # Create planet data
            planet_data = {
                "name": planet_name,
                "longitude": sidereal_pos,
                "sign": full_sign,
                "retrograde": retrograde,
                "formatted_position": formatted_pos
            }
            
            # Add information about nakshatra if available (not native to Kerykeion)
            # This would require custom calculation
            
            planets.append(planet_data)
        
        # Calculate houses using Whole Sign system based on the sidereal ascendant
        houses = []
        
        # For Whole Sign houses, we use the ascendant's sign as the 1st house
        # and each subsequent sign becomes the next house
        for i in range(12):
            house_num = i + 1
            house_sign_num = (sign_num + i) % 12
            house_sign_abbr = sign_abbrs[house_sign_num]
            house_sign_full = sign_map.get(house_sign_abbr, house_sign_abbr)
            
            # House cusp is at 0 degrees of the sign
            house_deg, house_min, house_sec = 0, 0, 0
            house_formatted = f"{house_sign_full} {house_deg}°{house_min}'{house_sec}\""
            
            house_data = {
                "house": house_num,
                "sign": house_sign_full,
                "longitude": house_sign_num * 30,  # Start of the sign
                "formatted": house_formatted
            }
            houses.append(house_data)
        
        # Create the ascendant position object for compatibility
        ascendant_position_obj = {
            'longitude': sidereal_abs_pos,
            'sign': full_sign_name,
            'degree': position_in_sign,
            'formatted': formatted_position
        }
        
        logging.info(f"Successfully calculated chart using Kerykeion - Ascendant: {formatted_position}")
        
        return {
            "ascendant": ascendant_position_obj,
            "houses": houses,
            "planets": planets,
            "calculation_method": "Kerykeion (Vedic)"
        }
        
    except Exception as e:
        logging.error(f"Error calculating chart with Kerykeion: {str(e)}")
        raise

def format_dms(degrees):
    """Format degrees to DMS (degrees, minutes, seconds) format."""
    d, m, s = degrees_to_dms(degrees)
    return f"{d}°{m}'{s}\""