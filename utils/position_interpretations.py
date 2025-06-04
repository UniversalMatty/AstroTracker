"""
Position-specific interpretations for planets in signs and houses.
These interpretations provide practical insights on the specific combinations
of planets in signs rather than general descriptions of planets or signs.
"""

def build_houses_from_ascendant(ascendant_sign):
    """
    COMPLETELY NEW IMPLEMENTATION: Build houses using the Whole Sign system
    
    1. First house has the exact same sign as the Ascendant (Lagna)
    2. Subsequent houses have consecutive zodiac signs
    
    This implementation is guaranteed to make House 1 match the Ascendant sign.
    
    Args:
        ascendant_sign: String containing the Ascendant's zodiac sign
        
    Returns:
        List of dictionaries containing house data
    """
    import logging
    import traceback
    
    try:
        # Standard zodiac signs in order
        zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        # Log the input for debugging
        logging.warning(f"BUILD HOUSES - INPUT ASCENDANT SIGN: '{ascendant_sign}' (type: {type(ascendant_sign).__name__})")
        
        # Validate and standardize the ascendant sign
        if ascendant_sign not in zodiac_signs:
            logging.warning(f"BUILD HOUSES - Invalid ascendant sign '{ascendant_sign}', defaulting to Aries")
            ascendant_sign = 'Aries'
        
        # Find the index of the ascendant sign
        asc_index = zodiac_signs.index(ascendant_sign)
        logging.warning(f"BUILD HOUSES - Ascendant index in zodiac array: {asc_index}")
        
        # Create the houses array with the Whole Sign system:
        # 1st house has the ascendant sign, subsequent houses have consecutive signs
        houses = []
        
        for house_num in range(1, 13):  # Houses 1-12
            # Calculate the sign index for this house (wrapping around the zodiac)
            sign_index = (asc_index + house_num - 1) % 12
            sign = zodiac_signs[sign_index]
            
            # Add house to the list
            house = {
                "house": house_num,
                "sign": sign,
                "system": "Whole Sign"
            }
            houses.append(house)
        
        # Log the final house array for debugging
        logging.warning(f"BUILD HOUSES - First house sign: '{houses[0]['sign']}'")
        logging.warning(f"BUILD HOUSES - All houses: {[(h['house'], h['sign']) for h in houses]}")
        
        # Final verification to guarantee House 1 matches Ascendant
        if houses[0]['sign'] != ascendant_sign:
            logging.error(f"BUILD HOUSES - CRITICAL ERROR: House 1 sign ({houses[0]['sign']}) doesn't match ascendant ({ascendant_sign})")
            # Force correct the first house sign
            houses[0]['sign'] = ascendant_sign
            logging.warning(f"BUILD HOUSES - FIXED House 1 sign to: {houses[0]['sign']}")
        
        return houses
        
    except Exception as e:
        # Log any exceptions that occur during house calculation
        logging.error(f"BUILD HOUSES - Exception in build_houses_from_ascendant: {str(e)}")
        logging.error(f"BUILD HOUSES - Traceback: {traceback.format_exc()}")
        
        # Create a fallback house array with Aries as the first house
        logging.warning("BUILD HOUSES - Using emergency fallback house calculation (Aries-based)")
        houses = []
        zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 
            'Leo', 'Virgo', 'Libra', 'Scorpio',
            'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        for house_num in range(1, 13):
            sign_index = (house_num - 1) % 12
            house = {
                "house": house_num,
                "sign": zodiac_signs[sign_index],
                "system": "Whole Sign (Emergency Fallback)"
            }
            houses.append(house)
        
        return houses

# Legacy function kept for backwards compatibility
def calculate_simple_houses(ascendant_sign):
    """Legacy wrapper for build_houses_from_ascendant"""
    return build_houses_from_ascendant(ascendant_sign)

