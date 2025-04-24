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
        "Sun": "The Sun represents your core personality traits, confidence level, and natural talents. Its position can indicate your leadership style, how you express authority in professional settings, and the ways you seek recognition. A strong Sun often correlates with clear career direction and the ability to make independent decisions.",
        
        "Moon": "The Moon represents your emotional patterns, comfort needs, and instinctive reactions. Its position can indicate how you handle stress, your relationship with family members, and your emotional intelligence. The Moon's influence often appears in your home environment preferences and how you nurture relationships.",
        
        "Mercury": "Mercury represents your communication style, learning methods, and decision-making process. Its position can indicate your educational strengths, how you express ideas at work, and your approach to problem-solving. Mercury often manifests in your technological aptitude, writing abilities, and effectiveness in negotiations.",
        
        "Venus": "Venus represents your relationship patterns, aesthetic preferences, and financial habits. Its position can indicate your approach to partnerships, spending habits, and design sensibilities. Venus influences your diplomatic skills, taste in art and music, and how you maintain harmony in various social contexts.",
        
        "Mars": "Mars represents your energy levels, competitive nature, and action patterns. Its position can indicate your work ethic, exercise preferences, and conflict resolution style. Mars often influences career choices related to leadership, athletics, or technical skills, and can show how you pursue goals and handle challenging situations.",
        
        "Jupiter": "Jupiter represents your growth opportunities, educational interests, and optimistic tendencies. Its position can indicate potential career advancements, learning paths that bring success, and how you handle expansion in business. Jupiter often relates to international connections, publishing opportunities, and areas where you might experience financial abundance.",
        
        "Saturn": "Saturn represents your discipline, structural needs, and areas requiring persistent effort. Its position can indicate career responsibilities, time management challenges, and long-term planning abilities. Saturn often manifests in professional achievements gained through consistent work, organizational skills, and how you handle authority figures.",
        
        "Rahu": "Rahu (North Node) represents unfamiliar growth areas, progressive thinking, and innovative talents. Its position can indicate career fields where you can break new ground, technology adoption patterns, and unconventional relationship approaches. Rahu often correlates with areas where taking calculated risks leads to significant advancement.",
        
        "Ketu": "Ketu (South Node) represents inherent skills, areas of natural detachment, and analytical abilities. Its position can indicate technical expertise you may take for granted, research capacities, and situations where you benefit from minimalist approaches. Ketu often relates to specialized knowledge, scientific thinking, and areas where you function well independently.",
        
        "Uranus": "Uranus represents your innovative thinking, adaptability to change, and technological aptitude. Its position can indicate which career fields might experience sudden shifts, where you're likely to implement progressive solutions, and your capacity for original thinking. Uranus often influences your approach to digital technologies and collaborative projects.",
        
        "Neptune": "Neptune represents your creative imagination, sensitivity to environments, and pattern recognition abilities. Its position can indicate potential in artistic fields, vulnerability to misinformation, and capacity for empathetic leadership. Neptune often manifests in photography skills, music appreciation, and your approach to healthcare and wellness.",
        
        "Pluto": "Pluto represents your capacity for in-depth analysis, resource management, and transformative leadership. Its position can indicate areas where you excel at research, power dynamics in professional settings, and psychological insight. Pluto often correlates with investigative abilities, financial strategy, and organizational restructuring skills.",
        
        "Ascendant": "The Ascendant represents your natural physical energy patterns, first impression style, and practical approach to new situations. Its position strongly influences your body type, instinctive health habits, and personal presentation. The Ascendant manifests in how you adapt to different social and professional environments and often correlates with your natural strengths in first impressions."
    }
    
    # Return the description if available, otherwise a generic message
    return descriptions.get(planet_name, f"Description for {planet_name} is not available.")