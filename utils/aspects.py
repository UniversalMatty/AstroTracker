"""
Aspects calculation and interpretation module.

This module contains functions to calculate aspects between planets
and interpret their meaning.
"""

import logging
import math
from typing import Dict, List, Tuple


# Define aspect types and their orbs (how many degrees of tolerance)
ASPECTS = {
    "conjunction": {"angle": 0, "orb": 8, "symbol": "☌", "nature": "varies"},
    "opposition": {"angle": 180, "orb": 8, "symbol": "☍", "nature": "challenging"},
    "trine": {"angle": 120, "orb": 8, "symbol": "△", "nature": "harmonious"},
    "square": {"angle": 90, "orb": 7, "symbol": "□", "nature": "challenging"},
    "sextile": {"angle": 60, "orb": 6, "symbol": "⚹", "nature": "harmonious"},
    "quincunx": {"angle": 150, "orb": 5, "symbol": "⚻", "nature": "challenging"},
    "semi-sextile": {"angle": 30, "orb": 3, "symbol": "⚺", "nature": "minor"},
    "semi-square": {"angle": 45, "orb": 3, "symbol": "∠", "nature": "minor-challenging"},
    "sesquiquadrate": {"angle": 135, "orb": 3, "symbol": "⚼", "nature": "minor-challenging"}
}

# Define which planets to consider for aspects
MAJOR_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
ADDITIONAL_POINTS = ["Ascendant"]  # We will also calculate aspects to the Ascendant


def get_aspect_type(angle_diff: float) -> Tuple[str, float]:
    """
    Determine the type of aspect based on the angle difference.
    
    Args:
        angle_diff: The angular difference between two planets in degrees
        
    Returns:
        Tuple containing (aspect_name, orb) or (None, None) if no aspect is found
    """
    # Normalize the angle difference to 0-180 range
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    # Check each aspect type
    for aspect_name, aspect_data in ASPECTS.items():
        aspect_angle = aspect_data["angle"]
        max_orb = aspect_data["orb"]
        
        # Calculate how close the planets are to forming an exact aspect
        orb = abs(angle_diff - aspect_angle)
        
        # If within orb, return the aspect type and the orb value
        if orb <= max_orb:
            return aspect_name, orb
    
    # No aspect found
    return None, None


def calculate_aspects(planets: List[Dict], ascendant: Dict = None) -> List[Dict]:
    """
    Calculate all aspects between planets and optionally with the ascendant.
    
    Args:
        planets: List of planet dictionaries, each containing at least 'name' and 'longitude'
        ascendant: Optional ascendant dictionary with 'longitude'
        
    Returns:
        List of aspect dictionaries
    """
    aspects = []
    
    # Filter to major planets to avoid too many minor aspects
    major_planets = [p for p in planets if p["name"] in MAJOR_PLANETS]
    
    # Add ascendant to the list if provided
    if ascendant:
        ascendant_obj = {
            "name": "Ascendant",
            "longitude": ascendant["longitude"]
        }
        points_to_check = major_planets + [ascendant_obj]
    else:
        points_to_check = major_planets
    
    # Calculate aspects between all pairs (only once per pair)
    for i in range(len(points_to_check)):
        for j in range(i + 1, len(points_to_check)):
            point1 = points_to_check[i]
            point2 = points_to_check[j]
            
            # Skip calculating aspects between the same planet
            if point1["name"] == point2["name"]:
                continue
                
            # Calculate the angular difference
            angle_diff = abs(point1["longitude"] - point2["longitude"])
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
                
            # Get aspect type and orb
            aspect_type, orb = get_aspect_type(angle_diff)
            
            # If there's a valid aspect, add it to the list
            if aspect_type:
                # Format orb to 1 decimal place
                formatted_orb = round(orb, 1)
                
                # Get aspect properties
                aspect_properties = ASPECTS[aspect_type]
                
                aspect = {
                    "point1": point1["name"],
                    "point2": point2["name"],
                    "aspect_type": aspect_type,
                    "orb": formatted_orb,
                    "angle": angle_diff,
                    "symbol": aspect_properties["symbol"],
                    "nature": aspect_properties["nature"],
                    "applying": is_aspect_applying(point1, point2, aspect_properties["angle"])
                }
                
                # Add interpretation
                aspect["interpretation"] = get_aspect_interpretation(
                    point1["name"], 
                    point2["name"], 
                    aspect_type
                )
                
                aspects.append(aspect)
    
    # Sort aspects: first by aspect type importance, then by orb (closest first)
    aspect_priority = {
        "conjunction": 1,
        "opposition": 2,
        "trine": 3,
        "square": 4,
        "sextile": 5,
        "quincunx": 6,
        "semi-sextile": 7,
        "semi-square": 8,
        "sesquiquadrate": 9
    }
    
    sorted_aspects = sorted(
        aspects, 
        key=lambda a: (aspect_priority.get(a["aspect_type"], 99), a["orb"])
    )
    
    return sorted_aspects


