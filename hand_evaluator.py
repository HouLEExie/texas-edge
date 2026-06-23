"""Texas Hold'em hand evaluation.

The evaluator accepts 5 to 7 cards and returns a comparable result. It uses
direct rank/suit analysis rather than enumerating every five-card combination,
which keeps Monte Carlo simulation responsive on mobile-oriented workloads.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

from cards import RANK_VALUES, rank, rank_value, suit, value_label


HAND_CATEGORY_NAMES: dict[int, str] = {
    9: "皇家同花顺",
    8: "同花顺",
    7: "四条",
    6: "葫芦",
    5: "同花",
    4: "顺子",
    3: "三条",
    2: "两对",
    1: "一对",
    0: "高牌",
}

HAND_CATEGORY_EN: dict[int, str] = {
    9: "Royal Flush",
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card",
}


@dataclass(frozen=True)
class HandResult:
    category: int
    kickers: tuple[int, ...]
    name: str
    english_name: str

    @property
    def strength(self) -> tuple[int, ...]:
        return (self.category, *self.kickers)

    @property
    def full_name(self) -> str:
        return f"{self.name} / {self.english_name}"


def _straight_high(values: Iterable[int]) -> int | None:
    unique = set(values)
    if 14 in unique:
        unique.add(1)
    for high in range(14, 4, -1):
        if all(value in unique for value in range(high - 4, high + 1)):
            return high
    return None


def _top_values(values: Iterable[int], amount: int, exclude: set[int] | None = None) -> tuple[int, ...]:
    excluded = exclude or set()
    unique_desc = sorted({value for value in values if value not in excluded}, reverse=True)
    return tuple(unique_desc[:amount])


def _name(category: int, kickers: Sequence[int]) -> str:
    if category == 9:
        return "皇家同花顺"
    if category == 8:
        return f"{value_label(kickers[0])}高同花顺"
    if category == 7:
        return f"四条 {value_label(kickers[0])}"
    if category == 6:
        return f"{value_label(kickers[0])}带{value_label(kickers[1])}葫芦"
    if category == 5:
        return f"{value_label(kickers[0])}高同花"
    if category == 4:
        return f"{value_label(kickers[0])}高顺子"
    if category == 3:
        return f"三条 {value_label(kickers[0])}"
    if category == 2:
        return f"两对 {value_label(kickers[0])} 和 {value_label(kickers[1])}"
    if category == 1:
        return f"一对 {value_label(kickers[0])}"
    return f"高牌 {value_label(kickers[0])}"


def evaluate_best(cards: Sequence[str]) -> HandResult:
    """Evaluate the best poker hand from 5 to 7 cards."""
    if not 5 <= len(cards) <= 7:
        raise ValueError("牌型判断需要 5 到 7 张牌。")

    values = [rank_value(card) for card in cards]
    counts = Counter(values)
    by_suit: dict[str, list[int]] = defaultdict(list)
    for card in cards:
        by_suit[suit(card)].append(rank_value(card))

    straight_flush_highs: list[int] = []
    flush_values: list[int] | None = None
    for suited_values in by_suit.values():
        if len(suited_values) >= 5:
            suited_sorted = sorted(suited_values, reverse=True)
            flush_values = max(flush_values or [], suited_sorted, key=lambda item: tuple(item[:5]))
            high = _straight_high(suited_values)
            if high:
                straight_flush_highs.append(high)

    if straight_flush_highs:
        high = max(straight_flush_highs)
        category = 9 if high == 14 else 8
        kickers = (high,)
        return HandResult(category, kickers, _name(category, kickers), HAND_CATEGORY_EN[category])

    four_ranks = sorted([value for value, count in counts.items() if count == 4], reverse=True)
    if four_ranks:
        four = four_ranks[0]
        kickers = (four, *_top_values(values, 1, {four}))
        return HandResult(7, kickers, _name(7, kickers), HAND_CATEGORY_EN[7])

    trip_ranks = sorted([value for value, count in counts.items() if count >= 3], reverse=True)
    pair_ranks = sorted([value for value, count in counts.items() if count >= 2], reverse=True)
    if trip_ranks:
        trip = trip_ranks[0]
        full_house_pairs = [value for value in pair_ranks if value != trip] + trip_ranks[1:]
        if full_house_pairs:
            pair = max(full_house_pairs)
            kickers = (trip, pair)
            return HandResult(6, kickers, _name(6, kickers), HAND_CATEGORY_EN[6])

    if flush_values:
        kickers = tuple(flush_values[:5])
        return HandResult(5, kickers, _name(5, kickers), HAND_CATEGORY_EN[5])

    straight_high = _straight_high(values)
    if straight_high:
        kickers = (straight_high,)
        return HandResult(4, kickers, _name(4, kickers), HAND_CATEGORY_EN[4])

    if trip_ranks:
        trip = trip_ranks[0]
        kickers = (trip, *_top_values(values, 2, {trip}))
        return HandResult(3, kickers, _name(3, kickers), HAND_CATEGORY_EN[3])

    if len(pair_ranks) >= 2:
        high_pair, low_pair = pair_ranks[:2]
        kickers = (high_pair, low_pair, *_top_values(values, 1, {high_pair, low_pair}))
        return HandResult(2, kickers, _name(2, kickers), HAND_CATEGORY_EN[2])

    if len(pair_ranks) == 1:
        pair = pair_ranks[0]
        kickers = (pair, *_top_values(values, 3, {pair}))
        return HandResult(1, kickers, _name(1, kickers), HAND_CATEGORY_EN[1])

    kickers = _top_values(values, 5)
    return HandResult(0, kickers, _name(0, kickers), HAND_CATEGORY_EN[0])


def compare_many(hands: Sequence[Sequence[str]], board: Sequence[str]) -> tuple[list[int], list[HandResult]]:
    """Return winner indices and evaluated hand results for all players."""
    results = [evaluate_best([*hand, *board]) for hand in hands]
    best_strength = max(result.strength for result in results)
    winners = [index for index, result in enumerate(results) if result.strength == best_strength]
    return winners, results


def has_flush_draw(cards: Sequence[str]) -> bool:
    if len(cards) >= 7:
        return False
    suit_counts = Counter(suit(card) for card in cards)
    return any(count == 4 for count in suit_counts.values())


def has_straight_draw(cards: Sequence[str]) -> bool:
    if len(cards) >= 7:
        return False
    values = {rank_value(card) for card in cards}
    if RANK_VALUES["A"] in values:
        values.add(1)

    for low in range(1, 11):
        window = set(range(low, low + 5))
        if len(window & values) == 4:
            return True
    return False


def describe_current_hand(hero_cards: Sequence[str], board_cards: Sequence[str]) -> str:
    """Describe the hero's current made hand, with simple draw hints."""
    cards = [*hero_cards, *board_cards]
    if len(hero_cards) < 2:
        return "请选择两张手牌"
    if len(board_cards) == 0:
        return "翻牌前未成牌"
    if len(cards) < 5:
        return "公共牌数量不足"

    result = evaluate_best(cards)
    if len(board_cards) < 5 and result.category <= 1:
        if has_flush_draw(cards):
            return "同花听牌"
        if has_straight_draw(cards):
            return "顺子听牌"
    return result.name
