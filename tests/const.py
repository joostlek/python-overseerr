"""Constants for tests."""

from importlib import metadata

MOCK_HOST = "192.168.0.30"

MOCK_URL = f"https://{MOCK_HOST}/api/v1"
version = metadata.version("python_overseerr")

HEADERS = {
    "User-Agent": f"PythonOverseerr/{version}",
    "Accept": "application/json",
}
