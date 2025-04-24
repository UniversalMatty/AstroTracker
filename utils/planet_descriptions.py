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
        "Sun": "Represents the soul, ego, self-expression, vitality, authority, and father figures. The Sun governs leadership abilities, personal power, and creativity.",
        
        "Moon": "Governs emotions, mind, maternal instincts, nurturing, and the subconscious. The Moon reflects how we process feelings, respond to others, and our emotional needs.",
        
        "Mercury": "Rules intellect, communication, logical thinking, learning, and adaptability. Mercury influences how we express ourselves, process information, and interact with others.",
        
        "Venus": "Governs love, relationships, beauty, aesthetics, pleasure, and values. Venus represents our capacity for affection, artistic appreciation, and harmony in relationships.",
        
        "Mars": "Represents energy, action, courage, passion, aggression, and drive. Mars influences our assertiveness, physical vitality, and how we pursue our desires.",
        
        "Jupiter": "The planet of expansion, wisdom, higher learning, abundance, and growth. Jupiter brings optimism, generosity, and opportunities for spiritual and material prosperity.",
        
        "Saturn": "Rules discipline, responsibility, restrictions, karma, and life lessons. Saturn teaches through challenges, representing structure, endurance, and maturity.",
        
        "Uranus": "Governs revolution, innovation, sudden changes, and originality. Uranus breaks established patterns, bringing unexpected developments and technological advancements.",
        
        "Neptune": "Represents spirituality, dreams, intuition, and dissolution of boundaries. Neptune influences imagination, compassion, and connection to higher realms.",
        
        "Pluto": "Rules transformation, regeneration, power dynamics, and hidden truths. Pluto brings profound changes through destruction and rebirth processes.",
        
        "Rahu": "The North Node of the Moon, representing desire, ambition, and worldly attachment. Rahu pushes us toward new experiences and materialistic growth, often causing obsession and illusion.",
        
        "Ketu": "The South Node of the Moon, representing past karma, spiritual insight, and detachment. Ketu brings spiritual wisdom, liberation from material desires, and connects to past life experiences.",
        
        "Ascendant": "Also known as Lagna, represents the self, physical body, appearance, and first impressions. The Ascendant is the zodiac sign rising on the eastern horizon at birth."
    }
    
    return descriptions.get(planet_name, "No description available.")