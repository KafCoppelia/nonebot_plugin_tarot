import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter


@pytest.fixture(scope="session", autouse=True)
def load_bot() -> None:
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)
    nonebot.load_plugin("nonebot_plugin_tarot")
