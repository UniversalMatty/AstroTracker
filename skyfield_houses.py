from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
import math
from timezonefinder import TimezoneFinder
import pytz
from skyfield.api import load, Topos
import numpy as np

from utils.geocoding import get_coordinates
from utils.astronomy import calculate_planet_positions
from utils.utils import get_lahiri_ayanamsa

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load the ephemeris file
try:
    logger.info("Loading ephemeris file de440s.bsp...")
    eph = load("de440s.bsp")
    logger.info("Ephemeris loaded successfully")
except Exception as e:
    logger.error(f"Error loading ephemeris: {str(e)}")
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


def get_nakshatra(longitude):
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


def get_zodiac_sign(longitude):
    """Get zodiac sign from longitude in degrees (0-360)"""
    sign_index = int(longitude / 30)
    return ZODIAC_SIGNS[sign_index % 12]


def format_position(longitude, retrograde=False):
    """Format position with zodiac sign and degree"""
    sign = get_zodiac_sign(longitude)
    degree = longitude % 30
    nakshatra = get_nakshatra(longitude)
    r_symbol = " (R)" if retrograde else ""
    return {
        "longitude": longitude,
        "sign": sign,
        "degree": degree,
        "formatted": f"{degree:.2f}° {sign}{r_symbol}",
        "nakshatra": nakshatra,
        "full_description": f"{degree:.2f}° {sign} – {nakshatra['name']} ({nakshatra['ruling_planet']}){r_symbol}",
    }


def local_to_utc(date_str, time_str, timezone_str):
    """Convert local time to UTC using pytz."""
    try:
        # Parse date and time strings
        local_dt_str = f"{date_str} {time_str}"
        local_dt = datetime.strptime(local_dt_str, "%Y-%m-%d %H:%M")

        # Get timezone
        local_tz = pytz.timezone(timezone_str)

        # Localize the datetime (add timezone info)
        local_dt = local_tz.localize(local_dt)

        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.UTC)

        logger.debug(f"Converted {local_dt} ({timezone_str}) to UTC: {utc_dt}")
        return utc_dt
    except Exception as e:
        logger.error(f"Error converting time to UTC: {str(e)}")
        raise


