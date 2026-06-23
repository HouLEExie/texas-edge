"""Streamlit styling for Texas Edge."""

from __future__ import annotations

import streamlit as st


CSS = """
:root {
  --edge-bg: #07110D;
  --edge-card: #111A16;
  --edge-card-2: #0F2A1E;
  --edge-green: #1DB954;
  --edge-gold: #D6A84F;
  --edge-red: #B43A3A;
  --edge-text: #F3F1E8;
  --edge-muted: #9FAAA3;
  --edge-line: rgba(214, 168, 79, 0.20);
}

.stApp {
  background:
    radial-gradient(circle at top left, rgba(29, 185, 84, 0.12), transparent 30rem),
    linear-gradient(160deg, #07110D 0%, #0B1711 48%, #06100C 100%);
  color: var(--edge-text);
}

header[data-testid="stHeader"] {
  background: transparent;
}

div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
#MainMenu,
footer {
  visibility: hidden;
  height: 0;
}

.block-container {
  max-width: 760px;
  padding: 0.8rem 0.72rem 2.5rem;
}

h1, h2, h3, p, label, span, div {
  letter-spacing: 0;
}

.edge-hero {
  padding: 0.45rem 0 0.35rem;
}

.edge-kicker {
  color: var(--edge-gold);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.edge-title {
  color: var(--edge-text);
  font-size: clamp(1.55rem, 7vw, 2.45rem);
  line-height: 1.02;
  font-weight: 850;
  margin: 0.15rem 0 0.25rem;
}

.edge-subtitle {
  color: var(--edge-muted);
  font-size: 0.82rem;
  margin: 0;
}

.edge-section-title {
  align-items: center;
  color: var(--edge-text);
  display: flex;
  font-size: 0.9rem;
  font-weight: 780;
  gap: 0.45rem;
  margin: 0.58rem 0 0.26rem;
}

.edge-section-title::before {
  background: var(--edge-gold);
  border-radius: 999px;
  content: "";
  display: inline-block;
  height: 0.7rem;
  width: 0.25rem;
}

.edge-card-slot {
  align-items: center;
  aspect-ratio: 1.65;
  background:
    linear-gradient(180deg, rgba(243, 241, 232, 0.06), rgba(243, 241, 232, 0.02)),
    var(--edge-card);
  border: 1px solid var(--edge-line);
  border-radius: 8px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 10px 24px rgba(0,0,0,0.24);
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 68px;
  padding: 0.35rem 0.25rem;
  text-align: center;
}

.edge-card-slot.active {
  border-color: var(--edge-green);
  box-shadow: 0 0 0 2px rgba(29,185,84,0.18), 0 12px 24px rgba(0,0,0,0.26);
}

.edge-card-face {
  color: var(--edge-text);
  font-size: clamp(1.15rem, 6vw, 1.75rem);
  font-weight: 850;
  line-height: 1;
}

.edge-card-face.red {
  color: #F06A6A;
}

.edge-card-label {
  color: var(--edge-muted);
  font-size: 0.62rem;
  margin-top: 0.18rem;
}

.edge-pill {
  background: rgba(15, 42, 30, 0.86);
  border: 1px solid rgba(214, 168, 79, 0.18);
  border-radius: 999px;
  color: var(--edge-muted);
  display: inline-flex;
  font-size: 0.74rem;
  font-weight: 650;
  margin: 0.08rem 0 0.18rem;
  padding: 0.24rem 0.52rem;
}

.edge-panel {
  background: rgba(17, 26, 22, 0.82);
  border: 1px solid rgba(214, 168, 79, 0.16);
  border-radius: 8px;
  box-shadow: 0 16px 38px rgba(0,0,0,0.25);
  padding: 0.58rem;
}

.edge-result-grid {
  display: grid;
  gap: 0.42rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 0.32rem;
}

.edge-metric {
  background: linear-gradient(180deg, rgba(243,241,232,0.055), rgba(243,241,232,0.015));
  border: 1px solid rgba(214,168,79,0.15);
  border-radius: 8px;
  min-height: 62px;
  padding: 0.52rem;
}

.edge-metric.win {
  background:
    linear-gradient(135deg, rgba(29,185,84,0.24), rgba(214,168,79,0.08)),
    #111A16;
  border-color: rgba(29,185,84,0.45);
  grid-column: 1 / -1;
  min-height: 84px;
}

.edge-metric-label {
  color: var(--edge-muted);
  font-size: 0.68rem;
  font-weight: 760;
  text-transform: uppercase;
}

.edge-metric-value {
  color: var(--edge-text);
  font-size: 1.05rem;
  font-weight: 850;
  line-height: 1.12;
  margin-top: 0.25rem;
  overflow-wrap: anywhere;
}

.edge-metric.win .edge-metric-value {
  color: var(--edge-green);
  font-size: clamp(2.05rem, 12vw, 3.6rem);
}

.edge-history-item {
  border-bottom: 1px solid rgba(243,241,232,0.08);
  padding: 0.52rem 0;
}

.edge-history-item:last-child {
  border-bottom: 0;
}

.edge-history-top {
  color: var(--edge-text);
  font-weight: 760;
}

.edge-history-bottom {
  color: var(--edge-muted);
  font-size: 0.74rem;
  margin-top: 0.2rem;
}

.stButton > button {
  background: rgba(17, 26, 22, 0.94);
  border: 1px solid rgba(214, 168, 79, 0.18);
  border-radius: 8px;
  color: var(--edge-text);
  min-height: 2.12rem;
  padding: 0.18rem 0.35rem;
  transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.stButton > button:hover {
  border-color: var(--edge-gold);
  box-shadow: 0 0 0 2px rgba(214, 168, 79, 0.12);
  color: var(--edge-text);
}

.stButton > button:active {
  transform: translateY(1px);
}

.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #1DB954, #138A3E);
  border: 1px solid rgba(29,185,84,0.7);
  color: #06100C;
  font-weight: 850;
  min-height: 2.72rem;
}

button[disabled] {
  opacity: 0.36;
}

div[data-testid="stSlider"] {
  padding: 0 0 0.25rem;
}

div[data-testid="stVerticalBlock"] {
  gap: 0.28rem;
}

div[data-testid="stHorizontalBlock"] {
  gap: 0.35rem;
}

div[data-testid="stExpander"] details {
  background: rgba(17, 26, 22, 0.72);
  border-color: rgba(214, 168, 79, 0.16);
  border-radius: 8px;
}

div[data-testid="stAlert"] {
  border-radius: 8px;
}

@media (max-width: 520px) {
  .block-container {
    padding: 0.35rem 0.45rem 1.8rem;
  }

  .edge-panel {
    padding: 0.48rem;
  }

  .edge-card-slot {
    aspect-ratio: 1.8;
    min-height: 52px;
  }

  .edge-title {
    font-size: 1.62rem;
  }

  .edge-subtitle {
    font-size: 0.76rem;
  }

  .stButton > button {
    min-height: 1.95rem;
    font-size: 0.78rem;
  }

  .stButton > button[kind="primary"] {
    min-height: 2.45rem;
  }

  .edge-metric {
    min-height: 54px;
  }

  .edge-metric.win {
    min-height: 74px;
  }
}
"""


def apply_styles() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
