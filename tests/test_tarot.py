import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pytest
from nonebug import App

try:
    import ujson as json  # type: ignore
except ModuleNotFoundError:
    import json


@pytest.mark.asyncio
async def test_tarot_config_import(app: App):
    from nonebot_plugin_tarot.config import tarot_config

    print(tarot_config.tarot_path)


CardInfoType = Dict[str, Union[str, Dict[str, str]]]
FormationInfoType = Dict[str, Dict[str, Union[int, bool, List[List[str]]]]]

tarot_builtin_themes = ["BilibiliTarot"]
"""Built-in tarot themes."""

tarot_themes_in_repo = ["BilibiliTarot", "TouhouTarot"]
"""Themes in the repository."""

tarot_path = Path(__file__).parent.parent / "nonebot_plugin_tarot" / "resource"
tarot_json = Path(__file__).parent.parent / "nonebot_plugin_tarot" / "tarot.json"


def subcategories(theme: str) -> List[str]:
    """Return the subcategories of the theme."""
    all_subcategories = ["MajorArcana", "Cups", "Pentacles", "Sowrds", "Wands"]

    if theme in tarot_builtin_themes:
        return all_subcategories

    # For extra themes, iterate the subdirectory
    sub_categories = [
        f.name
        for f in (tarot_path / theme).iterdir()
        if f.is_dir() and f.name in all_subcategories
    ]

    return sub_categories


@dataclass
class DivinationInfo:
    theme: str
    cards_info: List[CardInfoType]
    is_cut: bool
    rep: List[List[str]]
    """Representations"""

    @property
    def n_cards(self) -> int:
        return len(self.cards_info)


def _select_theme() -> str:
    return random.choice(tarot_themes_in_repo)


def _draw_n_cards(theme: str, n: int):
    """Randomly draw `n` cards based on the provided theme."""
    # 1. Get the subcategories of the theme.
    sub_categories = subcategories(theme)

    if len(sub_categories) < 1:
        raise FileNotFoundError

    # 2. Get the cards that match the subcategory.
    with open(tarot_json, "r", encoding="utf-8") as f:
        content = json.load(f)
        all_cards: Dict[str, CardInfoType] = content.get("cards")

    subset_cards = {
        k: v for k, v in all_cards.items() if v.get("type") in sub_categories
    }

    # 3. Shuffle and draw `n` cards.
    cards_index = random.sample(list(subset_cards), n)
    cards_info = [v for k, v in subset_cards.items() if k in cards_index]

    return cards_info


def _draw_a_formation() -> Tuple[str, FormationInfoType]:
    with open(tarot_json, "r", encoding="utf-8") as f:
        content = json.load(f)
        all_formations: Dict[str, FormationInfoType] = content.get("formations")

    formation_name = random.choice(list(all_formations))
    formation = all_formations.get(formation_name)

    if not formation:
        raise KeyError(f"The content of formation {formation_name} is empty!")

    return formation_name, formation


def _get_divination_info() -> Tuple[DivinationInfo, str]:
    # 1. Select a theme and formation from tarot.json randomly.
    theme = _select_theme()
    formation_name, formation = _draw_a_formation()

    # 2. Get #N of cards, where N is `cards_num`.`
    cards_num: int = formation.get("cards_num")  # type: ignore
    cards_info = _draw_n_cards(theme, cards_num)

    # 3. Get the text of representations.
    is_cut: bool = formation.get("is_cut")  # type: ignore
    representations: List[List[str]] = random.choice(
        formation.get("representations")  # type: ignore
    )

    return DivinationInfo(theme, cards_info, is_cut, representations), formation_name


def test_get_one_tarot():
    """One-time divination."""
    # 1. Pick a theme randomly.
    theme = _select_theme()

    # 2. Draw 1 card.
    card_info = _draw_n_cards(theme, 1)
    assert len(card_info) == 1

    card_info = card_info[0]

    """Get the tarot image & text based on `card_info`."""
    _type: str = card_info.get("type")  # type: ignore
    _name: str = card_info.get("pic")  # type: ignore

    path_1 = tarot_path
    img_dir = path_1 / theme / _type
    img_name = ""

    # Consider the suffix of pictures, `.png` or `.jpg`, etc.
    for p in img_dir.glob(_name + ".*"):
        img_name = p.name
        break

    assert img_name != ""

    path_2 = Path.cwd()
    img_dir = path_2 / theme / _type
    img_name = ""

    # Consider the suffix of pictures, `.png` or `.jpg`, etc.
    for p in img_dir.glob(_name + ".*"):
        img_name = p.name
        break

    assert img_name == ""


def test_general_divine():
    info, formation_name = _get_divination_info()