def get_planet_in_sign_interpretation(planet_name, sign_name):
    """
    Get an interpretation for a specific planet in a specific sign.
    
    Args:
        planet_name: Name of the planet
        sign_name: Name of the sign
        
    Returns:
        A string with a practical interpretation of this specific combination
    """
    # Dictionary to store all the possible planet-sign combinations
    interpretations = {
        # Sun in signs
        "Sun-Aries": "With Sun in Aries, you typically have a direct leadership style and excel in competitive environments where quick decision-making is valued. At work, you're often the one who initiates projects and moves things forward with energy and determination. You tend to thrive in roles that let you pioneer new approaches.",
        
        "Sun-Taurus": "With Sun in Taurus, you bring exceptional persistence to projects and reliable follow-through to commitments. You excel in work environments that value stability and tangible results. Your practical approach to resource management makes you valuable in financial planning and sustainable growth initiatives.",
        
        "Sun-Gemini": "With Sun in Gemini, you showcase versatile communication skills and the ability to adapt quickly to new information. You excel in roles requiring research, writing, or public speaking. Your natural curiosity often leads to innovative connections between seemingly unrelated concepts, making you valuable in creative problem-solving situations.",
        
        "Sun-Cancer": "With Sun in Cancer, you have strong emotional intelligence and intuitive understanding of others' needs. You excel in nurturing environments like healthcare, education, or family businesses. Your dedication to team welfare and organizational history makes you particularly effective in roles requiring institutional memory and personnel development.",
        
        "Sun-Leo": "With Sun in Leo, you have natural charisma and leadership presence that draws others to your projects. You excel in roles requiring public presentations, creative direction, or motivating teams. Your confidence makes you particularly effective in high-visibility positions where personal brand and reputation matter.",
        
        "Sun-Virgo": "With Sun in Virgo, you bring analytical precision and attention to detail to your work. You excel in environments requiring quality control, process improvement, or technical writing. Your practical problem-solving approach makes you particularly valuable in troubleshooting complex systems and implementing efficiency measures.",
        
        "Sun-Libra": "With Sun in Libra, you excel at building consensus and mediating conflicting viewpoints in professional settings. Your diplomatic communication style makes you effective in client relations, negotiations, and team coordination. You typically perform best in collaborative environments that value aesthetic harmony and balanced decision-making.",
        
        "Sun-Scorpio": "With Sun in Scorpio, you bring investigative thoroughness and strategic thinking to your work. You excel in roles requiring research, crisis management, or confidential information handling. Your ability to see beyond surface appearances makes you particularly valuable in competitive business environments that reward psychological insight.",
        
        "Sun-Sagittarius": "With Sun in Sagittarius, you bring optimism and big-picture vision to projects. You excel in roles involving education, publishing, or international relations. Your forward-thinking approach makes you particularly effective in expansion initiatives, market development, and creating opportunities through networking.",
        
        "Sun-Capricorn": "With Sun in Capricorn, you bring disciplined organization and structural thinking to leadership roles. You excel in positions requiring long-term planning, resource management, and consistent performance. Your practical ambition makes you particularly effective in traditional business environments that reward reliability and measured progress.",
        
        "Sun-Aquarius": "With Sun in Aquarius, you bring innovative thinking and collaborative leadership to organizations. You excel in technology sectors, social enterprises, or research and development roles. Your ability to envision future trends makes you particularly valuable in modernization initiatives and cross-functional team projects.",
        
        "Sun-Pisces": "With Sun in Pisces, you bring creative imagination and empathetic understanding to your work. You excel in artistic fields, healthcare, or human services roles. Your intuitive grasp of emotional undercurrents makes you particularly effective in environments requiring sensitivity to unspoken needs and creative problem-solving.",
        
        # Moon in signs
        "Moon-Aries": "With Moon in Aries, you respond to challenges with quick emotional reactions and decisive action. In professional settings, you need autonomy and opportunities for initiative. Your direct emotional expression can energize team projects, especially during time-sensitive situations that benefit from your ability to act without hesitation.",
        
        "Moon-Taurus": "With Moon in Taurus, you find emotional security through stability and practical comfort in your environment. You excel in work settings with predictable schedules and tangible rewards. Your steady emotional temperament makes you particularly valuable during organizational changes when consistency and patience are needed.",
        
        "Moon-Gemini": "With Moon in Gemini, you process emotions through communication and intellectual analysis. You need variety and information exchange to feel emotionally engaged at work. Your adaptable emotional nature makes you particularly effective in environments requiring quick shifts between tasks and frequent interpersonal interactions.",
        
        "Moon-Cancer": "With Moon in Cancer, you have heightened emotional sensitivity and strong nurturing instincts. You excel in supportive roles or leading teams where organizational culture and morale are priorities. Your intuitive understanding of others' emotional needs makes you particularly effective in customer care and employee development.",
        
        "Moon-Leo": "With Moon in Leo, you need recognition and creative expression for emotional fulfillment. You thrive in workplaces that acknowledge your contributions and allow for personal flair. Your warm emotional presence makes you particularly effective in roles requiring inspiration, motivation, and building team loyalty.",
        
        "Moon-Virgo": "With Moon in Virgo, you find emotional security through practical problem-solving and creating efficient systems. You excel in detail-oriented work environments that value precision. Your analytical approach to emotions makes you particularly effective in crisis management situations requiring calm assessment rather than reactive responses.",
        
        "Moon-Libra": "With Moon in Libra, you process emotions through relationship dynamics and need harmonious work environments. You excel in partnership-oriented business models and collaborative projects. Your diplomatic emotional style makes you particularly effective in client relations, conflict resolution, and creating balanced team atmospheres.",
        
        "Moon-Scorpio": "With Moon in Scorpio, you experience emotions intensely and seek depth in professional relationships. You excel in environments requiring psychological insight, research, or crisis management. Your emotional resilience makes you particularly effective in high-pressure situations and projects requiring complete commitment.",
        
        "Moon-Sagittarius": "With Moon in Sagittarius, you need freedom and meaningful purpose for emotional satisfaction. You excel in educational roles, travel-related industries, or international business. Your optimistic emotional outlook makes you particularly effective in expanding organizations and motivating others during challenging transitions.",
        
        "Moon-Capricorn": "With Moon in Capricorn, you find emotional security through achievement and professional recognition. You excel in structured environments with clear advancement paths. Your disciplined approach to emotions makes you particularly effective in leadership roles requiring consistent performance regardless of personal feelings.",
        
        "Moon-Aquarius": "With Moon in Aquarius, you process emotions through intellectual understanding and value emotional independence. You excel in innovative companies, humanitarian organizations, or technology sectors. Your objective emotional perspective makes you particularly effective in team settings requiring impartial assessment and future-oriented thinking.",
        
        "Moon-Pisces": "With Moon in Pisces, you have heightened emotional sensitivity and intuitive understanding of collective atmospheres. You excel in creative fields, healthcare, or spiritual organizations. Your compassionate emotional nature makes you particularly effective in roles requiring empathy, artistic vision, and adaptability to subtle environmental cues.",
        
        # Mercury in signs
        "Mercury-Aries": "With Mercury in Aries, you communicate with directness and quick thinking. In professional settings, you excel at making rapid decisions and cutting through unnecessary details. Your communication style is particularly effective in time-sensitive projects, sales presentations, and leadership roles requiring clear directives.",
        
        "Mercury-Taurus": "With Mercury in Taurus, you process information methodically and communicate with practical clarity. You excel in financial planning, contract negotiations, and detailed documentation work. Your deliberate thinking style is particularly valuable in roles requiring reliable data management and consistent communication protocols.",
        
        "Mercury-Gemini": "With Mercury in Gemini, you gather diverse information quickly and communicate with versatility. You excel in writing, teaching, sales, or any role requiring adaptable communication. Your multitasking mental ability makes you particularly effective in fast-paced environments requiring simultaneous handling of various information streams.",
        
        "Mercury-Cancer": "With Mercury in Cancer, you communicate with emotional intelligence and remember personal details others miss. You excel in roles requiring care-based communication like counseling, human resources, or family businesses. Your intuitive thinking approach is particularly valuable in creating relatable marketing content and building customer loyalty.",
        
        "Mercury-Leo": "With Mercury in Leo, you communicate with charisma and creative flair. You excel in presentations, creative writing, or leadership communication roles. Your confident expression is particularly effective in motivational speaking, brand development, and situations requiring persuasive communication that inspires action.",
        
        "Mercury-Virgo": "With Mercury in Virgo, you analyze information with precision and communicate with practical clarity. You excel in technical writing, data analysis, or quality assurance roles. Your detail-oriented thinking is particularly valuable in troubleshooting complex systems, improving efficiency, and developing standard operating procedures.",
        
        "Mercury-Libra": "With Mercury in Libra, you communicate diplomatically and consider multiple perspectives before deciding. You excel in mediation, client relations, or collaborative decision-making environments. Your balanced thinking approach is particularly effective in negotiations, conflict resolution, and creating inclusive communication strategies.",
        
        "Mercury-Scorpio": "With Mercury in Scorpio, you communicate with strategic depth and investigate thoroughly before presenting conclusions. You excel in research, psychology, or investigative roles. Your penetrating mental focus makes you particularly effective in competitive analysis, uncovering hidden information, and high-stakes negotiation scenarios.",
        
        "Mercury-Sagittarius": "With Mercury in Sagittarius, you communicate with optimism and focus on big-picture concepts. You excel in teaching, publishing, or cross-cultural communication roles. Your expansive thinking style is particularly valuable in developing broad business strategies, creating educational content, and connecting disparate ideas into meaningful frameworks.",
        
        "Mercury-Capricorn": "With Mercury in Capricorn, you communicate with structure and authority, focusing on practical outcomes. You excel in business planning, policy development, or management communication. Your methodical thinking approach is particularly effective in creating long-term strategic frameworks and communicating complex ideas with clarity.",
        
        "Mercury-Aquarius": "With Mercury in Aquarius, you think innovatively and communicate with original perspectives. You excel in technology development, scientific research, or social movement organizing. Your progressive mental approach is particularly valuable in solving persistent problems through unconventional methods and collaborative intelligence.",
        
        "Mercury-Pisces": "With Mercury in Pisces, you think intuitively and communicate with empathetic understanding. You excel in creative writing, psychological insight, or visual communication. Your imaginative thinking style is particularly effective in artistic projects, understanding client needs before they're verbalized, and creating emotional connections through communication.",
        
        # Venus in signs
        "Venus-Aries": "With Venus in Aries, you approach relationships with enthusiasm and direct expression of interest. In professional settings, you form quick connections and prefer straightforward negotiations. Your relationship style is particularly effective in sales roles, athletic teams, and environments requiring immediate rapport and energetic collaboration.",
        
        "Venus-Taurus": "With Venus in Taurus, you build relationships with consistency and practical expressions of loyalty. You excel in environments that value aesthetic quality and sensory experience. Your approach to professional relationships is particularly effective in luxury markets, financial partnerships, and organizations requiring stable long-term commitments.",
        
        "Venus-Gemini": "With Venus in Gemini, you connect with others through communication and intellectual exchange. You excel in networking roles, media relations, or collaborative creative work. Your versatile relationship style is particularly valuable in building diverse professional connections, facilitating introductions between contacts, and adapting to various social contexts.",
        
        "Venus-Cancer": "With Venus in Cancer, you build relationships with emotional depth and nurturing support. You excel in family businesses, healthcare teams, or hospitality roles. Your supportive relationship approach is particularly effective in creating customer loyalty, developing mentoring programs, and establishing emotional safety in workplace cultures.",
        
        "Venus-Leo": "With Venus in Leo, you approach relationships with warmth, generosity, and authentic self-expression. You excel in entertainment industries, luxury sales, or leadership roles requiring charisma. Your expressive relationship style is particularly valuable in building brand loyalty, creating memorable client experiences, and inspiring team enthusiasm.",
        
        "Venus-Virgo": "With Venus in Virgo, you build relationships through practical assistance and attention to detail. You excel in service-oriented businesses, health consulting, or quality improvement teams. Your helpful relationship approach is particularly effective in client retention through excellent service, creating efficient collaboration systems, and showing appreciation through practical support.",
        
        "Venus-Libra": "With Venus in Libra, you cultivate relationships with diplomacy and aesthetic sensibility. You excel in design fields, conflict resolution roles, or partnership-based businesses. Your balanced relationship style is particularly valuable in negotiations, creating harmonious work environments, and developing win-win business proposals.",
        
        "Venus-Scorpio": "With Venus in Scorpio, you form deep, transformative relationships and value authentic connection over superficial networking. You excel in roles requiring trust with sensitive information, financial partnerships, or psychological insight. Your intense relationship approach is particularly effective in high-stakes negotiations and creating loyal business alliances.",
        
        "Venus-Sagittarius": "With Venus in Sagittarius, you build relationships through shared ideals and adventures. You excel in international business, educational publishing, or travel industries. Your expansive relationship style is particularly valuable in cross-cultural negotiations, developing mentor relationships, and creating mission-driven business partnerships.",
        
        "Venus-Capricorn": "With Venus in Capricorn, you approach relationships with practicality and long-term commitment. You excel in traditional business environments, legacy planning, or roles requiring professional networking. Your structured relationship style is particularly effective in building industry reputation, maintaining client relationships through consistency, and formalizing business partnerships.",
        
        "Venus-Aquarius": "With Venus in Aquarius, you build relationships based on intellectual connection and shared humanitarian values. You excel in technology startups, non-profit organizations, or innovative collaborative projects. Your progressive relationship approach is particularly valuable in forming diverse professional networks, creating community-oriented business models, and developing equitable team structures.",
        
        "Venus-Pisces": "With Venus in Pisces, you connect with others through empathy and intuitive understanding. You excel in creative collaborations, healing professions, or spiritual organizations. Your compassionate relationship style is particularly effective in creating emotional brand loyalty, understanding unspoken client needs, and developing supportive organizational cultures.",
        
        # Mars in signs
        "Mars-Aries": "With Mars in Aries, you pursue goals with direct action and quick initiative. In professional settings, you excel at starting projects, leading competitive efforts, and creating momentum. Your energetic approach is particularly effective in entrepreneurial ventures, sales targets, and situations requiring immediate decisive action.",
        
        "Mars-Taurus": "With Mars in Taurus, you work with determined persistence and practical resource management. You excel in financial planning, product development, or any field requiring steady productivity. Your methodical energy is particularly valuable in long-term projects, quality control, and sustainable business development initiatives.",
        
        "Mars-Gemini": "With Mars in Gemini, you apply energy through communication and mental versatility. You excel in negotiations, writing deadlines, or any work requiring quick thinking. Your adaptable approach to action is particularly effective in multi-tasking environments, gathering and distributing information, and verbally advocating for projects.",
        
        "Mars-Cancer": "With Mars in Cancer, you take action with emotional conviction and protective instincts. You excel in family businesses, property development, or roles protecting organizational assets. Your intuitive approach to action is particularly valuable in building team loyalty, creating security measures, and developing customer care initiatives.",
        
        "Mars-Leo": "With Mars in Leo, you pursue goals with confident self-expression and creative leadership. You excel in performance-based roles, creative direction, or motivational leadership. Your dramatic energy is particularly effective in brand promotion, inspiring teams during challenges, and situations requiring visible leadership presence.",
        
        "Mars-Virgo": "With Mars in Virgo, you apply energy with precise analysis and methodical improvement. You excel in quality assurance, efficiency consulting, or detailed technical work. Your practical approach to action is particularly valuable in troubleshooting systems, implementing procedural improvements, and managing complex task sequences.",
        
        "Mars-Libra": "With Mars in Libra, you take action through collaboration and strategic partnerships. You excel in negotiations, client relationship management, or team coordination. Your balanced approach to action is particularly effective in conflict resolution, creating fair agreements, and initiatives requiring stakeholder buy-in.",
        
        "Mars-Scorpio": "With Mars in Scorpio, you pursue goals with strategic intensity and psychological insight. You excel in competitive research, crisis management, or transformative leadership. Your focused energy is particularly valuable in turnaround situations, high-stakes negotiations, and addressing complex hidden problems requiring persistent investigation.",
        
        "Mars-Sagittarius": "With Mars in Sagittarius, you take action with optimistic expansion and philosophical purpose. You excel in international business, educational leadership, or entrepreneurial vision. Your adventurous approach to action is particularly effective in market expansion, publishing initiatives, and motivating teams with meaningful goals.",
        
        "Mars-Capricorn": "With Mars in Capricorn, you pursue goals with disciplined strategy and persistent ambition. You excel in organizational leadership, structural planning, or achievement-oriented environments. Your methodical approach to action is particularly valuable in long-term career development, building systems for lasting results, and tasks requiring consistent effort.",
        
        "Mars-Aquarius": "With Mars in Aquarius, you take action through innovation and collaborative reform. You excel in technology development, humanitarian initiatives, or progressive organizations. Your independent approach to action is particularly effective in disrupting outdated processes, implementing technological solutions, and mobilizing group efforts toward common goals.",
        
        "Mars-Pisces": "With Mars in Pisces, you pursue goals with intuitive adaptation and creative vision. You excel in artistic creation, spiritual leadership, or compassionate service. Your fluid approach to action is particularly valuable in situations requiring empathetic understanding, creative problem-solving, and navigating unclear circumstances with flexibility.",
        
        # Jupiter in signs
        "Jupiter-Aries": "With Jupiter in Aries, you experience growth through bold initiative and independent action. In professional settings, you excel at creating new opportunities through personal leadership. Your expansive energy is particularly effective in entrepreneurial ventures, athletic coaching, and situations requiring courageous decisions that open new pathways.",
        
        "Jupiter-Taurus": "With Jupiter in Taurus, you find success through practical resource development and steady expansion. You excel in financial planning, sustainable growth strategies, or luxury markets. Your abundance-oriented approach is particularly valuable in wealth management, product development with longevity, and creating security through measured expansion.",
        
        "Jupiter-Gemini": "With Jupiter in Gemini, you experience growth through intellectual diversity and communication networks. You excel in publishing, education, or roles requiring versatile knowledge. Your expansive mental approach is particularly effective in developing multi-channel marketing, creating educational content, and connecting disparate ideas or people for mutual benefit.",
        
        "Jupiter-Cancer": "With Jupiter in Cancer, you find success through emotional intelligence and supportive networks. You excel in family businesses, real estate, or nurturing professional environments. Your growth-oriented approach is particularly valuable in developing customer loyalty programs, creating supportive company cultures, and expanding businesses with historical foundations.",
        
        "Jupiter-Leo": "With Jupiter in Leo, you experience growth through creative leadership and authentic self-expression. You excel in entertainment industries, motivational speaking, or creative direction. Your expansive leadership style is particularly effective in brand development, inspiring team performance, and creating opportunities that showcase individual talents.",
        
        "Jupiter-Virgo": "With Jupiter in Virgo, you find success through analytical improvement and practical service systems. You excel in healthcare administration, efficiency consulting, or quality assurance roles. Your detail-oriented growth approach is particularly valuable in scaling service businesses, implementing systematic improvements, and expanding through precision rather than general promotion.",
        
        "Jupiter-Libra": "With Jupiter in Libra, you experience growth through balanced partnerships and harmonious negotiations. You excel in legal mediation, relationship consulting, or collaborative businesses. Your partnership-oriented approach is particularly effective in creating win-win business alliances, expanding through ethical practices, and developing inclusive growth strategies.",
        
        "Jupiter-Scorpio": "With Jupiter in Scorpio, you find success through strategic insight and transformative processes. You excel in investment banking, psychological consulting, or crisis management. Your depth-oriented growth approach is particularly valuable in turning around struggling businesses, developing powerful research initiatives, and creating wealth through strategic resource allocation.",
        
        "Jupiter-Sagittarius": "With Jupiter in Sagittarius, you experience growth through optimistic vision and broad philosophical frameworks. You excel in international business, higher education, or publishing. Your expansive worldview is particularly effective in developing global markets, creating educational enterprises, and leading organizations with inspiring mission statements.",
        
        "Jupiter-Capricorn": "With Jupiter in Capricorn, you find success through structured ambition and responsible leadership. You excel in corporate management, government contracting, or traditional industries. Your disciplined growth approach is particularly valuable in building lasting institutional success, developing professional credibility, and creating sustainable expansion through proven methods.",
        
        "Jupiter-Aquarius": "With Jupiter in Aquarius, you experience growth through innovation and collaborative networks. You excel in technology startups, social enterprises, or humanitarian organizations. Your progressive growth orientation is particularly effective in developing disruptive business models, expanding through community engagement, and creating success through ethical innovation.",
        
        "Jupiter-Pisces": "With Jupiter in Pisces, you find success through intuitive creativity and compassionate service. You excel in artistic fields, spiritual organizations, or healing professions. Your imaginative growth approach is particularly valuable in developing holistic business models, expanding through emotional connection with audiences, and creating success that transcends conventional metrics.",
        
        # Saturn in signs
        "Saturn-Aries": "With Saturn in Aries, you build structure through disciplined initiative and focused energy management. In professional settings, you develop maturity by learning strategic patience and channeling impulsiveness into planned action. Your structured approach is particularly effective in entrepreneurial ventures requiring sustainable growth rather than quick wins.",
        
        "Saturn-Taurus": "With Saturn in Taurus, you create stability through disciplined resource management and practical systems. You excel in financial regulation, conservation planning, or long-term asset development. Your methodical approach to structure is particularly valuable in creating sustainable business models, managing material resources efficiently, and building lasting value.",
        
        "Saturn-Gemini": "With Saturn in Gemini, you develop structure through disciplined communication and systematic information management. You excel in technical writing, data organization, or communication protocols. Your focused mental approach is particularly effective in developing clear documentation, creating structured learning systems, and maintaining information integrity.",
        
        "Saturn-Cancer": "With Saturn in Cancer, you build security through emotional discipline and structured support systems. You excel in family business management, organizational continuity planning, or community development. Your approach to structure is particularly valuable in creating sustainable care protocols, developing institutional memory, and balancing emotional needs with practical requirements.",
        
        "Saturn-Leo": "With Saturn in Leo, you create enduring impact through disciplined creativity and methodical leadership. You excel in production management, creative administration, or long-term brand development. Your structured approach to self-expression is particularly effective in sustainable performance systems, creating reliable creative output, and developing leadership protocols with integrity.",
        
        "Saturn-Virgo": "With Saturn in Virgo, you build precision through disciplined analysis and systematic improvement. You excel in quality assurance, process engineering, or detailed operational management. Your meticulous approach to structure is particularly valuable in regulatory compliance, implementing efficient systems, and creating reliable service delivery models.",
        
        "Saturn-Libra": "With Saturn in Libra, you develop structure through balanced agreements and carefully constructed relationships. You excel in contract law, formal negotiations, or partnership management. Your fair-minded approach to structure is particularly effective in creating sustainable agreements, developing balanced organizational policies, and establishing clear relationship parameters.",
        
        "Saturn-Scorpio": "With Saturn in Scorpio, you build depth through disciplined investigation and strategic resource control. You excel in financial forensics, risk management, or transformational leadership. Your focused approach to structure is particularly valuable in crisis stabilization, developing security protocols, and establishing controls for shared resources or confidential information.",
        
        "Saturn-Sagittarius": "With Saturn in Sagittarius, you create expansion through disciplined vision and structured educational frameworks. You excel in higher education administration, publishing standards, or international business regulation. Your principled approach to structure is particularly effective in developing ethical guidelines, creating sustainable growth plans, and establishing credible knowledge systems.",
        
        "Saturn-Capricorn": "With Saturn in Capricorn, you build authority through disciplined achievement and traditional structures. You excel in organizational leadership, governmental roles, or established institutions. Your responsible approach to structure is particularly valuable in creating reliable hierarchical systems, developing professional credentials, and establishing lasting operational frameworks.",
        
        "Saturn-Aquarius": "With Saturn in Aquarius, you develop innovation through disciplined collaboration and structured progressive systems. You excel in technology governance, cooperative management, or social organization. Your methodical approach to change is particularly effective in creating sustainable innovations, establishing equitable systems, and bridging traditional structures with future needs.",
        
        "Saturn-Pisces": "With Saturn in Pisces, you build boundaries through compassionate structure and realistic idealism. You excel in healthcare administration, spiritual organization, or creative production management. Your practical approach to inspiration is particularly valuable in creating sustainable support systems, developing realistic compassion protocols, and establishing clear guidelines in fluid environments.",
        
        # Rahu in signs
        "Rahu-Aries": "With Rahu in Aries, you're drawn to developing leadership abilities and pioneering initiatives that push boundaries. In professional settings, this manifests as natural entrepreneurial tendencies and willingness to take calculated risks. This position suggests potential success through independent ventures, competitive environments, and roles requiring courageous innovation.",
        
        "Rahu-Taurus": "With Rahu in Taurus, you're attracted to building material security and developing practical resources in unconventional ways. You might excel in financial innovation, sustainable luxury markets, or modernizing traditional industries. This position suggests potential success through wealth management approaches that balance stability with progressive methods.",
        
        "Rahu-Gemini": "With Rahu in Gemini, you're drawn to communication technologies and information systems that expand conventional thinking. You might excel in digital media, technical writing, or educational innovation. This position suggests potential success through roles requiring adaptive intelligence, multifaceted communication skills, and connecting diverse knowledge areas.",
        
        "Rahu-Cancer": "With Rahu in Cancer, you're attracted to creating innovative support systems and redefining traditional family or organizational structures. You might excel in remote work culture development, modern approaches to community building, or emotional intelligence technologies. This position suggests potential success through nurturing environments that incorporate progressive elements.",
        
        "Rahu-Leo": "With Rahu in Leo, you're drawn to creative leadership roles and recognition through distinctive self-expression. You might excel in digital entertainment, personal branding, or innovative leadership approaches. This position suggests potential success through performance-oriented environments that reward authentic individuality and creative risk-taking.",
        
        "Rahu-Virgo": "With Rahu in Virgo, you're attracted to perfecting systems and analytical approaches that break new ground. You might excel in data science, health technology, or efficiency optimization. This position suggests potential success through roles requiring detailed problem-solving, technical expertise, and methodical innovation in practical applications.",
        
        "Rahu-Libra": "With Rahu in Libra, you're drawn to creating balanced partnerships and fair systems through progressive approaches. You might excel in relationship technologies, modern mediation techniques, or collaborative business models. This position suggests potential success through environments valuing equitable exchange, diplomatic innovation, and aesthetic modernization.",
        
        "Rahu-Scorpio": "With Rahu in Scorpio, you're attracted to investigating hidden truths and transformative processes using innovative methods. You might excel in financial technology, psychological research, or strategic resource management. This position suggests potential success through roles requiring deep analytical skills, comfort with transformative change, and strategic intensity.",
        
        "Rahu-Sagittarius": "With Rahu in Sagittarius, you're drawn to expanding horizons through progressive educational approaches and global connectivity. You might excel in international digital marketing, educational technology, or cross-cultural initiatives. This position suggests potential success through environments valuing philosophical exploration, cultural growth, and optimistic vision.",
        
        "Rahu-Capricorn": "With Rahu in Capricorn, you're attracted to achieving recognition through innovative approaches to traditional structures. You might excel in corporate innovation, government modernization, or professional development technologies. This position suggests potential success through organizations that balance established credibility with progressive methodologies.",
        
        "Rahu-Aquarius": "With Rahu in Aquarius, you're drawn to technological innovation and social reform through collaborative networks. You might excel in futuristic technologies, humanitarian initiatives, or progressive organizational structures. This position suggests potential success through environments valuing scientific thinking, social consciousness, and breaking established patterns.",
        
        "Rahu-Pisces": "With Rahu in Pisces, you're attracted to expanding consciousness and creative vision through innovative approaches. You might excel in virtual reality, spiritual technologies, or artistic innovation. This position suggests potential success through environments valuing imagination, compassionate service, and intuitive understanding combined with technical advancement.",
        
        # Ketu in signs
        "Ketu-Aries": "With Ketu in Aries, you possess innate skills in independent action and self-initiated projects. In professional settings, you may take your natural directness and courage for granted. This position suggests you might excel in roles requiring quick decision-making and situations where detachment from personal glory allows your natural leadership to function most effectively.",
        
        "Ketu-Taurus": "With Ketu in Taurus, you have inherent understanding of resource management and practical value assessment. You might excel in minimalist approaches to business, essential resource allocation, or identifying core value in complicated assets. This position suggests potential success through roles where detachment from material attachment allows your natural stability to function most effectively.",
        
        "Ketu-Gemini": "With Ketu in Gemini, you possess innate communication abilities and information processing skills. You might excel in data analytics, technical documentation, or specialized knowledge areas. This position suggests potential success through roles requiring objective information assessment and situations where detachment from unnecessary details allows your natural analytical skills to function effectively.",
        
        "Ketu-Cancer": "With Ketu in Cancer, you have inherent emotional intelligence and understanding of support systems. You might excel in psychological analysis, organizational memory management, or heritage preservation. This position suggests potential success through roles where emotional detachment allows your natural intuitive understanding to function most effectively.",
        
        "Ketu-Leo": "With Ketu in Leo, you possess innate creative abilities and natural leadership presence. You might excel in behind-the-scenes creative direction, mentorship roles, or organizational culture development. This position suggests potential success in areas where detachment from personal recognition allows your natural charisma and talent to function most effectively.",
        
        "Ketu-Virgo": "With Ketu in Virgo, you have inherent analytical precision and attention to critical details. You might excel in quality assurance, specialized technical roles, or systems analysis. This position suggests potential success through roles where detachment from perfectionism allows your natural diagnostic abilities to function most effectively.",
        
        "Ketu-Libra": "With Ketu in Libra, you possess innate diplomatic skills and natural balance in relationships. You might excel in conflict resolution, aesthetic assessment, or creating fair systems. This position suggests potential success through roles where detachment from approval-seeking allows your natural sense of harmony and proportion to function most effectively.",
        
        "Ketu-Scorpio": "With Ketu in Scorpio, you have inherent investigative abilities and natural understanding of power dynamics. You might excel in research, emergency management, or strategic resource allocation. This position suggests potential success through roles where detachment from control issues allows your natural intensity and focus to function most effectively.",
        
        "Ketu-Sagittarius": "With Ketu in Sagittarius, you possess innate philosophical understanding and natural teaching abilities. You might excel in specialized knowledge transmission, ethical frameworks development, or focused educational programs. This position suggests potential success through roles where detachment from ideological positions allows your natural wisdom to function most effectively.",
        
        "Ketu-Capricorn": "With Ketu in Capricorn, you have inherent organizational abilities and natural understanding of hierarchical structures. You might excel in streamlined management approaches, essential business functions, or minimalist organizational models. This position suggests potential success through roles where detachment from status concerns allows your natural discipline to function most effectively.",
        
        "Ketu-Aquarius": "With Ketu in Aquarius, you possess innate innovative thinking and natural scientific abilities. You might excel in specialized technological fields, objective analysis roles, or focused research. This position suggests potential success through roles where detachment from group consensus allows your natural progressive thinking to function most effectively.",
        
        "Ketu-Pisces": "With Ketu in Pisces, you have inherent intuitive abilities and natural creative vision. You might excel in specific artistic techniques, spiritual practices, or compassionate service roles. This position suggests potential success through positions where detachment from emotional confusion allows your natural sensitivity and imagination to function most effectively."
    }
    
    # Create the lookup key from planet and sign
    key = f"{planet_name}-{sign_name}"
    
    # Return the interpretation if available, otherwise a generic message
    return interpretations.get(key, f"The specific interpretation for {planet_name} in {sign_name} is not available yet.")


