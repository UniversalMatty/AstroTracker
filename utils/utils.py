from datetime import datetime
import logging

REFERENCE_DATE = datetime(1950, 1, 1)
REFERENCE_AYANAMSA = 23.15
SECONDS_PER_YEAR = 50.3 / 3600.0  # 50.3" in degrees


def get_lahiri_ayanamsa(date):
    """Return the Lahiri ayanamsa for ``date``.

    Parameters
    ----------
    date : datetime or str
        Date for which to compute the ayanamsa. Strings are parsed using
        ``datetime.fromisoformat`` or ``%Y-%m-%d``.
    """
    try:
        if isinstance(date, str):
            try:
                dt = datetime.fromisoformat(date)
            except ValueError:
                dt = datetime.strptime(date, "%Y-%m-%d")
        else:
            dt = date

        ref = REFERENCE_DATE
        if dt.tzinfo is not None:
            ref = ref.replace(tzinfo=dt.tzinfo)
        days_diff = (dt - ref).days
        years_diff = days_diff / 365.25
        return REFERENCE_AYANAMSA + (years_diff * SECONDS_PER_YEAR * 365.25)
    except Exception as exc:
        logging.error(f"Error calculating Lahiri ayanamsa: {exc}")
        return REFERENCE_AYANAMSA