def is_aspect_applying(point1: Dict, point2: Dict, aspect_angle: float) -> bool:
    """
    Determine if an aspect is applying (getting closer) or separating (moving apart).
    This is a simplification as we don't track speeds, but assuming typical speeds:
    - Outer planets are "slower" than inner planets
    - Moon is fastest, then Mercury, Venus, etc.
    
    Args:
        point1: First point dictionary with 'name' and 'longitude'
        point2: Second point dictionary with 'name' and 'longitude'
        aspect_angle: The ideal angle for the aspect
        
    Returns:
        True if the aspect is likely applying, False if separating
    """
    # Simplified version - just return False as we don't track speeds
    # In a real implementation, we would need daily motion values
    return False


def get_aspect_interpretation(planet1: str, planet2: str, aspect_type: str) -> str:
    """
    Get interpretation text for a specific aspect between two planets.
    
    Args:
        planet1: Name of the first planet
        planet2: Name of the second planet
        aspect_type: Type of aspect (conjunction, trine, etc.)
        
    Returns:
        Interpretation text for the aspect
    """
    # Create a key that is always sorted alphabetically by planet name
    # This ensures we get the same interpretation regardless of planet order
    planets = sorted([planet1, planet2])
    aspect_key = f"{planets[0]}_{planets[1]}_{aspect_type}"
    
    # Return the interpretation from our dictionary, or a generic one if not found
    return ASPECT_INTERPRETATIONS.get(
        aspect_key,
        GENERIC_ASPECT_INTERPRETATIONS.get(
            aspect_type,
            f"This {aspect_type} represents a significant connection between {planet1} and {planet2}."
        )
    )


# Generic interpretations by aspect type
GENERIC_ASPECT_INTERPRETATIONS = {
    "conjunction": "This conjunction represents a powerful fusion of these energies, intensifying both their qualities and expression.",
    
    "opposition": "This opposition creates a dynamic tension between these two energies, requiring balance and integration.",
    
    "trine": "This trine creates a harmonious flow between these energies, supporting ease and opportunity in their expression.",
    
    "square": "This square creates productive tension that drives growth through challenges and necessary adjustments.",
    
    "sextile": "This sextile supports positive cooperation between these energies, offering opportunities when actively engaged.",
    
    "quincunx": "This quincunx creates an awkward angle requiring constant adjustment and adaptation between these energies.",
    
    "semi-sextile": "This semi-sextile creates a subtle connection requiring awareness to utilize constructively.",
    
    "semi-square": "This semi-square creates mild friction that can manifest as minor irritations or growth opportunities.",
    
    "sesquiquadrate": "This sesquiquadrate represents built-up tension seeking an adjustment or release between these energies."
}


