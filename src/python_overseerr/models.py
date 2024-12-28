"""Models for Overseerr."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options
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


@dataclass
class Status(DataClassORJSONMixin):
    """Status model."""

    version: str
    update_available: bool = field(metadata=field_options(alias="updateAvailable"))
    commits_behind: int = field(metadata=field_options(alias="commitsBehind"))
    restart_required: bool = field(metadata=field_options(alias="restartRequired"))
