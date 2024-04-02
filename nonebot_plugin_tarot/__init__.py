from typing import NoReturn
from nonebot import on_command, on_regex, require
from nonebot.adapters import Event
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.params import Depends
from nonebot.rule import Rule

require("nonebot_plugin_localstore")  # isort:skip
require("nonebot_plugin_saa")  # isort:skip

from nonebot_plugin_saa import MessageFactory, PlatformTarget, get_target

from .config import TarotConfig
from .data_source import tarot_manager

__plugin_version__ = "v0.5.0a6"
__plugin_usages__ = f"""
塔罗牌 {__plugin_version__}
[占卜] 随机选取牌阵进行占卜
[塔罗牌] 得到单张塔罗牌回应
[开启/启用/关闭/禁用]群聊转发 开启或关闭全局群聊转发""".strip()

__plugin_meta__ = PluginMetadata(
    name="塔罗牌",
    description="塔罗牌！魔法占卜🔮",
    usage=__plugin_usages__,
    type="application",
    homepage="https://github.com/MinatoAquaCrews/nonebot_plugin_tarot",
    config=TarotConfig,
    extra={
        "author": "KafCoppelia <k740677208@gmail.com>",
        "version": __plugin_version__,
    },
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
)


def _is_group_event(event: Event) -> bool:
    return "_" in event.get_session_id()


divine = on_command(cmd="占卜", priority=7)
tarot = on_command(cmd="塔罗牌", priority=7)
chain_reply_switch = on_regex(
    pattern=r"^(开启|启用|关闭|禁用)群聊转发(模式)?$",
    rule=Rule(_is_group_event),
    permission=SUPERUSER,
    priority=7,
    block=True,
)


@divine.handle()
async def general_divine(
    event: Event, target: PlatformTarget = Depends(get_target)
) -> None:
    arg = event.get_plaintext()

    if "帮助" in arg[-2:]:
        await MessageFactory(__plugin_usages__).finish()

    if _is_group_event(event):
        await tarot_manager.divine_in_group(target)
    else:
        await tarot_manager.divine_in_private()


@tarot.handle()
async def _(event: Event) -> NoReturn:
    arg = event.get_plaintext()

    if "帮助" in arg[-2:]:
        await MessageFactory(__plugin_usages__).finish()

    msg = await tarot_manager.get_one_tarot()

    await MessageFactory(msg).finish(at_sender=True)


@chain_reply_switch.handle()
async def _(event: Event) -> NoReturn:
    arg = event.get_plaintext()
    base = "占卜群聊转发模式已{0}~"

    if arg[:2] == "开启" or arg[:2] == "启用":
        tarot_manager.is_chain_reply = True
        msg = base.format("开启")
    else:
        tarot_manager.is_chain_reply = False
        msg = base.format("关闭")

    await MessageFactory(msg).finish()
