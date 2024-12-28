"""Models for Overseerr."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import Discriminator


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


class MediaStatus(IntEnum):
    """Media status enum."""

    UNKNOWN = 1
    PENDING = 2
    PROCESSING = 3
    PARTIALLY_AVAILABLE = 4
    AVAILABLE = 5


@dataclass
class MediaInfo(DataClassORJSONMixin):
    """Media info model."""

    id: int
    tmdb_id: int = field(metadata=field_options(alias="tmdbId"))
    tvdb_id: int = field(metadata=field_options(alias="tvdbId"))
    status: MediaStatus
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))


class MediaType(StrEnum):
    """Media type enum."""

    MOVIE = "movie"
    TV = "tv"
    PERSON = "person"


@dataclass
class Result(DataClassORJSONMixin):
    id: int
    mediaType: MediaType
    media_type: MediaType = field(metadata=field_options(alias="mediaType"))
    adult: bool


@dataclass
class MovieResult(Result):
    mediaType = MediaType.MOVIE
    original_language: str = field(metadata=field_options(alias="originalLanguage"))
    original_title: str = field(metadata=field_options(alias="originalTitle"))
    overview: str
    popularity: float
    title: str
    media_info: MediaInfo | None = field(
        metadata=field_options(alias="mediaInfo"), default=None
    )


@dataclass
class TVResult(Result):
    mediaType = MediaType.TV


@dataclass
class PersonResult(Result):
    mediaType = MediaType.PERSON


@dataclass
class SearchResult(DataClassORJSONMixin):
    results: list[
        Annotated[Result, Discriminator(field="mediaType", include_subtypes=True)]
    ]
