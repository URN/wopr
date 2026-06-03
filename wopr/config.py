"""Configuration for WOPR, loaded from constants and environment variables."""
from pydantic import BaseSettings


class Config(BaseSettings):
    """Configuration for WOPR."""

    xnode_ips : dict[str, str]

    token: str

    guild_id: int

    prefix: str = "!"

    stream_url: str = "https://live.urn1350.co.uk/listen"

    stats_url: str = "https://live.urn1350.co.uk/status-json.xsl"

    iqx_username: str
    iqx_password: str
    iqx_url: str

    class Config:  # noqa: D106
        env_file = ".env"
        env_prefix = "WOPR_"


CONFIG = Config()  # type: ignore  # noqa: PGH003
