"""Monte Carlo poker equity engine for Texas Edge."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from cards import board_count_is_valid, ensure_unique, remaining_deck, stage_name
from hand_evaluator import describe_current_hand, evaluate_best
from preflop_rank import confidence_label, grade_preflop


@dataclass(frozen=True)
class EquityResult:
    win_rate: float
    tie_rate: float
    lose_rate: float
    wins: int
    ties: int
    losses: int
    stage: str
    hero_hand_type: str
    preflop_grade: str
    preflop_combo: str
    preflop_comment: str
    simulations: int
    confidence: str

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "win_rate": self.win_rate,
            "tie_rate": self.tie_rate,
            "lose_rate": self.lose_rate,
            "wins": self.wins,
            "ties": self.ties,
            "losses": self.losses,
            "stage": self.stage,
            "hero_hand_type": self.hero_hand_type,
            "preflop_grade": self.preflop_grade,
            "preflop_combo": self.preflop_combo,
            "preflop_comment": self.preflop_comment,
            "simulations": self.simulations,
            "confidence": self.confidence,
        }


def validate_simulation_inputs(
    hero_cards: Sequence[str],
    board_cards: Sequence[str],
    player_count: int,
    simulations: int,
) -> None:
    if len(hero_cards) != 2:
        raise ValueError("请先选择两张手牌。")
    if not board_count_is_valid(len(board_cards)):
        raise ValueError("公共牌数量必须为 0、3、4 或 5 张。")
    if not 2 <= player_count <= 10:
        raise ValueError("玩家人数必须在 2 到 10 人之间。")
    if simulations <= 0:
        raise ValueError("模拟次数必须大于 0。")

    ensure_unique([*hero_cards, *board_cards])
    deck = remaining_deck([*hero_cards, *board_cards])
    required_cards = (player_count - 1) * 2 + (5 - len(board_cards))
    if len(deck) < required_cards:
        raise ValueError("剩余牌数量不足以模拟当前玩家人数。")


def run_monte_carlo(
    hero_cards: Sequence[str],
    board_cards: Sequence[str],
    player_count: int = 6,
    simulations: int = 10_000,
    seed: int | None = None,
) -> EquityResult:
    """Estimate hero equity against unknown opponent hands."""
    hero = list(hero_cards)
    board = list(board_cards)
    validate_simulation_inputs(hero, board, player_count, simulations)

    rng = random.Random(seed)
    deck = remaining_deck([*hero, *board])
    opponent_count = player_count - 1
    missing_board_count = 5 - len(board)
    draw_count = opponent_count * 2 + missing_board_count

    wins = ties = losses = 0

    for _ in range(simulations):
        sample = rng.sample(deck, draw_count)
        cursor = 0
        opponents: list[list[str]] = []
        for _opponent in range(opponent_count):
            opponents.append(sample[cursor : cursor + 2])
            cursor += 2

        full_board = [*board, *sample[cursor : cursor + missing_board_count]]
        hero_result = evaluate_best([*hero, *full_board])
        hero_strength = hero_result.strength

        opponent_strengths = [evaluate_best([*opponent, *full_board]).strength for opponent in opponents]
        best_strength = max([hero_strength, *opponent_strengths])

        if hero_strength == best_strength:
            tied_players = 1 + sum(strength == best_strength for strength in opponent_strengths)
            if tied_players == 1:
                wins += 1
            else:
                ties += 1
        else:
            losses += 1

    preflop = grade_preflop(hero)
    total = float(simulations)
    return EquityResult(
        win_rate=round(wins / total * 100, 1),
        tie_rate=round(ties / total * 100, 1),
        lose_rate=round(losses / total * 100, 1),
        wins=wins,
        ties=ties,
        losses=losses,
        stage=stage_name(len(board)),
        hero_hand_type=describe_current_hand(hero, board),
        preflop_grade=preflop.grade,
        preflop_combo=preflop.combo,
        preflop_comment=preflop.comment,
        simulations=simulations,
        confidence=confidence_label(simulations),
    )
