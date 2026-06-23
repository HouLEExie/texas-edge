"""Card helpers for Texas Edge.

Cards use compact two-character codes:
- Ranks: A, K, Q, J, T, 9 ... 2
- Suits: S, H, D, C for spades, hearts, diamonds, clubs
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable


RANKS: tuple[str, ...] = ("A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2")
SUITS: tuple[str, ...] = ("S", "H", "D", "C")

RANK_VALUES: dict[str, int] = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

VALUE_TO_RANK: dict[int, str] = {value: rank for rank, value in RANK_VALUES.items()}

DISPLAY_RANKS: dict[str, str] = {"T": "10"}
SUIT_SYMBOLS: dict[str, str] = {"S": "♠", "H": "♥", "D": "♦", "C": "♣"}
SUIT_NAMES_CN: dict[str, str] = {"S": "黑桃", "H": "红桃", "D": "方块", "C": "梅花"}
SUIT_COLORS: dict[str, str] = {"S": "black", "H": "red", "D": "red", "C": "black"}


def generate_deck() -> list[str]:
    """Return a full 52-card deck in display-friendly suit/rank order."""
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]


def validate_card(card: str) -> None:
    if len(card) != 2 or card[0] not in RANK_VALUES or card[1] not in SUITS:
        raise ValueError(f"无效牌面: {card}")


def rank(card: str) -> str:
    validate_card(card)
    return card[0]


def suit(card: str) -> str:
    validate_card(card)
    return card[1]


def rank_value(card: str) -> int:
    return RANK_VALUES[rank(card)]


def rank_label(rank_code: str) -> str:
    return DISPLAY_RANKS.get(rank_code, rank_code)


def value_label(value: int) -> str:
    return rank_label(VALUE_TO_RANK[value])


def format_card(card: str | None) -> str:
    if not card:
        return "?"
    validate_card(card)
    return f"{rank_label(card[0])}{SUIT_SYMBOLS[card[1]]}"


def format_cards(cards: Iterable[str]) -> str:
    visible = [format_card(card) for card in cards if card]
    return " ".join(visible) if visible else "无"


def card_color(card: str) -> str:
    return SUIT_COLORS[suit(card)]


def sort_cards(cards: Iterable[str]) -> list[str]:
    return sorted(cards, key=lambda c: (SUITS.index(suit(c)), -rank_value(c)))


def find_duplicates(cards: Iterable[str | None]) -> list[str]:
    values = [card for card in cards if card]
    counts = Counter(values)
    return [card for card, count in counts.items() if count > 1]


def ensure_unique(cards: Iterable[str | None]) -> None:
    duplicates = find_duplicates(cards)
    if duplicates:
        labels = ", ".join(format_card(card) for card in duplicates)
        raise ValueError(f"不能重复选择同一张牌: {labels}")


def remaining_deck(excluded_cards: Iterable[str | None]) -> list[str]:
    excluded = {card for card in excluded_cards if card}
    ensure_unique(excluded)
    return [card for card in generate_deck() if card not in excluded]


def board_count_is_valid(board_count: int) -> bool:
    return board_count in {0, 3, 4, 5}


def stage_name(board_count: int) -> str:
    names = {
        0: "Preflop / 翻牌前",
        3: "Flop / 翻牌圈",
        4: "Turn / 转牌圈",
        5: "River / 河牌圈",
    }
    return names.get(board_count, "Invalid / 公共牌数量无效")
