"""
Planet descriptions for Vedic astrology.
Each description provides information about the planet's meaning and significance.
"""

def get_planet_description(planet_name):
    """
    Get a short description for the given planet.
    
    Args:
        planet_name: Name of the planet
        
    Returns:
        A string describing the planet's astrological significance
    """
    descriptions = {
        "Sun": "The Sun represents our core identity, ego, and personal power. In Vedic astrology, it governs authority, vitality, leadership, and self-expression. The Sun's position indicates areas of life where you naturally shine and express your individuality.",
        
        "Moon": "The Moon represents our emotions, subconscious mind, and inner feelings. In Vedic astrology, it governs intuition, nurturing abilities, and how we respond emotionally to experiences. The Moon's position indicates the nature of your emotional landscape and needs for comfort and security.",
        
        "Mercury": "Mercury represents intellect, communication, and analytical thinking. In Vedic astrology, it governs learning, speech, writing, and quick-wittedness. Mercury's position indicates how you process information, express yourself verbally, and approach problem-solving.",
        
        "Venus": "Venus represents love, beauty, aesthetics, and relationships. In Vedic astrology, it governs pleasure, artistic talents, and sensuality. Venus's position indicates your approach to love, what you find beautiful, and how you express affection and create harmony.",
        
        "Mars": "Mars represents energy, action, courage, and desire. In Vedic astrology, it governs ambition, physical strength, and competitive drive. Mars's position indicates how you assert yourself, pursue goals, and channel your passions and aggression.",
        
        "Jupiter": "Jupiter represents expansion, wisdom, and abundance. In Vedic astrology, it governs higher learning, philosophy, spirituality, and good fortune. Jupiter's position indicates areas of life where you may experience growth, optimism, and opportunities for advancement.",
        
        "Saturn": "Saturn represents discipline, responsibility, and life lessons. In Vedic astrology, it governs structure, limitations, hard work, and the wisdom gained through experience. Saturn's position indicates areas of life where you may face challenges that lead to maturity and mastery.",
        
        "Rahu": "Rahu (North Node) represents desire, ambition, and unfamiliar experiences. In Vedic astrology, it governs worldly obsessions, innovation, and breaking social norms. Rahu's position indicates areas of life where you seek growth through new, sometimes unconventional experiences.",
        
        "Ketu": "Ketu (South Node) represents spiritual insight, detachment, and liberation. In Vedic astrology, it governs intuitive knowledge, past-life abilities, and release from materialistic desires. Ketu's position indicates areas of life where you may experience a sense of detachment or possess inherent spiritual wisdom.",
        
        "Uranus": "Uranus represents innovation, rebellion, and sudden change. In Vedic astrology (where it's a non-traditional planet), it governs originality, technological advances, and liberation from restrictions. Uranus's position indicates areas where you seek freedom and may experience unexpected breakthroughs.",
        
        "Neptune": "Neptune represents spirituality, intuition, and transcendence. In Vedic astrology (where it's a non-traditional planet), it governs mysticism, dreams, and dissolving boundaries. Neptune's position indicates areas where you may experience inspiration, compassion, or sometimes confusion and illusion.",
        
        "Pluto": "Pluto represents transformation, power, and regeneration. In Vedic astrology (where it's a non-traditional planet), it governs deep psychological change, hidden resources, and rebirth. Pluto's position indicates areas of life where you may experience profound transformation and empowerment.",
        
        "Ascendant": "The Ascendant (or Lagna) represents your physical self and the way you present yourself to the world. It influences appearance, personality, and the first impression you make on others. The Ascendant is considered one of the most important points in a Vedic birth chart."
    }
    
    # Return the description if available, otherwise a generic message
    return descriptions.get(planet_name, f"Description for {planet_name} is not available.")