# Specific aspect interpretations
# Format: "planet1_planet2_aspect" where planets are in alphabetical order
ASPECT_INTERPRETATIONS = {
    # Sun-Moon aspects
    "Moon_Sun_conjunction": "The conjunction between Sun and Moon (New Moon energy) represents a powerful alignment of your conscious self and emotional nature. Your purpose and feelings work together harmoniously, giving you a strong sense of self-integration. You have a natural ability to express your emotions authentically and align your actions with your inner needs.",
    
    "Moon_Sun_opposition": "This opposition (Full Moon energy) creates a dynamic tension between your conscious identity and emotional nature. You may experience conflicts between what you want to do and what you feel you need. This aspect requires integrating your rational mind with your emotional responses, learning to honor both your individuality and your need for emotional connection.",
    
    "Moon_Sun_trine": "This harmonious aspect creates a natural flow between your identity and emotions. You can express your feelings authentically while maintaining a clear sense of purpose. There's an innate understanding of how to balance your rational mind with your emotional needs, allowing for integrated self-expression and emotional well-being.",
    
    "Moon_Sun_square": "This square creates productive tension between your conscious will and emotional nature. You may experience inner conflicts between what you want to achieve and what you feel you need emotionally. This aspect challenges you to develop a more integrated approach to honoring both your individual purpose and your emotional well-being.",
    
    # Mercury aspects
    "Mercury_Sun_conjunction": "This conjunction merges your conscious identity with your communication style and thinking patterns. You naturally express yourself with clarity and purpose, and your thoughts are closely aligned with your core identity. Your communication tends to be authentic and self-expressive.",
    
    "Mercury_Venus_conjunction": "This conjunction blends your communication style with your capacity for appreciation and relationship. You likely express yourself diplomatically and pleasantly, valuing harmony in exchanges. You may have artistic communication skills or an ability to articulate beauty and value effectively.",
    
    "Mercury_Mars_conjunction": "This conjunction energizes your mind and communication with drive and assertiveness. You likely think and speak with directness and passion. Your mental processes are quick, decisive, and action-oriented, though you may need to guard against impatience or argumentativeness in communication.",
    
    # Venus aspects
    "Sun_Venus_conjunction": "This conjunction integrates your core identity with your capacity for appreciation, pleasure, and connection. You naturally express warmth and charm as part of your essential self. Beauty, harmony, and relationships are central to your sense of purpose and self-expression.",
    
    "Venus_Mars_conjunction": "This conjunction merges your capacity for relationship with your drive and assertiveness. You bring passion and energy to your connections while maintaining an appreciation for harmony. This aspect supports direct pursuit of what (and who) you value, blending receptive and initiative energies.",
    
    # Jupiter aspects
    "Jupiter_Sun_conjunction": "This conjunction expands your sense of identity and purpose with optimism and growth potential. You likely approach life with a philosophical outlook and natural confidence. There may be opportunities for recognition and success, especially through education, travel, or spiritual pursuits.",
    
    "Jupiter_Moon_conjunction": "This conjunction expands your emotional nature with optimism and a philosophical perspective. You likely have a generous emotional capacity and find meaning in your feelings and needs. This aspect supports emotional abundance and growth through nurturing connections with others.",
    
    "Jupiter_Saturn_opposition": "This opposition creates tension between expansion and limitation. You may struggle between optimism and caution, growth and security, or risk-taking and conservatism. This aspect challenges you to develop a balanced approach that honors both the need for growth and the necessity of practical structure.",
    
    # Saturn aspects
    "Saturn_Sun_conjunction": "This conjunction brings discipline and structure to your core identity and purpose. You approach life with seriousness and a strong sense of responsibility. While this may create challenges in self-expression, it ultimately supports building something enduring and meaningful aligned with your authentic self.",
    
    "Saturn_Moon_opposition": "This opposition creates tension between your emotional needs and sense of limitation or responsibility. You may struggle between vulnerability and emotional control. This aspect challenges you to develop emotional maturity while honoring your authentic feelings and needs for security.",
    
    # Ascendant aspects
    "Ascendant_Sun_conjunction": "This conjunction aligns your outer personality and approach to life with your core identity and purpose. You present yourself authentically, with your external demeanor reflecting your inner essence. This aspect supports a strong sense of self and natural leadership abilities.",
    
    "Ascendant_Moon_conjunction": "This conjunction merges your outer personality with your emotional nature. Your appearance and approach to life likely reflect your feelings and inner needs. You may appear nurturing, sensitive, or emotionally expressive, with your moods visibly affecting how you engage with the world.",
    
    "Ascendant_Venus_conjunction": "This conjunction brings charm and aesthetic sensitivity to your outer personality. You likely make a pleasant first impression, with a natural grace or attractiveness. This aspect supports relationship-building and an appreciation for beauty in your approach to life.",
    
    "Jupiter_Ascendant_conjunction": "This conjunction expands your outer personality with optimism and growth potential. You likely make a positive first impression, appearing confident and generous. This aspect supports opportunity through personal connections and an expansive approach to life circumstances.",
    
    "Ascendant_Saturn_conjunction": "This conjunction brings structure and seriousness to your outer personality. You likely appear responsible, mature, or reserved upon first meeting. While this may create some initial distance in connections, it ultimately supports building respect and credibility in your life path."
}