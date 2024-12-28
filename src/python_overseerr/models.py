"""Models for Overseerr."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime  # noqa: TC003
from enum import IntEnum, IntFlag, StrEnum
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
    tmdb_id: int | None = field(metadata=field_options(alias="tmdbId"))
    tvdb_id: int | None = field(metadata=field_options(alias="tvdbId"))
    imdb_id: str | None = field(metadata=field_options(alias="imdbId"))
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
    """Result model."""

    id: int
    mediaType: MediaType  # noqa: N815 # pylint: disable=invalid-name
    media_type: MediaType = field(metadata=field_options(alias="mediaType"))


@dataclass
class Movie(Result):
    """Movie result model."""

    mediaType = MediaType.MOVIE  # noqa: N815 # pylint: disable=invalid-name
    original_language: str = field(metadata=field_options(alias="originalLanguage"))
    original_title: str = field(metadata=field_options(alias="originalTitle"))
    overview: str
    popularity: float
    title: str
    adult: bool
    media_info: MediaInfo | None = field(
        metadata=field_options(alias="mediaInfo"), default=None
    )


@dataclass
class TV(Result):
    """TV result model."""

    mediaType = MediaType.TV  # noqa: N815 # pylint: disable=invalid-name
    first_air_date: date = field(metadata=field_options(alias="firstAirDate"))
    name: str
    original_language: str = field(metadata=field_options(alias="originalLanguage"))
    original_name: str = field(metadata=field_options(alias="originalName"))
    overview: str
    popularity: float
    media_info: MediaInfo | None = field(
        metadata=field_options(alias="mediaInfo"), default=None
    )


@dataclass
class Person(Result):
    """Person result model."""

    mediaType = MediaType.PERSON  # noqa: N815 # pylint: disable=invalid-name
    name: str
    popularity: float
    known_for: list[Movie] = field(metadata=field_options(alias="knownFor"))
    adult: bool


@dataclass
class SearchResult(DataClassORJSONMixin):
    """Search result model."""

    results: list[
        Annotated[Result, Discriminator(field="mediaType", include_subtypes=True)]
    ]


class NotificationType(IntFlag):
    """Webhook notification type enum."""

    REQUEST_PENDING_APPROVAL = 2
    REQUEST_APPROVED = 4
    REQUEST_AVAILABLE = 8
    REQUEST_PROCESSING_FAILED = 16
    REQUEST_DECLINED = 64
    REQUEST_AUTOMATICALLY_APPROVED = 128
    ISSUE_REPORTED = 256
    ISSUE_COMMENT = 512
    ISSUE_RESOLVED = 1024
    ISSUE_REOPENED = 2048


@dataclass
class NotificationConfig(DataClassORJSONMixin):
    """Webhook config model."""

    enabled: bool
    types: NotificationType


@dataclass
class WebhookNotificationOptions:
    """Webhook notification options model."""

    json_payload: str = field(metadata=field_options(alias="jsonPayload"))
    webhook_url: str = field(metadata=field_options(alias="webhookUrl"))


@dataclass
class WebhookNotificationConfig(NotificationConfig):
    """Webhook config model."""

    options: WebhookNotificationOptions
