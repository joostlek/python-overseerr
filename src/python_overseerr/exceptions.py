"""Asynchronous Python client for Overseerr."""


class OverseerrError(Exception):
    """Generic exception."""


class OverseerrConnectionError(OverseerrError):
    """Overseerr connection exception."""


class OverseerrAuthenticationError(OverseerrError):
    """Overseerr authentication exception."""


class OverseerrNothingToRequestError(OverseerrError):
    """Raised when there is nothing left to request.

    Overseerr responds with HTTP 202 and a ``{"status", "message"}`` body
    instead of a created request when every requested season is already
    requested or available (``NoSeasonsAvailableError`` server-side).
    """
