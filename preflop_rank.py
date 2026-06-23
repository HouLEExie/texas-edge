"""Preflop hand grading for Texas Edge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from cards import VALUE_TO_RANK, rank_value, suit


@dataclass(frozen=True)
class PreflopGrade:
    grade: str
    combo: str
    comment: str


GRADE_COMMENTS: dict[str, str] = {
    "S": "顶级起手牌，适合多数位置积极参与。",
    "A": "强起手牌，但多人底池中胜率会下降。",
    "B": "有竞争力的起手牌，适合结合位置和行动强度选择参与。",
    "C": "边缘牌，位置和对手人数非常重要。",
    "D": "弱牌，通常不适合主动投入太多。",
}

S_GRADE = {"AA", "KK", "QQ", "AKs"}
A_GRADE = {"JJ", "TT", "AQs", "AKo", "AQo", "AJs", "KQs"}
B_GRADE = {"99", "88", "77", "ATs", "KJs", "QJs", "JTs", "KQo"}
C_SUITED_CONNECTORS = {"KTs", "QTs", "T9s", "98s", "87s", "76s", "65s", "54s"}


def _rank_code_from_value(value: int) -> str:
    return VALUE_TO_RANK[value]


def normalize_combo(cards: Sequence[str]) -> str:
    if len(cards) != 2:
        raise ValueError("起手牌评级需要正好两张手牌。")

    first, second = sorted(cards, key=rank_value, reverse=True)
    first_rank = _rank_code_from_value(rank_value(first))
    second_rank = _rank_code_from_value(rank_value(second))
    if first_rank == second_rank:
        return f"{first_rank}{second_rank}"

    suited = "s" if suit(first) == suit(second) else "o"
    return f"{first_rank}{second_rank}{suited}"


def grade_preflop(cards: Sequence[str]) -> PreflopGrade:
    combo = normalize_combo(cards)
    if combo in S_GRADE:
        grade = "S"
    elif combo in A_GRADE:
        grade = "A"
    elif combo in B_GRADE:
        grade = "B"
    elif _is_c_grade(combo, cards):
        grade = "C"
    else:
        grade = "D"
    return PreflopGrade(grade=grade, combo=combo, comment=GRADE_COMMENTS[grade])


def _is_c_grade(combo: str, cards: Sequence[str]) -> bool:
    values = sorted([rank_value(card) for card in cards], reverse=True)
    is_pair = values[0] == values[1]
    is_suited = suit(cards[0]) == suit(cards[1])
    gap = abs(values[0] - values[1])

    if is_pair:
        return True
    if is_suited and gap <= 1 and values[0] >= 8:
        return True
    if is_suited and values[0] == 14 and values[1] <= 9:
        return True
    if combo in C_SUITED_CONNECTORS:
        return True
    return False


def confidence_label(simulations: int) -> str:
    if simulations >= 50_000:
        return "稳定度高"
    if simulations >= 10_000:
        return "稳定度较高"
    return "稳定度一般"
