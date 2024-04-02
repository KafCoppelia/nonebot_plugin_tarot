import asyncio
import random
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple, Union
from PIL import Image

try:
    import ujson as json  # type: ignore
except ModuleNotFoundError:
    import json

from .config import download_tarot, ResourceError, tarot_config
from nonebot_plugin_saa import (
    AggregatedMessageFactory,
    MessageFactory,
    PlatformTarget,
    TargetQQGroup,
    Text,
    Image as MessageImage,
)

CardInfoType = Dict[str, Union[str, Dict[str, str]]]
FormationInfoType = Dict[str, Dict[str, Union[int, bool, List[List[str]]]]]

TAROT_BUILTIN_THEMES = ["BilibiliTarot"]
"""Built-in tarot themes. DO NOT EDIT!"""

TAROT_THEMES_IN_REPO = ["BilibiliTarot", "TouhouTarot"]
"""Themes in the repository. DO NOT EDIT!"""

TAROT_SUBCATEGORIES = ["MajorArcana", "Cups", "Pentacles", "Sowrds", "Wands"]


def subcategories(theme: str) -> List[str]:
    """Return the subcategories of the theme."""
    if theme in TAROT_BUILTIN_THEMES:
        return TAROT_SUBCATEGORIES

    # For extra themes, iterate the subdirectory
    sub_categories = [
        f.name
        for f in (tarot_config.tarot_path / theme).iterdir()
        if f.is_dir() and f.name in TAROT_SUBCATEGORIES
    ]

    return sub_categories


@dataclass
class DivinationInfo:
    theme: str
    cards_info: List[CardInfoType]
    is_cut: bool
    rep: List[List[str]]  # representations

    @property
    def n_cards(self) -> int:
        return len(self.cards_info)


