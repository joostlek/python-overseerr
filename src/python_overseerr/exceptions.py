"""Asynchronous Python client for Overseerr."""


class OverseerrError(Exception):
    """Generic exception."""


class OverseerrConnectionError(OverseerrError):
    """Overseerr connection exception."""


class OverseerrAuthenticationError(OverseerrError):
    """Overseerr authentication exception."""


class OverseerrMediaAlreadyAvailableError(OverseerrError):
    """Raised when there is nothing left to request.

    Overseerr responds with a 2xx status and a ``{"status", "message"}`` body
    instead of a created request when every requested season is already
    available (e.g. ``NoSeasonsAvailableError`` server-side), so this can't
    be detected from the HTTP status code alone.
    """
