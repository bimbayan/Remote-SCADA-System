from __future__ import annotations

from typing import Any

import requests

from config import (
    NOMINATIM_API_URL,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)


class LocationLookupError(RuntimeError):
    """Raised when a location cannot be resolved."""


class LocationService:
    """
    Resolves user-provided locations into geographical coordinates.
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": USER_AGENT,
            }
        )

    def resolve(self, query: str) -> LocationResult:
        """
        Resolve a location name into latitude and longitude.
        """

        query = query.strip()

        if not query:
            raise LocationLookupError("Please enter a location.")

        try:
            response = self._session.get(
                NOMINATIM_API_URL,
                params={
                    "q": query,
                    "format": "jsonv2",
                    "addressdetails": 1,
                    "limit": 1,
                    "accept-language": "en",
                },
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise LocationLookupError(
                "Unable to contact location service."
            ) from exc

        results = response.json()

        if not results:
            raise LocationLookupError(
                f"No location found for '{query}'."
            )

        result = results[0]
        address: dict[str, Any] = result.get("address", {})

        return LocationResult(
            query=query,
            display_name=result.get("display_name", query),
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            city=(
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("municipality")
            ),
            state=address.get("state"),
            country=address.get("country", "Unknown"),
        )