def get_ascendant_interpretation(sign_name):
    """
    Get interpretation for a specific ascendant sign.
    
    Args:
        sign_name: Name of the ascendant sign
        
    Returns:
        A string with an interpretation of this ascendant sign
    """
    # Dictionary of ascendant sign interpretations
    interpretations = {
        "Aries": "With Aries Ascendant, you project a dynamic and pioneering presence that others notice immediately. Your natural approach to new situations is direct and action-oriented. In professional settings, you're perceived as someone who takes initiative and leads with confidence. This ascendant gives you a competitive edge and the courage to pursue challenging opportunities that require quick decision-making and bold action.",
        
        "Taurus": "With Taurus Ascendant, you present yourself with steady reliability and practical groundedness. Your natural approach to situations is methodical and patient. In professional settings, you're perceived as dependable and solid. This ascendant gives you a natural presence that inspires others to trust your judgment, especially regarding resource management, long-term planning, and creating tangible results.",
        
        "Gemini": "With Gemini Ascendant, you project an adaptable, communicative presence. Your natural approach to situations is curious and information-gathering. In professional settings, you're perceived as versatile and quick-thinking. This ascendant gives you exceptional verbal skills and the ability to network effectively across different groups. You excel in environments that reward mental agility and social versatility.",
        
        "Cancer": "With Cancer Ascendant, you present yourself with nurturing sensitivity and emotional intelligence. Your natural approach to situations is protective and caring. In professional settings, you're perceived as supportive and intuitive about others' needs. This ascendant gives you a natural ability to create psychological safety for teams and build loyalty through genuine concern for others' wellbeing.",
        
        "Leo": "With Leo Ascendant, you project a warm, confident presence that naturally draws attention. Your approach to new situations is generous and self-assured. In professional settings, you're perceived as charismatic and leadership-oriented. This ascendant gives you a natural stage presence and the ability to inspire others through your authentic self-expression and unwavering confidence.",
        
        "Virgo": "With Virgo Ascendant, you present yourself with practical precision and analytical clarity. Your natural approach to situations is methodical and improvement-oriented. In professional settings, you're perceived as competent and detail-focused. This ascendant gives you a natural problem-solving orientation and the ability to implement efficient systems that others might overlook.",
        
        "Libra": "With Libra Ascendant, you project a harmonious, balanced presence. Your natural approach to situations is diplomatic and partnership-oriented. In professional settings, you're perceived as fair-minded and socially intelligent. This ascendant gives you excellent negotiation skills and the ability to create consensus in diverse teams, making you valuable in collaborative environments.",
        
        "Scorpio": "With Scorpio Ascendant, you present yourself with magnetic intensity and perceptive depth. Your natural approach to situations is strategic and investigative. In professional settings, you're perceived as powerful and insightful. This ascendant gives you exceptional ability to understand underlying motivations and navigate complex power dynamics that others might miss.",
        
        "Sagittarius": "With Sagittarius Ascendant, you project an optimistic, expansive presence. Your natural approach to situations is philosophical and growth-oriented. In professional settings, you're perceived as inspiring and visionary. This ascendant gives you the ability to see the bigger picture and connect diverse elements into meaningful opportunities, particularly in international or educational contexts.",
        
        "Capricorn": "With Capricorn Ascendant, you present yourself with structured composure and professional authority. Your natural approach to situations is disciplined and goal-oriented. In professional settings, you're perceived as reliable and achievement-focused. This ascendant gives you natural executive presence and the ability to navigate organizational hierarchies effectively.",
        
        "Aquarius": "With Aquarius Ascendant, you project an innovative, independent presence. Your natural approach to situations is progressive and community-oriented. In professional settings, you're perceived as forward-thinking and principled. This ascendant gives you a natural talent for bringing fresh perspectives to established systems and connecting diverse groups around shared ideals.",
        
        "Pisces": "With Pisces Ascendant, you present yourself with intuitive sensitivity and adaptable compassion. Your natural approach to situations is empathetic and receptive. In professional settings, you're perceived as understanding and imaginative. This ascendant gives you exceptional ability to sense emotional undercurrents and create inclusive environments where people feel genuinely understood."
    }
    
    return interpretations.get(sign_name, f"The specific interpretation for {sign_name} Ascendant is not available yet.")


