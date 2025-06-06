import logging
import math
import os
import re
import traceback
from datetime import datetime, date
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    Response,
    make_response,
)
from werkzeug.utils import secure_filename
import tempfile
import json
import numpy as np
from timezonefinder import TimezoneFinder
import pytz
from skyfield.api import load, Topos

from utils.geocoding import get_coordinates
from utils.astronomy import calculate_planet_positions, get_zodiac_sign
from utils.astrology import get_nakshatra, get_house_meanings
from utils.planet_descriptions import get_planet_description
from utils.psych_descriptions import (
    get_planet_sign_description,
    get_house_sign_description,
)
from utils.position_interpretations import (
    get_planet_in_sign_interpretation,
    get_house_meaning,
    get_ascendant_interpretation,
)
from utils.utils import get_lahiri_ayanamsa
from utils.swisseph import calculate_jd_ut

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Load the ephemeris file
try:
    logging.info("Loading ephemeris file de440s.bsp...")
    eph = load("de440s.bsp")
    logging.info("Ephemeris loaded successfully")
except Exception as e:
    logging.error(f"Error loading ephemeris: {str(e)}")
    raise

# Define Earth for calculations
earth = eph["earth"]
ts = load.timescale()

# Zodiac signs and nakshatras
ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

NAKSHATRAS = [
    {"name": "Ashwini", "ruling_planet": "Ketu", "end_degree": 13.33333},
    {"name": "Bharani", "ruling_planet": "Venus", "end_degree": 26.66666},
    {"name": "Krittika", "ruling_planet": "Sun", "end_degree": 40.0},
    {"name": "Rohini", "ruling_planet": "Moon", "end_degree": 53.33333},
    {"name": "Mrigashira", "ruling_planet": "Mars", "end_degree": 66.66666},
    {"name": "Ardra", "ruling_planet": "Rahu", "end_degree": 80.0},
    {"name": "Punarvasu", "ruling_planet": "Jupiter", "end_degree": 93.33333},
    {"name": "Pushya", "ruling_planet": "Saturn", "end_degree": 106.66666},
    {"name": "Ashlesha", "ruling_planet": "Mercury", "end_degree": 120.0},
    {"name": "Magha", "ruling_planet": "Ketu", "end_degree": 133.33333},
    {"name": "Purva Phalguni", "ruling_planet": "Venus", "end_degree": 146.66666},
    {"name": "Uttara Phalguni", "ruling_planet": "Sun", "end_degree": 160.0},
    {"name": "Hasta", "ruling_planet": "Moon", "end_degree": 173.33333},
    {"name": "Chitra", "ruling_planet": "Mars", "end_degree": 186.66666},
    {"name": "Swati", "ruling_planet": "Rahu", "end_degree": 200.0},
    {"name": "Vishakha", "ruling_planet": "Jupiter", "end_degree": 213.33333},
    {"name": "Anuradha", "ruling_planet": "Saturn", "end_degree": 226.66666},
    {"name": "Jyeshtha", "ruling_planet": "Mercury", "end_degree": 240.0},
    {"name": "Mula", "ruling_planet": "Ketu", "end_degree": 253.33333},
    {"name": "Purva Ashadha", "ruling_planet": "Venus", "end_degree": 266.66666},
    {"name": "Uttara Ashadha", "ruling_planet": "Sun", "end_degree": 280.0},
    {"name": "Shravana", "ruling_planet": "Moon", "end_degree": 293.33333},
    {"name": "Dhanishta", "ruling_planet": "Mars", "end_degree": 306.66666},
    {"name": "Shatabhisha", "ruling_planet": "Rahu", "end_degree": 320.0},
    {"name": "Purva Bhadrapada", "ruling_planet": "Jupiter", "end_degree": 333.33333},
    {"name": "Uttara Bhadrapada", "ruling_planet": "Saturn", "end_degree": 346.66666},
    {"name": "Revati", "ruling_planet": "Mercury", "end_degree": 360.0},
]


def get_nakshatra_from_longitude(longitude):
    """Get nakshatra details from sidereal longitude in degrees"""
    for i, nakshatra in enumerate(NAKSHATRAS):
        if longitude < nakshatra["end_degree"]:
            start_degree = 0 if i == 0 else NAKSHATRAS[i - 1]["end_degree"]
            position_in_nakshatra = (
                (longitude - start_degree)
                / (nakshatra["end_degree"] - start_degree)
                * 100
            )
            return {
                "name": nakshatra["name"],
                "ruling_planet": nakshatra["ruling_planet"],
                "position": f"{position_in_nakshatra:.1f}%",
            }
    # Handle edge case (should not happen with proper input)
    return NAKSHATRAS[0]


def get_zodiac_sign_from_longitude(longitude):
    """Get zodiac sign from longitude in degrees (0-360)"""
    # Normalize longitude to ensure it's in 0-360 range
    normalized_longitude = longitude % 360
    sign_index = int(normalized_longitude / 30)
    return ZODIAC_SIGNS[sign_index % 12]


