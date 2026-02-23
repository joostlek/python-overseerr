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
class IssueCount(DataClassORJSONMixin):
    """Issue count model."""

    total: int
    video: int
    audio: int
    subtitles: int
    others: int
    open: int
    closed: int


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
    media_type: MediaType = field(metadata=field_options(alias="mediaType"))
    status: MediaStatus
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))


class ResultMediaType(StrEnum):
    """Media type enum."""

    MOVIE = "movie"
    TV = "tv"
    PERSON = "person"


class MediaType(StrEnum):
    """Media type enum."""

    MOVIE = "movie"
    TV = "tv"


@dataclass
class Result(DataClassORJSONMixin):
    """Result model."""

    id: int
    mediaType: ResultMediaType  # noqa: N815 # pylint: disable=invalid-name
    media_type: ResultMediaType = field(metadata=field_options(alias="mediaType"))


@dataclass
class Movie(Result):
    """Movie result model."""

    mediaType = ResultMediaType.MOVIE  # noqa: N815 # pylint: disable=invalid-name
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

    mediaType = ResultMediaType.TV  # noqa: N815 # pylint: disable=invalid-name
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

    mediaType = ResultMediaType.PERSON  # noqa: N815 # pylint: disable=invalid-name
    name: str
    popularity: float
    known_for: list[Result] = field(metadata=field_options(alias="knownFor"))
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
    ISSUE_COMMENTED = 512
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


@dataclass
class User(DataClassORJSONMixin):
    """User model."""

    id: int
    email: str
    avatar: str
    username: str | None
    plex_username: str | None = field(metadata=field_options(alias="plexUsername"))
    plex_id: int | None = field(metadata=field_options(alias="plexId"))
    movie_quota_limit: int | None = field(
        metadata=field_options(alias="movieQuotaLimit")
    )
    movie_quota_days: int | None = field(metadata=field_options(alias="movieQuotaDays"))
    tv_quota_limit: int | None = field(metadata=field_options(alias="tvQuotaLimit"))
    tv_quota_days: int | None = field(metadata=field_options(alias="tvQuotaDays"))
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
    request_count: int = field(metadata=field_options(alias="requestCount"))
    display_name: str = field(metadata=field_options(alias="displayName"))
    permissions: int
    recovery_link_expiration_date: date | None = field(
        metadata=field_options(alias="recoveryLinkExpirationDate")
    )
    user_type: int | None = field(metadata=field_options(alias="userType"))
    settings: UserSettings | None = None
    warnings: list[str] = field(default_factory=list)
    jellyfin_username: str | None = field(
        metadata=field_options(alias="jellyfinUsername"), default=None
    )
    jellyfin_user_id: str | None = field(
        metadata=field_options(alias="jellyfinUserId"), default=None
    )
    avatar_e_tag: str | None = field(
        metadata=field_options(alias="avatarETag"), default=None
    )
    avatar_version: str | None = field(
        metadata=field_options(alias="avatarVersion"), default=None
    )


@dataclass
class UserSettings(DataClassORJSONMixin):
    """User settings model."""

    discord_id: str | None = field(metadata=field_options(alias="discordId"))
    discover_region: str | None = field(metadata=field_options(alias="discoverRegion"))
    id: str
    locale: str
    notification_types: str | None = field(
        metadata=field_options(alias="notificationTypes")
    )
    original_language: str | None = field(
        metadata=field_options(alias="originalLanguage")
    )
    pgp_key: str | None = field(metadata=field_options(alias="pgpKey"))
    pushbullet_access_token: str | None = field(
        metadata=field_options(alias="pushbulletAccessToken")
    )
    pushover_application_token: str | None = field(
        metadata=field_options(alias="pushoverApplicationToken")
    )
    pushover_sound: str | None = field(metadata=field_options(alias="pushoverSound"))
    pushover_user_key: str | None = field(
        metadata=field_options(alias="pushoverUserKey")
    )
    streaming_region: str | None = field(
        metadata=field_options(alias="streamingRegion")
    )
    telegram_chat_id: str | None = field(metadata=field_options(alias="telegramChatId"))
    telegram_message_thread_id: str | None = field(
        metadata=field_options(alias="telegramMessageThreadId")
    )
    telegram_send_silently: str | None = field(
        metadata=field_options(alias="telegramSendSilently")
    )
    watchlist_sync_movies: str | None = field(
        metadata=field_options(alias="watchlistSyncMovies")
    )
    watchlist_sync_tv: str | None = field(
        metadata=field_options(alias="watchlistSyncTv")
    )


class RequestFilterStatus(StrEnum):
    """Request filter status enum."""

    ALL = "all"
    APPROVED = "approved"
    AVAILABLE = "available"
    PENDING = "pending"
    PROCESSING = "processing"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class RequestSortStatus(StrEnum):
    """Request sort status enum."""

    ADDED = "added"
    MODIFIED = "modified"


class RequestStatus(IntEnum):
    """Request status enum."""

    PENDING_APPROVAL = 1
    APPROVED = 2
    DECLINED = 3
    COMPLETED = 5


@dataclass
class Request(DataClassORJSONMixin):
    """Request model."""

    id: int
    status: RequestStatus
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
    is4k: bool
    requested_by: User = field(metadata=field_options(alias="requestedBy"))
    season_count: int | None = field(
        metadata=field_options(alias="seasonCount"), default=None
    )
    modified_by: User | None = field(
        metadata=field_options(alias="modifiedBy"), default=None
    )