def get_house_meaning(house_number, sign_name):
    """
    Get a practical interpretation for a house in a specific sign.
    
    Args:
        house_number: Number of the house (1-12)
        sign_name: Name of the sign
        
    Returns:
        A string describing practical applications of this house-sign combination
    """
    # House themes highlighting psychological focus
    house_areas = {
        1: "The 1st house reveals how you shape identity and react when feeling exposed. It shows whether courage or caution colors your self-image.",
        2: "The 2nd house explores resources and self-worth. It reflects how you chase stability or cling to possessions when insecure.",
        3: "The 3rd house examines learning style and immediate connections. It indicates whether you share ideas freely or retreat into silence under stress.",
        4: "The 4th house speaks to emotional roots and family conditioning. It reveals how you nurture yourself and seek safety at home.",
        5: "The 5th house expresses creativity and personal joy. It shows whether you risk sharing talents or guard them against judgment.",
        6: "The 6th house addresses daily habits and self-care. It highlights coping strategies for stress and the tension between perfectionism and compassion.",
        7: "The 7th house reveals patterns in partnership and projection. It exposes how you negotiate autonomy and cooperation in close relationships.",
        8: "The 8th house delves into intimacy, power, and transformation. It uncovers how you handle vulnerability and profound change.",
        9: "The 9th house looks at beliefs and expansive journeys. It shows how you seek meaning or cling to dogma when growth feels uncertain.",
        10: "The 10th house reflects ambition and public standing. It indicates how authority figures shape your drive for purposeful success.",
        11: "The 11th house explores community ties and future ideals. It shows how you connect with groups and rely on networks for support.",
        12: "The 12th house uncovers subconscious habits and spiritual longings. It highlights where retreat or escapism can become a coping style."
    }
    
    # Get the base house meaning
    base_meaning = house_areas.get(house_number, "Unknown house area")
    
    # Sign influences on house manifestations - how the sign modifies the house expression
    sign_influences = {
        "Aries": "direct, energetic, pioneering approach to",
        "Taurus": "stable, practical, resource-conscious approach to",
        "Gemini": "adaptable, communicative, information-oriented approach to",
        "Cancer": "nurturing, security-focused, emotionally attuned approach to",
        "Leo": "confident, expressive, leadership-oriented approach to",
        "Virgo": "analytical, improvement-focused, detail-oriented approach to",
        "Libra": "balanced, partnership-oriented, harmonious approach to",
        "Scorpio": "intense, transformative, research-oriented approach to",
        "Sagittarius": "expansive, optimistic, growth-oriented approach to",
        "Capricorn": "structured, disciplined, achievement-oriented approach to",
        "Aquarius": "innovative, community-focused, progressive approach to",
        "Pisces": "intuitive, compassionate, adaptable approach to"
    }
    
    # Get the sign influence
    influence = sign_influences.get(sign_name, "distinct approach to")

    # Combine them into a reflective interpretation
    interpretation = f"{base_meaning} With {sign_name}, you approach this area in a {influence} way."
    
    return interpretation