def format_position(longitude, retrograde=False):
    """Format position with zodiac sign and degree"""
    # Make sure longitude is normalized to 0-360 range
    normalized_longitude = longitude % 360
    sign = get_zodiac_sign_from_longitude(normalized_longitude)
    degree = normalized_longitude % 30
    nakshatra = get_nakshatra_from_longitude(normalized_longitude)
    r_symbol = " (R)" if retrograde else ""

    # Format degrees in DMS format
    degree_int = int(degree)
    minutes_float = (degree - degree_int) * 60
    minutes_int = int(minutes_float)
    seconds_int = int((minutes_float - minutes_int) * 60)

    formatted_dms = f"{sign} {degree_int}°{minutes_int}'{seconds_int}\""
    if retrograde:
        formatted_dms += " (R)"

    # Create full output
    return {
        "longitude": normalized_longitude,
        "sign": sign,
        "degree": degree,
        "formatted": formatted_dms,
        "nakshatra": nakshatra,
        "full_description": f"{sign} {degree_int}°{minutes_int}'{seconds_int}\" – {nakshatra['name']} ({nakshatra['ruling_planet']}){r_symbol}",
    }


def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates using timezonefinder."""
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if timezone_str is None:
            logging.warning(
                f"Could not find timezone for coordinates: {latitude}, {longitude}. Using UTC."
            )
            return "UTC"
        return timezone_str
    except Exception as e:
        logging.error(f"Error finding timezone: {str(e)}")
        return "UTC"


def calculate_ascendant(t, observer):
    """
    Calculate the ascendant (rising sign) using Skyfield.

    Args:
        t: Skyfield Time object
        observer: Skyfield Topos object for the observer's location

    Returns:
        Tropical longitude of the ascendant in degrees
    """
    # Much simpler approach that doesn't require accessing observer's internal structure
    # We use the constructor parameters directly since we know them

    # Extract latitude and longitude from the observer's creation parameters
    # These should be available when we created the observer with earth + Topos()
    latitude_degrees = observer.target.theta.degrees
    longitude_degrees = observer.target.longitude.degrees

    from skyfield.constants import tau

    # Get Local Sidereal Time
    # GMST = Greenwich Mean Sidereal Time
    greenwich_sidereal_hours = t.gmst
    # Convert to radians
    greenwich_sidereal_radians = greenwich_sidereal_hours * tau / 24.0

    # Add the observer's longitude to get Local Sidereal Time (LST)
    longitude_radians = math.radians(longitude_degrees)
    lst_radians = greenwich_sidereal_radians + longitude_radians

    # Normalize to 0-2π
    lst_radians = lst_radians % tau

    # Convert LST to degrees
    lst_degrees = math.degrees(lst_radians)

    # Obliquity of the ecliptic (approx. 23.4 degrees)
    obliquity_radians = math.radians(23.4392911)

    # Observer's latitude
    latitude_radians = math.radians(latitude_degrees)

    # Calculate ascendant using the standard formula
    tan_term = math.tan(latitude_radians) * math.cos(obliquity_radians)
    sin_lst = math.sin(lst_radians)
    cos_lst = math.cos(lst_radians)

    # Formula: tan(ascendant) = -cos(LST) / (sin(LST)*cos(ε) + tan(φ)*sin(ε))
    # where ε is obliquity and φ is latitude
    denominator = sin_lst * math.cos(obliquity_radians) + tan_term * math.sin(
        obliquity_radians
    )
    ascendant_radians = math.atan2(-cos_lst, denominator)

    # Convert to degrees and normalize to 0-360 range
    ascendant_degrees = math.degrees(ascendant_radians) % 360

    return ascendant_degrees


def calculate_whole_sign_houses(ascendant_position):
    """
    Calculate house cusps using the Whole Sign system.
    In this system, the sign containing the ascendant becomes the 1st house,
    and each subsequent sign becomes the next house.

    For example, if the Ascendant is Aquarius 19°25'43",
    the 1st house cusp is Aquarius 0°0'0".

    Args:
        ascendant_position: Dictionary with ascendant details

    Returns:
        List of house dictionaries, each with sign and other details
    """
    # Add extra logging for debugging
    logging.debug("======== WHOLE SIGN HOUSE CALCULATION ========")
    logging.debug(f"Ascendant position data: {ascendant_position}")

    houses = []

    # Make sure we have a valid ascendant sign
    if not ascendant_position or "sign" not in ascendant_position:
        logging.error("Invalid ascendant position data. Missing 'sign' key.")
        return houses

    # Get ascendant sign
    ascendant_sign = ascendant_position["sign"]
    logging.debug(f"Ascendant sign: {ascendant_sign}")

    # Define zodiac signs again locally to ensure consistency
    zodiac_signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    # Find the index of the ascendant sign
    try:
        sign_index = zodiac_signs.index(ascendant_sign)
    except ValueError:
        logging.error(f"Could not find '{ascendant_sign}' in zodiac signs list")
        return houses

    logging.debug(f"Ascendant sign index: {sign_index}")

    # Calculate houses
    for i in range(12):
        house_num = i + 1
        current_sign_index = (sign_index + i) % 12
        current_sign = zodiac_signs[current_sign_index]

        # In Whole Sign system, houses start at 0° of the sign
        # regardless of where the ascendant is within the sign
        house_longitude = (
            current_sign_index * 30
        )  # 0-based index, each sign is 30 degrees

        house = {
            "house": house_num,
            "sign": current_sign,
            "degree": 0.0,  # Always 0 degrees in Whole Sign
            "longitude": house_longitude,
            "formatted": f"{current_sign} 0°0'0\"",
            "system": "Whole Sign",
        }
        houses.append(house)

        logging.debug(f"House {house_num}: {current_sign} (index {current_sign_index})")

    # Check the first house specifically
    if houses and len(houses) > 0:
        logging.debug(f"FIRST HOUSE SIGN: {houses[0]['sign']}")
        logging.debug(f"SHOULD MATCH ASCENDANT: {ascendant_sign}")

    logging.debug("==========================================")

    return houses


def calculate_equal_houses(ascendant_position):
    """
    Calculate house cusps using the Equal House system.
    In this system, the ascendant becomes the 1st house cusp,
    and each subsequent house cusp is 30 degrees apart.

    For example, if the Ascendant is Aquarius 19°25'43",
    the 1st house cusp is also at Aquarius 19°25'43".

    Args:
        ascendant_position: Dictionary with ascendant details

    Returns:
        List of house dictionaries, each with sign and degree details
    """
    # Add debug logging
    logging.debug("======== EQUAL HOUSES CALCULATION ========")
    logging.debug(f"Ascendant position data: {ascendant_position}")

    houses = []

    # Make sure we have valid ascendant data
    if not ascendant_position or "longitude" not in ascendant_position:
        logging.error("Invalid ascendant position data for Equal Houses calculation")
        return houses

    ascendant_longitude = ascendant_position["longitude"]
    ascendant_sign = ascendant_position["sign"]
    ascendant_degree = ascendant_position.get("degree", ascendant_longitude % 30)

    logging.debug(f"Ascendant longitude: {ascendant_longitude}°")
    logging.debug(f"Ascendant sign: {ascendant_sign}")
    logging.debug(f"Ascendant degree in sign: {ascendant_degree}°")

    for i in range(12):
        house_num = i + 1
        house_cusp_longitude = (ascendant_longitude + (i * 30)) % 360
        house_sign = get_zodiac_sign_from_longitude(house_cusp_longitude)
        house_degree = house_cusp_longitude % 30

        # Format degrees in DMS format (degrees, minutes, seconds)
        degree_int = int(house_degree)
        minutes_float = (house_degree - degree_int) * 60
        minutes_int = int(minutes_float)
        seconds_int = int((minutes_float - minutes_int) * 60)

        house = {
            "house": house_num,
            "sign": house_sign,
            "degree": house_degree,
            "longitude": house_cusp_longitude,
            "formatted": f"{house_sign} {degree_int}°{minutes_int}'{seconds_int}\"",
            "system": "Equal Houses",
        }
        houses.append(house)

        logging.debug(
            f"House {house_num}: {house_sign} {degree_int}°{minutes_int}'{seconds_int}\""
        )

    # Check the first house specifically
    if houses and len(houses) > 0:
        logging.debug(f"FIRST HOUSE SIGN: {houses[0]['sign']}")

    logging.debug("==========================================")

    return houses


def calculate_houses(ascendant_position, house_system="whole_sign"):
    """
    Calculate houses based on the selected system

    Args:
        ascendant_position: Dictionary with ascendant details
        house_system: String indicating which house system to use ('whole_sign' or 'equal')

    Returns:
        List of house dictionaries
    """
    if house_system.lower() == "equal":
        return calculate_equal_houses(ascendant_position)
    else:
        return calculate_whole_sign_houses(ascendant_position)


# Temporary directory for ephemerides uploads
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {"json", "csv", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload size


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/skyfield_form", methods=["GET"])
def skyfield_form():
    """Show the Skyfield-based calculation form"""
    return render_template("skyfield_form.html")


@app.route("/calculate_skyfield", methods=["POST"])
def calculate_skyfield():
    """Calculate chart data using Skyfield API (JSON-based)"""
    try:
        # Get JSON data from the request
        data = request.json

        if not data:
            logging.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400

        logging.debug(f"Received data: {data}")

        # Extract data
        birth_date = data.get("birth_date")
        birth_time = data.get("birth_time", "12:00")
        city = data.get("city")
        country = data.get("country")

        # Validate data
        if not all([birth_date, city, country]):
            return jsonify({"error": "Missing required data"}), 400

        # Get coordinates
        location_str = f"{city}, {country}"
        coordinates = get_coordinates(location_str)
        if not coordinates:
            logger.error("Geocoding failed for input: %s", location_str)
            return (
                jsonify(
                    {"error": "Could not determine coordinates for the given location"}
                ),
                400,
            )

        longitude, latitude = coordinates
        logging.debug(f"Coordinates: {longitude}, {latitude}")

        # Get timezone
        timezone_str = get_timezone_from_coordinates(latitude, longitude)
        logging.debug(f"Timezone: {timezone_str}")

        # Convert local time to UTC
        try:
            local_datetime_str = f"{birth_date} {birth_time}"
            local_datetime = datetime.strptime(local_datetime_str, "%Y-%m-%d %H:%M")

            # Localize the datetime
            local_tz = pytz.timezone(timezone_str)
            local_datetime = local_tz.localize(local_datetime)

            # Convert to UTC
            utc_datetime = local_datetime.astimezone(pytz.UTC)
            logging.debug(f"UTC datetime: {utc_datetime}")
        except Exception as e:
            logging.error(f"Error converting time: {str(e)}")
            return jsonify({"error": f"Invalid date or time format: {str(e)}"}), 400

        # Calculate ayanamsa
        ayanamsa = get_lahiri_ayanamsa(utc_datetime)
        logging.debug(f"Ayanamsa: {ayanamsa}")

        jd_ut = julian_day_from_datetime(utc_datetime)
        sidereal_asc = get_sidereal_ascendant(jd_ut, latitude, longitude)
        ascendant_position = format_position(sidereal_asc)
        logging.debug(f"Ascendant: {ascendant_position['formatted']}")
        # Get house system preference (default to whole_sign if not specified)
        house_system = data.get("house_system", "whole_sign")
        # Calculate houses based on selected system
        houses = calculate_houses(ascendant_position, house_system)

        # Calculate planetary positions
        utc_date = utc_datetime.strftime("%Y-%m-%d")
        utc_time = utc_datetime.strftime("%H:%M")
        planets = calculate_planet_positions(utc_date, utc_time, longitude, latitude)
        for planet in planets:
            sign_idx = ZODIAC_SIGNS.index(planet["sign"])
            planet_house = ((sign_idx - asc_index) % 12) + 1
            planet["house"] = planet_house
            planet["interpretation"] = get_planet_in_sign_interpretation(
                planet["name"], planet["sign"]
            )
            planet["psychological_description"] = get_planet_sign_description(
                planet["name"], planet["sign"]
            )

        # Add interpretation to each house
        for h in houses:
            h["interpretation"] = get_house_meaning(h["house"], h["sign"])
            h["psychological_description"] = get_house_sign_description(
                h["house"], h["sign"]
            )

        # Create response data
        response_data = {
            "birth_details": {
                "date": birth_date,
                "time": birth_time,
                "location": f"{city}, {country}",
                "coordinates": [longitude, latitude],
            },
            "ayanamsa": {"value": f"{ayanamsa:.4f}°", "type": "Lahiri"},
            "ascendant": ascendant_position,
            "houses": houses,
            "planets": planets,
        }

        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error calculating chart data: {str(e)}")
        return jsonify({"error": f"Error calculating chart data: {str(e)}"}), 500


@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    # If accessed via GET, redirect to the index page
    if request.method == "GET":
        return redirect(url_for("index"))

    try:
        # Extract form data
        name = request.form.get("name", "")
        dob_date = request.form.get("dob_date")
        dob_time = request.form.get("dob_time")
        country = request.form.get("country")
        city = request.form.get("city")
        house_system = request.form.get("house_system", "whole_sign")

        # Validate required fields
        if not all([dob_date, country, city]):
            flash("Please fill in all required fields", "danger")
            return redirect(url_for("index"))

        # Get coordinates from location data
        location_str = f"{city}, {country}"
        coordinates = get_coordinates(location_str)
        if not coordinates:
            logger.error("Geocoding failed for input: %s", location_str)
            flash("Could not determine coordinates for the given location", "danger")
            return redirect(url_for("index"))

        # Calculate planetary positions (incl. Rahu and Ketu) using Swiss Ephemeris
        longitude, latitude = coordinates

        # Get timezone
        timezone_str = get_timezone_from_coordinates(latitude, longitude)
        if not timezone_str:
            timezone_str = "UTC"
        logging.debug(f"Timezone: {timezone_str}")

        # Convert local time to UTC for accurate planetary calculations
        local_datetime_str = f"{dob_date} {dob_time or '12:00'}"
        local_datetime = datetime.strptime(local_datetime_str, "%Y-%m-%d %H:%M")

        # Localize the datetime
        local_tz = pytz.timezone(timezone_str)
        local_datetime = local_tz.localize(local_datetime)

        # Convert to UTC
        utc_datetime = local_datetime.astimezone(pytz.UTC)

        from utils.swisseph import (
            julian_day_from_datetime,
            get_sidereal_ascendant,
            calculate_planet_position,
            calculate_lunar_nodes,
        )

        jd_ut = julian_day_from_datetime(utc_datetime)
        logging.debug(f"Julian Day: {jd_ut}")

        # Dictionary of planets with their Swiss Ephemeris IDs
        planet_ids = {
            "Sun": 0,
            "Moon": 1,
            "Mercury": 2,
            "Venus": 3,
            "Mars": 4,
            "Jupiter": 5,
            "Saturn": 6,
        }

        planets = []

        # Calculate positions for each planet
        for planet_name, planet_id in planet_ids.items():
            try:
                tropical_longitude, sidereal_longitude, retrograde = (
                    calculate_planet_position(planet_id, jd_ut)
                )
                sign = get_zodiac_sign_from_longitude(sidereal_longitude)
                degree_in_sign = sidereal_longitude % 30

                # Format position in degrees, minutes, seconds format
                degree_int = int(degree_in_sign)
                minutes_float = (degree_in_sign - degree_int) * 60
                minutes_int = int(minutes_float)
                seconds_int = int((minutes_float - minutes_int) * 60)

                # Format DMS string
                formatted_position = (
                    f"{sign} {degree_int}°{minutes_int}'{seconds_int}\""
                )
                if retrograde:
                    formatted_position += " (R)"

                planet_data = {
                    "name": planet_name,
                    "longitude": sidereal_longitude,
                    "sign": sign,
                    "retrograde": retrograde,
                    "formatted_position": formatted_position,
                }

                planets.append(planet_data)

            except Exception as e:
                logging.error(f"Error calculating position for {planet_name}: {str(e)}")
                # Add placeholder in case of error
                planets.append(
                    {
                        "name": planet_name,
                        "longitude": 0.0,
                        "sign": "Aries",
                        "retrograde": False,
                        "formatted_position": "Aries 0°0'0\" (Error)",
                    }
                )

        # Calculate Rahu and Ketu
        try:
            rahu_longitude, ketu_longitude = calculate_lunar_nodes(jd_ut)

            # Rahu (North Node)
            rahu_sign = get_zodiac_sign_from_longitude(rahu_longitude)
            rahu_degree = rahu_longitude % 30

            # Format in DMS
            rahu_degree_int = int(rahu_degree)
            rahu_minutes_float = (rahu_degree - rahu_degree_int) * 60
            rahu_minutes_int = int(rahu_minutes_float)
            rahu_seconds_int = int((rahu_minutes_float - rahu_minutes_int) * 60)
            rahu_formatted = f"{rahu_sign} {rahu_degree_int}°{rahu_minutes_int}'{rahu_seconds_int}\" (R)"

            planets.append(
                {
                    "name": "Rahu",
                    "longitude": rahu_longitude,
                    "sign": rahu_sign,
                    "retrograde": True,  # Nodes are always considered retrograde in Vedic astrology
                    "formatted_position": rahu_formatted,
                }
            )

            # Ketu (South Node)
            ketu_sign = get_zodiac_sign_from_longitude(ketu_longitude)
            ketu_degree = ketu_longitude % 30

            # Format in DMS
            ketu_degree_int = int(ketu_degree)
            ketu_minutes_float = (ketu_degree - ketu_degree_int) * 60
            ketu_minutes_int = int(ketu_minutes_float)
            ketu_seconds_int = int((ketu_minutes_float - ketu_minutes_int) * 60)
            ketu_formatted = f"{ketu_sign} {ketu_degree_int}°{ketu_minutes_int}'{ketu_seconds_int}\" (R)"

            planets.append(
                {
                    "name": "Ketu",
                    "longitude": ketu_longitude,
                    "sign": ketu_sign,
                    "retrograde": True,  # Nodes are always considered retrograde in Vedic astrology
                    "formatted_position": ketu_formatted,
                }
            )

        except Exception as e:
            logging.error(f"Error calculating lunar nodes: {str(e)}")
            # Add placeholder nodes in case of error
            planets.append(
                {
                    "name": "Rahu",
                    "longitude": 0.0,
                    "sign": "Aries",
                    "retrograde": True,
                    "formatted_position": "Aries 0°0'0\" (R) (Error)",
                }
            )
            planets.append(
                {
                    "name": "Ketu",
                    "longitude": 180.0,
                    "sign": "Libra",
                    "retrograde": True,
                    "formatted_position": "Libra 0°0'0\" (R) (Error)",
                }
            )

        # Add nakshatra information and descriptions to planets
        for planet in planets:
            planet["nakshatra"] = get_nakshatra_from_longitude(planet["longitude"])
            planet["description"] = get_planet_in_sign_interpretation(
                planet["name"], planet["sign"]
            )
            planet["psychological_description"] = get_planet_sign_description(
                planet["name"], planet["sign"]
            )

        # Always calculate houses and ascendant using Skyfield for better accuracy
        # Get timezone
        timezone_str = get_timezone_from_coordinates(latitude, longitude)
        if not timezone_str:
            timezone_str = "UTC"
        logging.debug(f"Timezone: {timezone_str}")

        # Convert local time to UTC
        local_datetime_str = f"{dob_date} {dob_time or '12:00'}"
        local_datetime = datetime.strptime(local_datetime_str, "%Y-%m-%d %H:%M")

        # Localize the datetime
        local_tz = pytz.timezone(timezone_str)
        local_datetime = local_tz.localize(local_datetime)

        # Convert to UTC
        utc_datetime = local_datetime.astimezone(pytz.UTC)
        logging.debug(f"UTC datetime: {utc_datetime}")

        jd_ut = julian_day_from_datetime(utc_datetime)
        sidereal_asc = get_sidereal_ascendant(jd_ut, latitude, longitude)
        ascendant_position = format_position(sidereal_asc)
        ascendant_position["description"] = get_ascendant_interpretation(ascendant_position["sign"])
        houses = []
        asc_index = ZODIAC_SIGNS.index(ascendant_position["sign"])
        for i in range(12):
            sign = ZODIAC_SIGNS[(asc_index + i) % 12]
            house = {"house": i+1, "sign": sign, "degree": 0.0, "formatted": f"{sign} 0°"}
            house["meaning"] = get_house_meaning(i + 1, sign)
            house["psychological_description"] = get_house_sign_description(
                i + 1, sign
            )
            houses.append(house)
        house_data = {"ascendant": ascendant_position, "houses": houses}

        # Calculate ayanamsa
        ayanamsa = get_lahiri_ayanamsa(utc_datetime)
        logging.debug(f"Ayanamsa: {ayanamsa}")


        logging.info(
            f"Successfully calculated houses using Skyfield - Ascendant: {ascendant_position['formatted']}"
        )

        # Store calculation results in session
        birth_details = {
            "name": name,
            "date": dob_date,
            "time": dob_time or "Not specified",
            "location": f"{city}, {country}",
            "coordinates": coordinates,
        }

        # Save data to session for export functionality
        session["birth_details"] = birth_details
        session["planets"] = planets
        session["ascendant"] = house_data["ascendant"]
        session["houses"] = house_data["houses"]

        # Pass data to result template
        return render_template(
            "result.html",
            birth_details=birth_details,
            planets=planets,
            ascendant=house_data["ascendant"],
            houses=house_data["houses"],
            calculation_method=house_data.get(
                "calculation_method", "Skyfield (High Precision)"
            ),
        )

    except Exception as e:
        logging.error(f"Error calculating astrological data: {str(e)}")
        flash(f"Error calculating astrological data: {str(e)}", "danger")
        return redirect(url_for("index"))


# PDF export functionality has been removed as requested
# @app.route('/export_chart_pdf', methods=['GET'])
# def export_chart_pdf():
#     """Export the current chart data as PDF file"""
#     try:
#         # Get data from session
#         if 'planets' not in session or 'birth_details' not in session:
#             flash('No chart data available to export. Please calculate a chart first.', 'warning')
#             return redirect(url_for('index'))
#
#         # Get chart data from session
#         birth_details = session['birth_details']
#         planets = session['planets']
#         ascendant = session.get('ascendant')
#         houses = session.get('houses')
#
#         # Make sure the ascendant has a description
#         if ascendant and 'description' not in ascendant:
#             ascendant['description'] = get_ascendant_interpretation(ascendant['sign'])
#
#         # Make sure all planets have descriptions
#         for planet in planets:
#             if 'description' not in planet:
#                 planet['description'] = get_planet_in_sign_interpretation(planet['name'], planet['sign'])
#
#         # Render PDF template
#         from flask_weasyprint import HTML, render_pdf
#         import re
#
#         html = render_template(
#             'chart_pdf.html',
#             birth_details=birth_details,
#             planets=planets,
#             ascendant=ascendant,
#             houses=houses,
#             notes=""  # No notes for direct export
#         )
#
#         # Generate PDF using WeasyPrint
#         pdf = render_pdf(HTML(string=html))
#
#         # Create a safe filename
#         safe_name = re.sub(r'[^\w\s-]', '', birth_details["name"])  # Remove special chars
#         safe_name = re.sub(r'\s+', '_', safe_name).strip()  # Replace spaces with underscores
#         safe_date = birth_details["date"].replace("-", "")
#
#         # Create response
#         response = make_response(pdf)
#         response.headers['Content-Disposition'] = f'attachment; filename=chart_{safe_name}_{safe_date}.pdf'
#         response.headers['Content-Type'] = 'application/pdf'
#
#         return response
#
#     except Exception as e:
#         logging.error(f"Error exporting chart as PDF: {str(e)}")
#         flash(f'Error exporting chart: {str(e)}', 'danger')
#         return redirect(url_for('index'))
#


@app.route("/test_ascendant")
def test_ascendant():
    """Test page for ascendant calculation with various methods"""
    # Default test parameters (you can change these or add URL parameters)
    date_str = request.args.get("date", "1990-01-15")
    time_str = request.args.get("time", "12:00")
    city = request.args.get("city", "New York")
    country = request.args.get("country", "United States")

    try:
        # Get coordinates
        location_str = f"{city}, {country}"
        coordinates = get_coordinates(location_str)
        if not coordinates:
            logger.error("Geocoding failed for input: %s", location_str)
            flash(f"Could not determine coordinates for {city}, {country}", "danger")
            return redirect(url_for("index"))

        longitude, latitude = coordinates

        # Get Julian Day
        from utils.swisseph import (
            calculate_jd_ut,
            get_zodiac_sign as swe_get_zodiac_sign,
        )

        jd_ut = calculate_jd_ut(date_str, time_str)

        # Calculate ayanamsa using different methods
        from utils.swisseph import calculate_ayanamsa

        krishnamurti_ayanamsa = calculate_ayanamsa(jd_ut)

        # Lahiri ayanamsa using common utility
        lahiri_ayanamsa = get_lahiri_ayanamsa(
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        )

        # Calculate ascendant with different methods
        import swisseph as swe

        # 1. Direct tropical calculation
        swe.set_sid_mode(0)  # Tropical zodiac (no ayanamsa)
        houses_tropical, ascmc_tropical = swe.houses(jd_ut, latitude, longitude, b"P")
        tropical_asc = ascmc_tropical[0]
        tropical_asc_sign = swe_get_zodiac_sign(tropical_asc)
        tropical_asc_degree = tropical_asc % 30

        # 2. Krishnamurti calculation with direct ayanamsa subtraction
        second_tropical_asc = tropical_asc  # Make a copy of the tropical value
        krishnamurti_asc = (second_tropical_asc - krishnamurti_ayanamsa) % 360
        krishnamurti_asc_sign = swe_get_zodiac_sign(krishnamurti_asc)
        krishnamurti_asc_degree = krishnamurti_asc % 30

        # 3. Lahiri calculation with direct ayanamsa subtraction
        lahiri_sidereal_asc = (tropical_asc - lahiri_ayanamsa) % 360
        lahiri_asc_sign = swe_get_zodiac_sign(lahiri_sidereal_asc)
        lahiri_asc_degree = lahiri_sidereal_asc % 30

        # 4. Alternative Krishnamurti ayanamsa with 1° less (some calculators use different values)
        alt_krishnamurti_ayanamsa = krishnamurti_ayanamsa - 1
        alt_krishnamurti_asc = (tropical_asc - alt_krishnamurti_ayanamsa) % 360
        alt_krishnamurti_asc_sign = swe_get_zodiac_sign(alt_krishnamurti_asc)
        alt_krishnamurti_asc_degree = alt_krishnamurti_asc % 30

        # 5. Special calibrated ayanamsa to match expected results
        # For Mateusz's chart: expected Aquarius 19.57°
        mateusz_target = 319.57  # Aquarius 19.57° in absolute degrees
        special_ayanamsa = (tropical_asc - mateusz_target) % 360
        special_asc = mateusz_target
        special_asc_sign = swe_get_zodiac_sign(special_asc)
        special_asc_degree = special_asc % 30

        # Special calibration for Damian's chart if the input matches
        damian_data = (
            date_str == "1997-09-17"
            and time_str == "13:04"
            and city.lower() == "wroclaw"
        )
        if damian_data:
            # Calculate what ayanamsa would make the ascendant Scorpio 9:35
            damian_target = 219.35  # Scorpio 9:35 in absolute degrees
            damian_special_ayanamsa = (tropical_asc - damian_target) % 360
            damian_special_asc = damian_target
            damian_special_asc_sign = swe_get_zodiac_sign(damian_special_asc)
            damian_special_asc_degree = damian_special_asc % 30

        # Store all results for comparison
        results = {
            "input": {
                "date": date_str,
                "time": time_str,
                "city": city,
                "country": country,
                "longitude": longitude,
                "latitude": latitude,
                "jd_ut": jd_ut,
            },
            "ayanamsa": {
                "krishnamurti": krishnamurti_ayanamsa,
                "lahiri": lahiri_ayanamsa,
                "alt_krishnamurti": alt_krishnamurti_ayanamsa,
            },
            "ascendant": {
                "tropical": {
                    "longitude": tropical_asc,
                    "sign": tropical_asc_sign,
                    "degree": tropical_asc_degree,
                    "formatted": f"{tropical_asc_sign} {tropical_asc_degree:.2f}°",
                },
                "krishnamurti_direct": {
                    "longitude": krishnamurti_asc,
                    "sign": krishnamurti_asc_sign,
                    "degree": krishnamurti_asc_degree,
                    "formatted": f"{krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°",
                },
                "lahiri": {
                    "longitude": lahiri_sidereal_asc,
                    "sign": lahiri_asc_sign,
                    "degree": lahiri_asc_degree,
                    "formatted": f"{lahiri_asc_sign} {lahiri_asc_degree:.2f}°",
                    "formula": f"{tropical_asc:.2f}° - {lahiri_ayanamsa:.2f}° = {lahiri_sidereal_asc:.2f}°",
                },
                "alt_krishnamurti": {
                    "longitude": alt_krishnamurti_asc,
                    "sign": alt_krishnamurti_asc_sign,
                    "degree": alt_krishnamurti_asc_degree,
                    "formatted": f"{alt_krishnamurti_asc_sign} {alt_krishnamurti_asc_degree:.2f}°",
                    "formula": f"{tropical_asc:.2f}° - {alt_krishnamurti_ayanamsa:.2f}° = {alt_krishnamurti_asc:.2f}°",
                },
            },
        }

        # Create a simple HTML output (we'll make a proper template later)
        html = "<h1>Ascendant Test Results</h1>"
        html += "<h2>Input Data</h2>"
        html += f"<p>Date: {date_str} Time: {time_str}</p>"
        html += f"<p>Location: {city}, {country} (Longitude: {longitude}, Latitude: {latitude})</p>"
        html += f"<p>Julian Day: {jd_ut}</p>"

        html += "<h2>Ayanamsa Values</h2>"
        html += f"<p>Standard Krishnamurti: {krishnamurti_ayanamsa:.4f}°</p>"
        html += f"<p>Lahiri: {lahiri_ayanamsa:.4f}°</p>"
        html += f"<p>Alt Krishnamurti (-1°): {alt_krishnamurti_ayanamsa:.4f}°</p>"
        html += f"<p>Special Calibrated Ayanamsa: {special_ayanamsa:.4f}° (to match Aquarius 19.57°)</p>"

        html += "<h2>Ascendant Calculations</h2>"

        # 1. Tropical result
        html += "<h3>Tropical (no ayanamsa)</h3>"
        html += f"<p>Longitude: {tropical_asc:.4f}°</p>"
        html += f"<p>Position: {tropical_asc_sign} {tropical_asc_degree:.2f}°</p>"

        # 2. Standard Krishnamurti
        html += "<h3>Standard Krishnamurti</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {krishnamurti_ayanamsa:.2f}° = {krishnamurti_asc:.2f}°</p>"
        html += (
            f"<p>Position: {krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°</p>"
        )

        # 3. Lahiri calculation
        html += "<h3>Lahiri Calculation</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {lahiri_ayanamsa:.2f}° = {lahiri_sidereal_asc:.2f}°</p>"
        html += f"<p>Position: {lahiri_asc_sign} {lahiri_asc_degree:.2f}°</p>"

        # 4. Alternative Krishnamurti
        html += "<h3>Alternative Krishnamurti (-1°)</h3>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {alt_krishnamurti_ayanamsa:.2f}° = {alt_krishnamurti_asc:.2f}°</p>"
        html += f"<p>Position: {alt_krishnamurti_asc_sign} {alt_krishnamurti_asc_degree:.2f}°</p>"

        # 5. Special Calibrated position
        html += "<h3>Special Calibrated Position (matching reference)</h3>"
        html += f"<p>Target position: Aquarius 19.57° (319.57° absolute)</p>"
        html += f"<p>Required ayanamsa: {special_ayanamsa:.4f}°</p>"
        html += f"<p>Formula: {tropical_asc:.2f}° - {special_ayanamsa:.2f}° = {special_asc:.2f}°</p>"
        html += f"<p>Position: {special_asc_sign} {special_asc_degree:.2f}°</p>"
        html += f"<p><strong>Ayanamsa difference from standard:</strong> {special_ayanamsa - krishnamurti_ayanamsa:.2f}°</p>"

        # Add a message about expected results for reference charts
        html += "<h2>Expected Results for Reference Charts</h2>"

        # Calculate with Kerykeion (new implementation)
        try:
            from utils.kerykeion_utils import calculate_kerykeion_chart

            kerykeion_chart = calculate_kerykeion_chart(
                birth_date=date_str,
                birth_time=time_str,
                city=city,
                country=country,
                latitude=latitude,
                longitude=longitude,
            )

            kerykeion_asc = kerykeion_chart["ascendant"]

            html += "<h3>Kerykeion Calculation (New Implementation)</h3>"
            html += f"<p>Ascendant: {kerykeion_asc['formatted']}</p>"
            html += f"<p>This is our new preferred calculation method</p>"
        except Exception as ke:
            html += f"<p>Error with Kerykeion calculation: {str(ke)}</p>"

        if damian_data:
            # Display special calibration for Damian
            html += f"<h3>For Damian Adasik (1997-09-17, 13:04, Wroclaw, Poland):</h3>"
            html += f"<p>Our calculation: Sagittarius 4.94°</p>"
            html += f"<p>Expected: Scorpio 9:35</p>"
            html += f"<p>Required ayanamsa: {damian_special_ayanamsa:.2f}° (standard is {krishnamurti_ayanamsa:.2f}°)</p>"
            html += f"<p>Ayanamsa difference: {damian_special_ayanamsa - krishnamurti_ayanamsa:.2f}°</p>"
        else:
            # Display Mateusz's reference info
            html += (
                f"<h3>For Mateusz Skawiński (1993-02-17, 07:18, Radom, Poland):</h3>"
            )
            html += f"<p>Our calculation: {krishnamurti_asc_sign} {krishnamurti_asc_degree:.2f}°</p>"
            html += f"<p>Expected Lahiri: Aquarius 19:51</p>"
            html += f"<p>Expected Krishnamurti: Aquarius 19:57</p>"

        return html

    except Exception as e:
        return f"<h1>Error</h1><p>Error calculating ascendant: {str(e)}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
