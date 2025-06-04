"""
Planet descriptions for the Energetic Blueprint system.
Each description provides practical information about how planetary positions can manifest in personality traits and life patterns.
"""

def get_planet_description(planet_name):
    """
    Get a practical description for the given planet.
    
    Args:
        planet_name: Name of the planet
        
    Returns:
        A string describing the planet's practical significance in real-world terms
    """
    descriptions = {
        "Sun": "The Sun illustrates the seat of personal vitality and purpose. It reveals how you feel seen and how you compensate when insecurity arises. When integrated, it guides confidence and warmth; when wounded, it may seek approval or dominate. This placement highlights the path to authentic self-expression.",

        "Moon": "The Moon describes your emotional memory and instinctive reactions. It shows how you soothe yourself when anxious or cling to habits from childhood. Here we see where you seek safety, sometimes by retreating or over-nurturing. Awareness fosters emotional regulation and healthier attachment.",

        "Mercury": "Mercury governs perception and communication patterns. It maps how you process information and express thoughts under stress. This planet highlights coping styles like overthinking, humor, or avoidance when feeling unheard. Understanding Mercury refines your voice and mental agility.",

        "Venus": "Venus reveals your capacity for love, pleasure, and self-worth. It shows how you attract connection or build walls to avoid hurt. This placement influences financial choices and aesthetic preferences. Working with Venus softens self-judgment and deepens relational harmony.",

        "Mars": "Mars channels your assertive drive and management of anger. It exposes impulses used to defend, compete, or avoid confrontation. When conscious, Mars offers courage and healthy boundaries instead of reckless force. This placement teaches how to pursue desires without harm.",

        "Jupiter": "Jupiter expands your worldview and sense of possibility. It outlines how optimism or excess shapes your growth. Under stress, you may overreach; when balanced, you inspire others and explore new horizons. Jupiter points to experiences that cultivate meaning and generosity.",

        "Saturn": "Saturn symbolizes structure, responsibility, and fear of inadequacy. It shows where you compensate with hard work or withdrawal due to self-criticism. By facing these tests patiently, you build resilience and realistic confidence. Saturn teaches maturity through sustained effort.",

        "Rahu": "Rahu (North Node) depicts yearning for unfamiliar experiences. It can fuel obsession with novelty or status when insecurity bites. Engaged mindfully, Rahu promotes bold experimentation and progressive thinking. This point suggests stepping into discomfort to accelerate growth.",

        "Ketu": "Ketu (South Node) signals ingrained skills and tendencies toward detachment. You may retreat or undervalue these abilities, seeing them as ordinary. Recognizing Ketu helps you access quiet expertise without isolation and invites balance between independence and reliance.",

        "Uranus": "Uranus reflects your urge for freedom and authentic individuality. Sudden changes or rebellious impulses may surface when you feel restricted. Expressed consciously, Uranus inspires innovation and unconventional insight. It teaches adaptability and the courage to break outdated patterns.",

        "Neptune": "Neptune speaks to imagination, spirituality, and sensitivity to collective moods. It may blur boundaries, leading to escapism or idealization when reality feels harsh. Channeled well, Neptune fosters compassion, artistic vision, and subtle perception. This placement encourages discerning inspiration from illusion.",

        "Pluto": "Pluto reveals core desires for transformation and control. It exposes areas where power struggles or deep fears push you toward regeneration. Confronting Pluto's intensity promotes psychological insight and the ability to release outworn attachments. It guides profound healing through facing shadow material.",

        "Ascendant": "The Ascendant describes your instinctive approach to life and the impression you make on others. It reflects coping mechanisms used to protect identity when under pressure. Embracing its qualities allows authentic presence and adaptability. This point sets the tone for your personal journey."
    }
    
    # Return the description if available, otherwise a generic message
    return descriptions.get(planet_name, f"Description for {planet_name} is not available.")