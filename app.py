from __future__ import annotations

from typing import Any

import streamlit as st

from cards import (
    RANKS,
    SUITS,
    SUIT_NAMES_CN,
    card_color,
    format_card,
    format_cards,
    stage_name,
)
from poker_engine import EquityResult, run_monte_carlo, validate_simulation_inputs
from preflop_rank import grade_preflop
from styles import apply_styles


SIMULATION_OPTIONS = {
    "快速 1,000": 1_000,
    "标准 10,000": 10_000,
    "精准 50,000": 50_000,
}


def init_state() -> None:
    defaults: dict[str, Any] = {
        "hero_cards": [None, None],
        "board_cards": [None, None, None, None, None],
        "active_area": "hero",
        "active_index": 0,
        "player_count": 6,
        "player_slider": 6,
        "simulations": 10_000,
        "last_result": None,
        "last_record": None,
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def compact_cards(cards: list[str | None]) -> list[str]:
    return [card for card in cards if card]


def selected_cards() -> list[str]:
    return [*compact_cards(st.session_state.hero_cards), *compact_cards(st.session_state.board_cards)]


def current_active_card() -> str | None:
    area = st.session_state.active_area
    index = st.session_state.active_index
    return st.session_state.hero_cards[index] if area == "hero" else st.session_state.board_cards[index]


def set_active_slot(area: str, index: int) -> None:
    st.session_state.active_area = area
    st.session_state.active_index = index


def next_open_slot() -> None:
    for index, card in enumerate(st.session_state.hero_cards):
        if card is None:
            set_active_slot("hero", index)
            return
    for index, card in enumerate(st.session_state.board_cards):
        if card is None:
            set_active_slot("board", index)
            return


def place_card(card: str) -> None:
    area = st.session_state.active_area
    index = st.session_state.active_index
    target = st.session_state.hero_cards if area == "hero" else st.session_state.board_cards

    if target[index] == card:
        target[index] = None
        return

    if card in selected_cards():
        return

    target[index] = card
    next_open_slot()


def clear_current_slot() -> None:
    area = st.session_state.active_area
    index = st.session_state.active_index
    if area == "hero":
        st.session_state.hero_cards[index] = None
    else:
        st.session_state.board_cards[index] = None


def reset_selection() -> None:
    st.session_state.hero_cards = [None, None]
    st.session_state.board_cards = [None, None, None, None, None]
    st.session_state.active_area = "hero"
    st.session_state.active_index = 0
    st.session_state.last_result = None
    st.session_state.last_record = None


def player_label(player_count: int) -> str:
    labels = {
        2: "Heads-up",
        6: "6-Max",
        9: "Full Ring",
        10: "10-Max",
    }
    return labels.get(player_count, "自定义人数")


def set_player_count(value: int) -> None:
    value = max(2, min(10, value))
    st.session_state.player_count = value
    st.session_state.player_slider = value


def sync_player_from_slider() -> None:
    st.session_state.player_count = st.session_state.player_slider


def board_cards_for_calc() -> list[str]:
    return compact_cards(st.session_state.board_cards)


def hero_cards_for_calc() -> list[str]:
    return compact_cards(st.session_state.hero_cards)


def slot_html(card: str | None, label: str, active: bool) -> str:
    active_class = " active" if active else ""
    color_class = " red" if card and card_color(card) == "red" else ""
    return f"""
    <div class="edge-card-slot{active_class}">
      <div class="edge-card-face{color_class}">{format_card(card)}</div>
      <div class="edge-card-label">{label}</div>
    </div>
    """


def render_hero_slots() -> None:
    st.markdown('<div class="edge-section-title">我的手牌</div>', unsafe_allow_html=True)
    cols = st.columns(2, gap="small")
    for index, col in enumerate(cols):
        with col:
            active = st.session_state.active_area == "hero" and st.session_state.active_index == index
            st.markdown(slot_html(st.session_state.hero_cards[index], f"Hero {index + 1}", active), unsafe_allow_html=True)
            label = "当前选择" if active else "选择此槽"
            if st.button(label, key=f"hero_slot_{index}", use_container_width=True):
                set_active_slot("hero", index)


def render_board_slots() -> None:
    board_count = len(board_cards_for_calc())
    st.markdown('<div class="edge-section-title">公共牌</div>', unsafe_allow_html=True)
    st.markdown(f'<span class="edge-pill">{stage_name(board_count)}</span>', unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    labels = ["Flop 1", "Flop 2", "Flop 3", "Turn", "River"]
    for index, col in enumerate(cols):
        with col:
            active = st.session_state.active_area == "board" and st.session_state.active_index == index
            st.markdown(slot_html(st.session_state.board_cards[index], labels[index], active), unsafe_allow_html=True)
            label = "当前" if active else "选择"
            if st.button(label, key=f"board_slot_{index}", use_container_width=True):
                set_active_slot("board", index)

    if board_count in {1, 2}:
        st.warning("公共牌数量必须为 0、3、4 或 5 张。")


def render_player_controls() -> None:
    st.markdown('<div class="edge-section-title">玩家人数</div>', unsafe_allow_html=True)
    left, center, right = st.columns([1, 2.2, 1], gap="small")
    with left:
        if st.button("-", key="player_minus", use_container_width=True, disabled=st.session_state.player_count <= 2):
            set_player_count(st.session_state.player_count - 1)
    with center:
        st.markdown(
            f"""
            <div class="edge-panel" style="text-align:center; padding:0.72rem;">
              <div style="font-size:1.8rem;font-weight:850;color:#F3F1E8;">{st.session_state.player_count} 人</div>
              <div style="color:#9FAAA3;font-size:0.82rem;">{player_label(st.session_state.player_count)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if st.button("+", key="player_plus", use_container_width=True, disabled=st.session_state.player_count >= 10):
            set_player_count(st.session_state.player_count + 1)

    quick_cols = st.columns(4, gap="small")
    for value, col in zip([2, 6, 9, 10], quick_cols):
        with col:
            label = f"✓ {value}人" if st.session_state.player_count == value else f"{value}人"
            if st.button(label, key=f"players_{value}", use_container_width=True):
                set_player_count(value)

    st.slider(
        "玩家人数滑块",
        2,
        10,
        key="player_slider",
        label_visibility="collapsed",
        on_change=sync_player_from_slider,
    )

    if st.session_state.player_count >= 9:
        st.info("多人局计算量更大，如手机端较慢，可使用快速或标准模式。")


def render_simulation_controls() -> None:
    st.markdown('<div class="edge-section-title">模拟精度</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for (label, value), col in zip(SIMULATION_OPTIONS.items(), cols):
        with col:
            button_label = f"✓ {label}" if st.session_state.simulations == value else label
            if st.button(button_label, key=f"sim_{value}", use_container_width=True):
                st.session_state.simulations = value


def render_card_picker() -> None:
    st.markdown('<div class="edge-section-title">牌面选择</div>', unsafe_allow_html=True)
    active_name = "手牌" if st.session_state.active_area == "hero" else "公共牌"
    st.caption(f"当前槽位：{active_name} {st.session_state.active_index + 1}。点击已选中的同一张牌可清空该槽位。")

    current_card = current_active_card()
    occupied = set(selected_cards())
    for suit_code in SUITS:
        st.markdown(f"**{SUIT_NAMES_CN[suit_code]}**")
        for chunk_index, rank_chunk in enumerate((RANKS[:7], RANKS[7:])):
            cols = st.columns(len(rank_chunk), gap="small")
            for rank_code, col in zip(rank_chunk, cols):
                card = f"{rank_code}{suit_code}"
                is_current = current_card == card
                is_occupied = card in occupied
                disabled = is_occupied and not is_current
                label = format_card(card)
                if is_current:
                    label = f"✓ {label}"
                elif is_occupied:
                    label = f"· {label}"
                with col:
                    if st.button(
                        label,
                        key=f"card_{card}_{chunk_index}",
                        disabled=disabled,
                        use_container_width=True,
                    ):
                        place_card(card)

    control_cols = st.columns(2, gap="small")
    with control_cols[0]:
        st.button("清空当前槽位", key="clear_slot", use_container_width=True, on_click=clear_current_slot)
    with control_cols[1]:
        st.button("重新选择", key="reset_top", use_container_width=True, on_click=reset_selection)


def build_record(result: EquityResult) -> dict[str, Any]:
    return {
        "hero": format_cards(hero_cards_for_calc()),
        "board": format_cards(board_cards_for_calc()),
        "players": st.session_state.player_count,
        "simulations": st.session_state.simulations,
        "win_rate": result.win_rate,
        "tie_rate": result.tie_rate,
        "lose_rate": result.lose_rate,
        "stage": result.stage,
        "hero_hand_type": result.hero_hand_type,
        "preflop_grade": result.preflop_grade,
        "preflop_comment": result.preflop_comment,
    }


def save_record(record: dict[str, Any]) -> None:
    history = st.session_state.history
    if history and history[0] == record:
        return
    st.session_state.history = [record, *history][:10]


def render_result(result: EquityResult) -> None:
    st.markdown('<div class="edge-section-title">结果仪表盘</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="edge-result-grid">
          <div class="edge-metric win">
            <div class="edge-metric-label">胜率 WIN</div>
            <div class="edge-metric-value">{result.win_rate:.1f}%</div>
          </div>
          <div class="edge-metric">
            <div class="edge-metric-label">平局 TIE</div>
            <div class="edge-metric-value">{result.tie_rate:.1f}%</div>
          </div>
          <div class="edge-metric">
            <div class="edge-metric-label">失败 LOSE</div>
            <div class="edge-metric-value">{result.lose_rate:.1f}%</div>
          </div>
          <div class="edge-metric">
            <div class="edge-metric-label">当前牌型</div>
            <div class="edge-metric-value">{result.hero_hand_type}</div>
          </div>
          <div class="edge-metric">
            <div class="edge-metric-label">起手牌评级</div>
            <div class="edge-metric-value">{result.preflop_grade} 级</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="edge-panel" style="margin-top:0.7rem;">
          <div style="color:#9FAAA3;font-size:0.84rem;">当前阶段</div>
          <div style="color:#F3F1E8;font-weight:760;margin-bottom:0.45rem;">{result.stage}</div>
          <div style="color:#9FAAA3;font-size:0.84rem;">稳定度</div>
          <div style="color:#F3F1E8;font-weight:760;margin-bottom:0.45rem;">{result.confidence} · {result.simulations:,} 次模拟</div>
          <div style="color:#9FAAA3;font-size:0.84rem;">起手牌说明</div>
          <div style="color:#F3F1E8;font-weight:760;">{result.preflop_combo} · {result.preflop_comment}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    actions = st.columns(2, gap="small")
    with actions[0]:
        if st.button("重新选择", key="reset_after_result", use_container_width=True):
            reset_selection()
            st.rerun()
    with actions[1]:
        if st.button("保存本次结果", key="save_result", use_container_width=True):
            if st.session_state.last_record:
                save_record(st.session_state.last_record)
                st.success("本次结果已保存到最近记录。")


def render_history() -> None:
    with st.expander("最近记录", expanded=bool(st.session_state.history)):
        if not st.session_state.history:
            st.caption("还没有保存的计算记录。")
            return

        for record in st.session_state.history:
            st.markdown(
                f"""
                <div class="edge-history-item">
                  <div class="edge-history-top">{record["hero"]} · {record["stage"]} · {record["players"]}人</div>
                  <div class="edge-history-bottom">公共牌：{record["board"]} · {record["simulations"]:,}次 · WIN {record["win_rate"]:.1f}% / TIE {record["tie_rate"]:.1f}% / LOSE {record["lose_rate"]:.1f}%</div>
                  <div class="edge-history-bottom">牌型：{record["hero_hand_type"]} · 起手牌评级：{record["preflop_grade"]}级</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_preflop_hint() -> None:
    hero = hero_cards_for_calc()
    if len(hero) != 2:
        return
    grade = grade_preflop(hero)
    st.markdown(
        f"""
        <div class="edge-panel" style="margin-top:0.75rem;">
          <div style="color:#D6A84F;font-weight:820;">起手牌评级：{grade.grade} 级 · {grade.combo}</div>
          <div style="color:#9FAAA3;margin-top:0.24rem;">{grade.comment}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_calculation() -> None:
    hero = hero_cards_for_calc()
    board = board_cards_for_calc()
    try:
        validate_simulation_inputs(hero, board, st.session_state.player_count, st.session_state.simulations)
        with st.spinner("正在模拟胜率，请稍候..."):
            result = run_monte_carlo(
                hero_cards=hero,
                board_cards=board,
                player_count=st.session_state.player_count,
                simulations=st.session_state.simulations,
            )
        record = build_record(result)
        st.session_state.last_result = result
        st.session_state.last_record = record
        save_record(record)
        st.success("计算完成。结果已加入最近记录。")
    except ValueError as exc:
        st.error(str(exc))
    except Exception:
        st.error("计算过程中遇到异常，请检查已选牌面后重试。")


def main() -> None:
    st.set_page_config(
        page_title="Texas Edge",
        page_icon="♠",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    init_state()
    apply_styles()

    st.markdown(
        """
        <section class="edge-hero">
          <div class="edge-kicker">Texas Hold'em Equity Lab</div>
          <h1 class="edge-title">Texas Edge</h1>
          <p class="edge-subtitle">德州扑克胜率分析器 · 手机端德州扑克胜率、牌型与起手牌分析工具。</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    render_hero_slots()
    render_board_slots()
    render_preflop_hint()
    render_player_controls()
    render_simulation_controls()
    render_card_picker()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("计算胜率", key="calculate", type="primary", use_container_width=True):
        run_calculation()

    if st.session_state.last_result:
        render_result(st.session_state.last_result)

    render_history()


if __name__ == "__main__":
    main()
