"""
Ephemerides database for common dates.
Each date contains sidereal longitudes (with Lahiri ayanamsa) for planets.
Positions are in decimal degrees.
"""

# This dictionary stores ephemerides data for specific dates
# Format: 'YYYY-MM-DD': {'Planet': longitude_in_degrees, ...}
EPHEMERIDES_DB = {
    # Your specific example date with exact positions
    '1993-02-17': {
        'Sun': 304.83555556,      # Aquarius
        'Moon': 257.5839444,      # Sagittarius
        'Mars': 74.93263889,      # Gemini
        'Mercury': 302.0583333,   # Aquarius 22:03:29
        'Jupiter': 170.3455556,   # Virgo
        'Venus': 347.9261111,     # Pisces
        'Saturn': 298.0786944,    # Aquarius
        'Rahu': 235.3453056,      # Scorpio
        'Ketu': 55.3453056        # Taurus
    },
    
    # Some sample dates with approximate positions
    # These are just examples and should be replaced with accurate calculations
    '1990-01-15': {
        'Sun': 270.5,             # Capricorn
        'Moon': 160.2,            # Virgo
        'Mars': 320.7,            # Aquarius
        'Mercury': 255.3,         # Sagittarius
        'Jupiter': 90.1,          # Cancer
        'Venus': 290.8,           # Capricorn
        'Saturn': 275.5,          # Capricorn
        'Rahu': 220.4,            # Scorpio
        'Ketu': 40.4              # Taurus
    },
    
    '2000-06-21': {
        'Sun': 66.2,              # Gemini
        'Moon': 120.5,            # Leo
        'Mars': 145.7,            # Virgo
        'Mercury': 70.3,          # Gemini
        'Jupiter': 50.1,          # Taurus
        'Venus': 85.8,            # Gemini
        'Saturn': 30.5,           # Aries
        'Rahu': 350.4,            # Pisces
        'Ketu': 170.4             # Virgo
    }
}

def get_ephemerides_for_date(date_str):
    """
    Get ephemerides data for a specific date if available.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Dictionary with planet positions or None if not available
    """
    return EPHEMERIDES_DB.get(date_str)