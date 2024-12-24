"""Models for Overseerr."""

from __future__ import annotations

from dataclasses import dataclass

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class RequestCount(DataClassORJSONMixin):
    """Request count model."""

    total: int
    movie: int
    tv: int
    pending: int
    approved: int
    declined: int
    processing: int
    available: int
