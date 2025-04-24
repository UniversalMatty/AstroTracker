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
        
        # Create the astrological chart
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
            lon=longitude
        )
        
        # Extract the ascendant (first house)
        ascendant = chart.first_house
        
        # Get the ascendant sign and position
        ascendant_sign = ascendant.sign  # Three-letter abbreviation
        sign_num = ascendant.sign_num    # Number of the sign
        
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
        
        # Get the position within the sign
        ascendant_position = ascendant.position
        
        # Format ascendant in degrees, minutes, seconds
        degrees, minutes, seconds = degrees_to_dms(ascendant_position)
        formatted_position = f"{full_sign_name} {degrees}°{minutes}'{seconds}\""
        
        # Extract planet positions
        planets = []
        for planet in chart.planets_list:
            # Get planet details
            planet_name = planet.name
            sign_abbr = planet.sign
            position = planet.position
            retrograde = getattr(planet, 'retrograde', False)
            
            # Get full sign name
            full_sign = sign_map.get(sign_abbr, sign_abbr)
            
            # Format position in DMS
            deg, mins, secs = degrees_to_dms(position)
            formatted_pos = f"{full_sign} {deg}°{mins}'{secs}\""
            if retrograde:
                formatted_pos += " (R)"
            
            # Create planet data
            planet_data = {
                "name": planet_name,
                "longitude": position,
                "sign": full_sign,
                "retrograde": retrograde,
                "formatted_position": formatted_pos
            }
            
            # Add information about nakshatra if available (not native to Kerykeion)
            # This would require custom calculation
            
            planets.append(planet_data)
        
        # Extract house positions
        houses = []
        for i in range(1, 13):
            # Get the house attribute
            house_attr_name = f"house_{i}"
            if hasattr(chart, house_attr_name):
                house = getattr(chart, house_attr_name)
                sign_abbr = house.sign
                house_position = house.position
                
                # Get full sign name
                full_sign = sign_map.get(sign_abbr, sign_abbr)
                
                # Format house position
                house_deg, house_min, house_sec = degrees_to_dms(house_position)
                house_formatted = f"{full_sign} {house_deg}°{house_min}'{house_sec}\""
                
                house_data = {
                    "house": i,
                    "sign": full_sign,
                    "longitude": house_position,
                    "formatted": house_formatted
                }
                houses.append(house_data)
        
        # Create the ascendant position object for compatibility
        ascendant_position_obj = {
            'longitude': ascendant.abs_pos,
            'sign': full_sign_name,
            'degree': ascendant.position,
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