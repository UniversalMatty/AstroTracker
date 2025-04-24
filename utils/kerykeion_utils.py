"""
Kerykeion integration for astrological calculations.
Uses Kerykeion for accurate ascendant and house calculations.
"""
import logging
from datetime import datetime
from kerykeion import KerykeionSubject
from kerykeion.utilities.math import degrees_to_dms

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
        
        # Create the astrological subject
        subject = KerykeionSubject(
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
        ascendant = subject.first_house
        
        # Get the ascendant sign name and degree
        ascendant_sign = ascendant.sign_name
        ascendant_position = ascendant.position
        
        # Format ascendant in degrees, minutes, seconds
        degrees, minutes, seconds = degrees_to_dms(ascendant_position % 30)
        formatted_position = f"{ascendant_sign} {degrees}°{minutes}'{seconds}\""
        
        # Extract planet positions
        planets = []
        for planet in subject.planets_list:
            # Get planet details
            planet_name = planet.planet_name
            sign = planet.sign_name
            position = planet.position
            retrograde = planet.retrograde
            
            # Format position in DMS
            deg, mins, secs = degrees_to_dms(position % 30)
            formatted_pos = f"{sign} {deg}°{mins}'{secs}\""
            if retrograde:
                formatted_pos += " (R)"
            
            # Create planet data
            planet_data = {
                "name": planet_name,
                "longitude": position,
                "sign": sign,
                "retrograde": retrograde,
                "formatted_position": formatted_pos
            }
            
            # Add information about nakshatra if available (not native to Kerykeion)
            # This would require custom calculation
            
            planets.append(planet_data)
        
        # Extract house positions
        houses = []
        for i in range(1, 13):
            # Get the house method from Kerykeion
            house_method = getattr(subject, f"house_{i}")
            house_sign = house_method.sign_name
            house_position = house_method.position
            
            # Format house position
            house_deg, house_min, house_sec = degrees_to_dms(house_position % 30)
            house_formatted = f"{house_sign} {house_deg}°{house_min}'{house_sec}\""
            
            house_data = {
                "house": i,
                "sign": house_sign,
                "longitude": house_position,
                "formatted": house_formatted
            }
            houses.append(house_data)
        
        # Create the ascendant position object for compatibility
        ascendant_position_obj = {
            'longitude': ascendant.position,
            'sign': ascendant_sign,
            'degree': ascendant.position % 30,
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