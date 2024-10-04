from .account import CloudflareAccount

from pathlib import Path

from appdirs import user_config_dir
import requests_cache

requests_cache.install_cache(
    Path(user_config_dir()) / "cloudflare-tools.db",
    expire_after=3600,
)

__all__ = [
    "CloudflareAccount",
]