@dataclass(kw_only=True)
class RequestWithMedia(Request):
    """Request with media model."""

    media: MediaInfo


@dataclass
class MediaInfoWithRequests(MediaInfo):
    """Media info with requests model."""

    requests: list[Request]


@dataclass
class RequestResponse(DataClassORJSONMixin):
    """Request response model."""

    results: list[RequestWithMedia]


class IssueFilterStatus(StrEnum):
    """Issue filter status enum."""

    ALL = "all"
    OPEN = "open"
    RESOLVED = "resolved"


class IssueSortStatus(StrEnum):
    """Issue sort status enum."""

    ADDED = "added"
    MODIFIED = "modified"


class IssueStatus(IntEnum):
    """Issue status enum."""

    OPEN = 1
    RESOLVED = 2


class IssueType(IntEnum):
    """Issue status enum."""

    VIDEO = 1
    AUDIO = 2
    SUBTITLE = 3
    OTHER = 4


@dataclass
class IssueComment(DataClassORJSONMixin):
    """Issue comment model."""

    id: int
    message: str
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    user: User | None = None


@dataclass
class Issue(DataClassORJSONMixin):
    """Issue model."""

    id: int
    issue_type: IssueType = field(metadata=field_options(alias="issueType"))
    status: IssueStatus
    problem_season: int = field(metadata=field_options(alias="problemSeason"))
    problem_episode: int = field(metadata=field_options(alias="problemEpisode"))
    created_at: datetime = field(metadata=field_options(alias="createdAt"))
    updated_at: datetime = field(metadata=field_options(alias="updatedAt"))
    created_by: User = field(metadata=field_options(alias="createdBy"))
    media: MediaInfo
    modified_by: User | None = field(
        metadata=field_options(alias="modifiedBy"), default=None
    )
    comments: list[IssueComment] = field(default_factory=list)


@dataclass
class IssueResponse(DataClassORJSONMixin):
    """Issue response model."""

    results: list[Issue]


@dataclass
class Genre:
    """Genre model."""

    id: int
    name: str


@dataclass
class Keyword:
    """Keyword model."""

    id: int
    name: str


@dataclass
class MovieDetails(DataClassORJSONMixin):
    """Movie details model."""

    id: int
    adult: bool
    budget: int
    genres: list[Genre]
    original_language: str = field(metadata=field_options(alias="originalLanguage"))
    original_title: str = field(metadata=field_options(alias="originalTitle"))
    popularity: float
    release_date: date = field(metadata=field_options(alias="releaseDate"))
    revenue: int
    title: str
    vote_average: float = field(metadata=field_options(alias="voteAverage"))
    vote_count: int = field(metadata=field_options(alias="voteCount"))
    imdb_id: str | None = field(metadata=field_options(alias="imdbId"))
    overview: str
    runtime: int
    tagline: str
    media_info: MediaInfoWithRequests = field(metadata=field_options(alias="mediaInfo"))
    keywords: list[Keyword]


@dataclass
class Season(DataClassORJSONMixin):
    """Season model."""

    id: int
    name: str
    overview: str
    season_number: int = field(metadata=field_options(alias="seasonNumber"))
    episode_count: int = field(metadata=field_options(alias="episodeCount"))
    air_date: date | None = field(metadata=field_options(alias="airDate"))
    poster_path: str = field(metadata=field_options(alias="posterPath"))


@dataclass
class Episode(DataClassORJSONMixin):
    """Episode model."""

    id: int
    name: str
    overview: str
    episode_number: int = field(metadata=field_options(alias="episodeNumber"))
    still_path: str = field(metadata=field_options(alias="stillPath"))
    air_date: date | None = field(metadata=field_options(alias="airDate"), default=None)


@dataclass
class TVDetails(DataClassORJSONMixin):
    """TV details model."""

    id: int
    first_air_date: date = field(metadata=field_options(alias="firstAirDate"))
    genres: list[Genre]
    languages: list[str]
    last_air_date: date = field(metadata=field_options(alias="lastAirDate"))
    name: str
    number_of_episodes: int = field(metadata=field_options(alias="numberOfEpisodes"))
    number_of_seasons: int = field(metadata=field_options(alias="numberOfSeasons"))
    original_language: str = field(metadata=field_options(alias="originalLanguage"))
    original_name: str = field(metadata=field_options(alias="originalName"))
    tagline: str
    overview: str
    popularity: float
    seasons: list[Season]
    last_episode_to_air: Episode = field(
        metadata=field_options(alias="lastEpisodeToAir")
    )
    keywords: list[Keyword]
    media_info: MediaInfoWithRequests | None = field(
        metadata=field_options(alias="mediaInfo"), default=None
    )
    next_episode_to_air: Episode | None = field(
        metadata=field_options(alias="nextEpisodeToAir"), default=None
    )


@dataclass
class WatchlistEntry(DataClassORJSONMixin):
    """Watchlist entry model."""

    rating_key: str = field(metadata=field_options(alias="ratingKey"))
    title: str
    media_type: MediaType = field(metadata=field_options(alias="mediaType"))
    tmdb_id: int | None = field(metadata=field_options(alias="tmdbId"))


@dataclass
class WatchlistResponse(DataClassORJSONMixin):
    """Watchlist response model."""

    results: list[WatchlistEntry]
