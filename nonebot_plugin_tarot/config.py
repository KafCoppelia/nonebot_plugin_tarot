from pathlib import Path
from typing import Sequence, Set, Optional

import httpx
import nonebot
import nonebot_plugin_localstore as store
from aiocache import cached
from nonebot import logger
from pydantic import BaseModel, ConfigDict, Extra

try:
    import ujson as json  # type: ignore
except ModuleNotFoundError:
    import json


class TarotConfig(BaseModel):
    model_config = ConfigDict(extra=Extra.ignore, validate_assignment=True)

    tarot_path: Path = store.get_data_dir("nonebot_plugin_tarot")
    """Directory of tarot image resources. Required when deploying images locally."""

    chain_reply: bool = True
    """Enable the chain reply for avoiding screen spamming in group chat."""

    github_proxy: str = "https://ghproxy.com/https://raw.githubusercontent.com/"

    nickname: Set[str] = {"Bot"}
    """Bot's nickname."""

    tarot_builtin_theme_enabled: bool = True

    tarot_extra_themes: Sequence[str] = []
    """Extra tarot themes."""


driver = nonebot.get_driver()
if hasattr(nonebot, "get_plugin_config"):  # compatible with lower versions
    from nonebot import get_plugin_config

    tarot_config: TarotConfig = get_plugin_config(TarotConfig)
else:
    tarot_config: TarotConfig = TarotConfig.parse_obj(
        driver.config.dict(exclude_unset=True)
    )


class DownloadError(Exception):
    pass


class ResourceError(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


async def download_url(name: str, base_proxy: str) -> Optional[httpx.Response]:
    if not base_proxy.endswith("/") or not base_proxy.endswith("\\"):
        base_proxy += "/"

    url = (
        f"{base_proxy}"
        + "MinatoAquaCrews/nonebot_plugin_tarot/master/nonebot_plugin_tarot/"
        + name
    )

    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    continue

                return response

            except Exception:
                logger.warning(f"Error occurred when downloading {url}, retry: {i+1}/3")

    logger.warning("Abort downloading")


@driver.on_startup
async def tarot_config_check() -> None:
    """Check the theme configuration & text reource on startup."""
    if (
        not tarot_config.tarot_builtin_theme_enabled
        and len(tarot_config.tarot_extra_themes) == 0
    ):
        raise ResourceError(
            "No available theme! Please make sure at least one theme is enabled.\n"
            "See https://github.com/MinatoAquaCrews/nonebot_plugin_tarot/blob/master/README.md for details."
        )

    # If a custom directory is provided by user, check if it exists.
    p = tarot_config.tarot_path
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    elif not p.is_dir():
        raise RuntimeError(f"{p} is not a directory")

    # Check whether tarot.json. exists
    tarot_json_path = Path(__file__).parent / "tarot.json"

    if not tarot_json_path.exists():
        logger.warning("Missing text resource tarot.json! Trying to download...")
        response = await download_url("tarot.json", tarot_config.github_proxy)

        if not response:
            raise DownloadError

        with tarot_json_path.open("w", encoding="utf-8") as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
            logger.info(f"Downloaded completed. Saved to {tarot_json_path}.")


@cached(ttl=180)
async def download_tarot(
    theme: str, type: str, name: str, name_with_suffix: str
) -> Optional[bytes]:
    """Download the image and cache it for a while. \
        If failed, return None.
    """
    logger.info(f"Downloading image {theme}/{type}/{name} from repo...")

    resource = f"resource/{theme}/{type}/{name_with_suffix}"
    response = await download_url(resource, tarot_config.github_proxy)

    if not response:
        logger.warning(f"Download image {theme}/{type}/{name} failed!")
        return None

    return response.content
