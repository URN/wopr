"""Configuration for Vincent, loaded from constants and environment variables."""
from pydantic import BaseSettings


class Config(BaseSettings):
    """Configuration for Vincent."""

    token: str

    guild_id: int

    prefix: str = "!"

    stream_url: str = "https://live.urn1350.net/listen"

    stats_url: str = "https://live.urn1350.net/status-json.xsl"

    class Config:  # noqa: D106
        env_file = ".env"
        env_prefix = "VINCENT_"


CONFIG = Config()  # type: ignore  # noqa: PGH003
