import logging
import os

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError


def get_coordinates(location: str):
    """Return (longitude, latitude) for the given location string.

    Parameters
    ----------
    location: str
        Location string including both city and country, e.g. ``"Warsaw, Poland"``.
        Frontend users should pass both city and country for best accuracy.
    """

    user_agent = os.getenv("GEOPY_USER_AGENT", "astrotracker_app")
    geolocator = Nominatim(user_agent=user_agent)

    try:
        result = geolocator.geocode(location)
        if result:
            latitude = float(result.latitude)
            longitude = float(result.longitude)
            logging.debug(
                "Found coordinates for %s: %s, %s", location, longitude, latitude
            )
            return (longitude, latitude)
        else:
            logging.warning("No coordinates found for location input: %s", location)
            return None
    except GeocoderServiceError as exc:
        logging.error("Geocoder service error for '%s': %s", location, exc)
        return None
    except Exception as exc:  # pragma: no cover - unexpected errors
        logging.error("Error getting coordinates for '%s': %s", location, exc)
        return None