def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates using timezonefinder."""
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if timezone_str is None:
            logger.warning(
                f"Could not find timezone for coordinates ({latitude}, {longitude}). Using UTC."
            )
            return "UTC"
        logger.debug(
            f"Found timezone {timezone_str} for coordinates ({latitude}, {longitude})"
        )
        return timezone_str
    except Exception as e:
        logger.error(f"Error finding timezone: {str(e)}")
        return "UTC"  # Fallback to UTC


def calculate_ascendant(t, observer):
    """
    Calculate the ascendant (rising sign) using Skyfield.

    Args:
        t: Skyfield Time object
        observer: Skyfield Topos object for the observer's location

    Returns:
        Tropical longitude of the ascendant in degrees
    """
    try:
        # Get sidereal time at Greenwich
        gst = t.gast * 15  # Convert hours to degrees

        # Adjust for observer's longitude to get local sidereal time (LST)
        lst = (gst + observer.longitude.degrees) % 360

        # The tropical ascendant is the point of the ecliptic that is rising
        # This is a simplified calculation that works well for most locations
        latitude_rad = math.radians(observer.latitude.degrees)

        # Calculate obliquity of the ecliptic
        # This is a simplified formula good for current epoch
        epsilon = math.radians(23.44)  # Obliquity in radians

        # Calculate ascendant
        tan_asc = math.cos(math.radians(lst)) / (
            math.sin(math.radians(lst)) * math.cos(epsilon)
            - math.tan(latitude_rad) * math.sin(epsilon)
        )

        ascendant_rad = math.atan(tan_asc)

        # Convert to degrees and ensure it's in the correct quadrant
        ascendant_deg = math.degrees(ascendant_rad)

        # Adjust quadrant based on LST
        if 90 <= lst < 270:
            ascendant_deg += 180

        # Ensure the result is between 0 and 360
        ascendant_deg = (ascendant_deg + 360) % 360

        logger.debug(f"Calculated tropical ascendant: {ascendant_deg:.2f}°")
        return ascendant_deg
    except Exception as e:
        logger.error(f"Error calculating ascendant: {str(e)}")
        # Return a default value in case of error
        return 0.0


# Calculate houses in the Whole Sign system
def calculate_whole_sign_houses(ascendant_position):
    """
    Calculate house cusps using the Whole Sign system.
    In this system, the sign containing the ascendant becomes the 1st house,
    and each subsequent sign becomes the next house.

    Args:
        ascendant_position: Dictionary with ascendant details

    Returns:
        List of house dictionaries, each with sign and other details
    """
    try:
        # Get the sign of the ascendant
        asc_sign = ascendant_position["sign"]
        asc_sign_num = ZODIAC_SIGNS.index(asc_sign)

        houses = []
        for i in range(1, 13):  # 12 houses
            # Each house is an entire sign
            house_sign_num = (asc_sign_num + i - 1) % 12
            house_sign = ZODIAC_SIGNS[house_sign_num]

            houses.append(
                {
                    "house": i,
                    "sign": house_sign,
                    "degree": 0.0,  # Whole sign houses start at 0° of the sign
                    "formatted": f"{house_sign} 0.00°",
                }
            )

        return houses
    except Exception as e:
        logger.error(f"Error calculating whole sign houses: {str(e)}")
        # Return a basic template in case of error
        return [
            {"house": i, "sign": "Unknown", "degree": 0.0, "formatted": "Unknown 0.00°"}
            for i in range(1, 13)
        ]


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Calculate ascendant and houses for a given birth details.

    Expected JSON input:
    {
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM",
        "city": "City Name",
        "country": "Country Name"
    }
    """
    try:
        # Get JSON data from request
        data = request.json

        # Validate required fields
        required_fields = ["birth_date", "city", "country"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract fields
        birth_date = data["birth_date"]
        birth_time = data.get("birth_time", "12:00")  # Default to noon if not provided
        city = data["city"]
        country = data["country"]

        logger.debug(
            f"Received request for birth_date={birth_date}, birth_time={birth_time}, city={city}, country={country}"
        )

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
        logger.debug(
            f"Geocoded {city}, {country} to coordinates: ({latitude}, {longitude})"
        )

        # Get timezone
        timezone_str = get_timezone_from_coordinates(latitude, longitude)

        # Convert local time to UTC
        utc_dt = local_to_utc(birth_date, birth_time, timezone_str)

        # Create Skyfield time object
        t = ts.from_datetime(utc_dt)

        # Create observer object
        observer = earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude)

        # Calculate ayanamsa (Lahiri)
        ayanamsa = get_lahiri_ayanamsa(utc_dt)
        logger.debug(f"Calculated Lahiri ayanamsa: {ayanamsa:.2f}°")

        # Calculate ascendant using Skyfield
        tropical_asc = calculate_ascendant(t, observer)
        sidereal_asc = (tropical_asc - ayanamsa) % 360
        ascendant = format_position(sidereal_asc)

        # Calculate houses using Whole Sign system
        houses = calculate_whole_sign_houses(ascendant)

        # Format response
        response = {
            "birth_details": {
                "date": birth_date,
                "time": birth_time,
                "location": f"{city}, {country}",
                "coordinates": {"latitude": latitude, "longitude": longitude},
            },
            "ayanamsa": {"type": "Lahiri", "value": f"{ayanamsa:.2f}°"},
            "ascendant": ascendant,
            "houses": houses,
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/calculate_full_chart", methods=["POST"])
def calculate_full_chart():
    """
    Calculate a complete astrological chart including ascendant, houses,
    and planetary positions. Uses Skyfield for ascendant and houses,
    but keeps the existing methods for planetary positions.

    Expected JSON input:
    {
        "birth_date": "YYYY-MM-DD",
        "birth_time": "HH:MM",
        "city": "City Name",
        "country": "Country Name"
    }
    """
    try:
        # First get the ascendant and houses calculation
        ascendant_houses_result = calculate()
        if isinstance(ascendant_houses_result, tuple):
            # If we got an error response, return it
            return ascendant_houses_result

        # Extract the data from the calculation result
        data = ascendant_houses_result.json

        # Now calculate planetary positions using the existing method
        try:
            birth_date = data["birth_details"]["date"]
            birth_time = data["birth_details"]["time"]
            longitude = data["birth_details"]["coordinates"]["longitude"]
            latitude = data["birth_details"]["coordinates"]["latitude"]

            planets = calculate_planet_positions(
                birth_date, birth_time, longitude, latitude
            )

            # Convert planet format to match our API format
            formatted_planets = {}
            for planet in planets:
                planet_name = planet["name"]

                # Skip if we already have this planet
                if planet_name in formatted_planets:
                    continue

                formatted_planets[planet_name] = {
                    "longitude": planet["longitude"],
                    "sign": planet["sign"],
                    "degree": planet["longitude"] % 30,
                    "formatted": f"{planet['longitude'] % 30:.2f}° {planet['sign']}",
                    "retrograde": planet.get("retrograde", False),
                    "nakshatra": planet.get("nakshatra", {}),
                }

            # Add the planet information to the response
            data["planets"] = formatted_planets

        except Exception as e:
            logger.error(f"Error calculating planetary positions: {str(e)}")
            # If planetary calculations fail, still return the ascendant and houses
            data["planets"] = {}
            data["warning"] = "Could not calculate planetary positions"

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error calculating chart: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/skyfield_form")
def skyfield_form():
    """Render the form for Skyfield calculations"""
    return app.send_static_file("skyfield_form.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
