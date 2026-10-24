import requests

from django.conf import settings
from django.core.cache import cache


class GeocodingError(Exception):
    pass


def reverse_geocode(*, latitude, longitude):
    cache_key = (
        f"reverse_geocode:"
        f"{round(latitude, 5)}:"
        f"{round(longitude, 5)}"
    )

    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    response = requests.get(
        f"{settings.GEOCODING_BASE_URL}/reverse",
        params={
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        },
        headers={
            "User-Agent": settings.GEOCODING_USER_AGENT,
        },
        timeout=5,
    )

    if response.status_code != 200:
        raise GeocodingError(
            "Could not determine the location name."
        )

    data = response.json()

    location_name = _format_location_name(data)

    cache.set(
        cache_key,
        location_name,
        timeout=60 * 60 * 24,
    )

    return location_name


def _format_location_name(data):
    address = data.get("address", {})

    local_area = (
        address.get("neighbourhood")
        or address.get("suburb")
        or address.get("quarter")
        or address.get("road")
    )

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
    )

    state = address.get("state")

    parts = []

    for part in (local_area, city, state):
        if part and part not in parts:
            parts.append(part)

    if parts:
        return ", ".join(parts)

    return data.get("display_name", "Selected location")