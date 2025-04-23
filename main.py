from flask import Flask, request, jsonify
import swisseph as swe
import datetime
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Ephemeris setup
swe.set_ephe_path('.')                    # look for .se1 files here
swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)   # sidereal Krishnamurti ayanamsa

# Zodiac signs and Nakshatras
ZODIAC = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
    'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]
NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
    "Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
    "Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
    "Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

# Short whole-sign house meanings
HOUSE_MEANINGS = {
    1:  "Self, identity, appearance",
    2:  "Values, resources, self-worth",
    3:  "Communication, siblings, local travel",
    4:  "Home, roots, emotional foundation",
    5:  "Creativity, romance, pleasure",
    6:  "Health, service, daily work",
    7:  "Partnerships, marriage, contracts",
    8:  "Transformation, shared resources, mysteries",
    9:  "Philosophy, higher education, long trips",
    10: "Career, reputation, public role",
    11: "Friendships, groups, aspirations",
    12: "Subconscious, solitude, spirituality"
}

def format_position(longitude):
    """Return e.g. '14.23° Cancer'."""
    sign = int(longitude // 30)
    deg  = longitude % 30
    return f"{deg:.2f}° {ZODIAC[sign]}"

def get_nakshatra(moon_longitude):
    """Return the Moon’s nakshatra."""
    index = int(moon_longitude // (360 / 27))
    return NAKSHATRAS[index]

@app.route('/chart', methods=['POST'])
def chart():
    data    = request.get_json()
    bdate   = data['birthdate']   # "YYYY-MM-DD"
    btime   = data['birthtime']   # "HH:MM"
    place   = data['place']
    country = data['country']

    # 1) Geocode place to lat/lon
    geolocator = Nominatim(user_agent="sidereal-api")
    location    = geolocator.geocode(f"{place}, {country}")
    lat, lon    = location.latitude, location.longitude

    # 2) Compute Julian Day
    year, month, day = map(int, bdate.split('-'))
    hour, minute     = map(int, btime.split(':'))
    jd               = swe.julday(year, month, day, hour + minute/60)

    # 3) Natal planetary positions
    bodies  = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']
    planets = {}
    for i, name in enumerate(bodies):
        lon_p = swe.calc_ut(jd, i)[0]
        planets[name] = format_position(lon_p)

    # 4) Ascendant (whole-sign)
    ascendant_long = swe.houses(jd, lat, lon)[1][0]
    ascendant      = format_position(ascendant_long)
    asc_sign       = int(ascendant_long // 30)

    # 5) Whole-sign houses
    houses = {}
    for i in range(12):
        sign_index = (asc_sign + i) % 12
        houses[f"House {i+1}"] = {
            "cusp":    f"0.00° {ZODIAC[sign_index]}",
            "meaning": HOUSE_MEANINGS[i+1]
        }

    # 6) Moon’s Nakshatra
    moon_long = swe.calc_ut(jd, swe.MOON)[0]
    nakshatra = get_nakshatra(moon_long)

    return jsonify({
        "latitude":   lat,
        "longitude":  lon,
        "ascendant":  ascendant,
        "nakshatra":  nakshatra,
        "planets":    planets,
        "houses":     houses
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