class Tarot:
    def __init__(self) -> None:
        self.tarot_json = Path(__file__).parent / "tarot.json"
        self._is_chain_reply = tarot_config.chain_reply

        if tarot_config.tarot_builtin_theme_enabled:
            avail_themes = TAROT_BUILTIN_THEMES + list(tarot_config.tarot_extra_themes)
        else:
            avail_themes = list(tarot_config.tarot_extra_themes)

        self.avail_themes = avail_themes

    async def divine_in_group(self, target: PlatformTarget) -> None:
        info, formation_name = self._get_divination_info()

        await MessageFactory(f"启用{formation_name}，正在洗牌中").send()

        # Generate messages
        chain = []
        n = info.n_cards

        for i in range(n):
            # Select the #i tarot
            if info.is_cut and i == n - 1:
                msg_header = Text(f"切牌「{info.rep[i]}」\n")
            else:
                msg_header = Text(f"第{i+1}张牌「{info.rep[i]}」\n")

            flag, msg_body = await self._get_text_and_image(
                info.theme, info.cards_info[i]
            )
            if not flag:
                await MessageFactory(msg_body).finish()

            if self.is_chain_reply and isinstance(target, TargetQQGroup):
                chain.append(msg_header + msg_body)
            else:
                if i < n - 1:
                    await MessageFactory(msg_header + msg_body).send()
                    await asyncio.sleep(0.5)  # In case of sending frequently
                else:
                    await MessageFactory(msg_header + msg_body).finish()

        if self.is_chain_reply and isinstance(target, TargetQQGroup):
            amf = AggregatedMessageFactory(chain)
            await amf.finish()

    async def divine_in_private(self) -> None:
        info, formation_name = self._get_divination_info()

        await MessageFactory(f"启用{formation_name}，正在洗牌中").send()

        # Generate messages
        n = info.n_cards
        for i in range(n):
            # Select the #i tarot
            if info.is_cut and i == n - 1:
                msg_header = Text(f"切牌「{info.rep[i]}」\n")
            else:
                msg_header = Text(f"第{i+1}张牌「{info.rep[i]}」\n")

            flag, msg_body = await self._get_text_and_image(
                info.theme, info.cards_info[i]
            )
            if not flag:
                await MessageFactory(msg_body).finish()

            if i < n:
                await MessageFactory(msg_header + msg_body).send()
            else:
                await MessageFactory(msg_header + msg_body).finish()

    async def get_one_tarot(self) -> MessageFactory:
        """Get one tarot."""
        # 1. Pick a theme randomly.
        theme = self._select_theme()

        # 2. Draw 1 card.
        card_info = self._draw_n_cards(theme, 1)

        # 3. Get the text & image.
        flag, body = await self._get_text_and_image(theme, card_info[0])

        return "回应是" + body if flag else body

    def _get_divination_info(self) -> Tuple[DivinationInfo, str]:
        """Get divination information.

        Steps:
            - 1. Choose a theme.
            - 2. Open tarot.json & draw a formation randomly.
            - 3. Get the devined cards list and the text of representations.

        Returns:
            - the divination information `DivinationInfo`.
            - the name of formation.
        """
        # 1. Select a theme and formation from tarot.json randomly.
        theme = self._select_theme()
        formation_name, formation = self._draw_a_formation()

        # 2. Get #N of cards, where N is `cards_num`.`
        cards_num: int = formation.get("cards_num")  # type: ignore
        cards_info = self._draw_n_cards(theme, cards_num)

        # 3. Get the text of representations.
        is_cut: bool = formation.get("is_cut")  # type: ignore
        representations: List[List[str]] = random.choice(
            formation.get("representations")  # type: ignore
        )

        return (
            DivinationInfo(theme, cards_info, is_cut, representations),
            formation_name,
        )

    def _select_theme(self) -> str:
        return random.choice(self.avail_themes)

    def _draw_a_formation(self) -> Tuple[str, FormationInfoType]:
        with open(self.tarot_json, "r", encoding="utf-8") as f:
            content = json.load(f)
            all_formations: Dict[str, FormationInfoType] = content.get("formations")

        formation_name = random.choice(list(all_formations))
        formation = all_formations.get(formation_name)

        if not formation:
            raise KeyError(f"The content of formation {formation_name} is empty!")

        return formation_name, formation

    def _draw_n_cards(self, theme: str, n: int) -> List[CardInfoType]:
        """Randomly draw `n` cards based on the provided theme."""
        # 1. Get the subcategories of the theme.
        sub_categories = subcategories(theme)

        if len(sub_categories) < 1:
            raise ResourceError(f"本地塔罗牌主题 {theme} 为空！请检查资源！")

        # 2. Get the cards that match the subcategory.
        with open(self.tarot_json, "r", encoding="utf-8") as f:
            content = json.load(f)
            all_cards: Dict[str, CardInfoType] = content.get("cards")

        subset_cards = {
            k: v for k, v in all_cards.items() if v.get("type") in sub_categories
        }

        # 3. Shuffle and draw `n` cards.
        cards_index = random.sample(list(subset_cards), n)
        cards_info = [v for k, v in subset_cards.items() if k in cards_index]

        return cards_info

    async def _get_text_and_image(
        self, theme: str, card_info: CardInfoType
    ) -> Tuple[bool, MessageFactory]:
        """Get the tarot image & text based on theme & `card_info`."""
        _type: str = card_info.get("type")  # type: ignore
        _name: str = card_info.get("pic")  # type: ignore
        img_dir = tarot_config.tarot_path / theme / _type
        img_with_suffix = ""

        # Consider the suffix of picture, such as `.png` or `.jpg`.
        for p in img_dir.glob(_name + ".*"):
            img_with_suffix = p.name
            break

        if img_with_suffix == "":
            # Not found in the local directory, so try to download from repo.
            if theme in TAROT_THEMES_IN_REPO:
                data = await download_tarot(theme, _type, _name, img_with_suffix)
                if data is None:
                    return False, MessageFactory(
                        Text("图片下载出错，请重试或将资源部署本地……")
                    )

                img = Image.open(data)
            else:
                # It's a user-defined theme, then raise exception.
                raise FileNotFoundError(
                    f"图片 {theme}/{_type}/{_name} 不存在！请确保自定义塔罗牌图片资源完整。"
                )
        else:
            img = Image.open(img_dir / img_with_suffix)

        # Select whether the card is upright or reversed.
        name_cn: str = card_info.get("name_cn")  # type: ignore
        if random.random() < 0.5:
            meaning: str = card_info.get("meaning").get("up")  # type: ignore
            msg = Text(f"「{name_cn}正位」「{meaning}」\n")
        else:
            meaning: str = card_info.get("meaning").get("down")  # type: ignore
            msg = Text(f"「{name_cn}逆位」「{meaning}」\n")
            img = img.rotate(180)

        buf = BytesIO()
        img.save(buf, format="png")

        return True, MessageFactory([msg, MessageImage(buf)])

    @property
    def is_chain_reply(self) -> bool:
        return self._is_chain_reply

    @is_chain_reply.setter
    def is_chain_reply(self, new_state: bool) -> None:
        """开启/关闭全局群聊转发模式"""
        self._is_chain_reply = new_state


tarot_manager = Tarot()
