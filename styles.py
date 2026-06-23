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
  padding: 1.25rem 0.85rem 5rem;
}

h1, h2, h3, p, label, span, div {
  letter-spacing: 0;
}

.edge-hero {
  padding: 1.1rem 0 0.75rem;
}

.edge-kicker {
  color: var(--edge-gold);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.edge-title {
  color: var(--edge-text);
  font-size: clamp(2rem, 9vw, 3.1rem);
  line-height: 1.02;
  font-weight: 850;
  margin: 0.15rem 0 0.25rem;
}

.edge-subtitle {
  color: var(--edge-muted);
  font-size: 0.96rem;
  margin: 0;
}

.edge-section-title {
  align-items: center;
  color: var(--edge-text);
  display: flex;
  font-size: 1rem;
  font-weight: 780;
  gap: 0.45rem;
  margin: 1.05rem 0 0.45rem;
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
  aspect-ratio: 0.72;
  background:
    linear-gradient(180deg, rgba(243, 241, 232, 0.06), rgba(243, 241, 232, 0.02)),
    var(--edge-card);
  border: 1px solid var(--edge-line);
  border-radius: 8px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 10px 24px rgba(0,0,0,0.24);
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 96px;
  padding: 0.65rem 0.35rem;
  text-align: center;
}

.edge-card-slot.active {
  border-color: var(--edge-green);
  box-shadow: 0 0 0 2px rgba(29,185,84,0.18), 0 12px 24px rgba(0,0,0,0.26);
}

.edge-card-face {
  color: var(--edge-text);
  font-size: clamp(1.45rem, 8vw, 2.25rem);
  font-weight: 850;
  line-height: 1;
}

.edge-card-face.red {
  color: #F06A6A;
}

.edge-card-label {
  color: var(--edge-muted);
  font-size: 0.72rem;
  margin-top: 0.45rem;
}

.edge-pill {
  background: rgba(15, 42, 30, 0.86);
  border: 1px solid rgba(214, 168, 79, 0.18);
  border-radius: 999px;
  color: var(--edge-muted);
  display: inline-flex;
  font-size: 0.82rem;
  font-weight: 650;
  margin: 0.15rem 0 0.35rem;
  padding: 0.34rem 0.68rem;
}

.edge-panel {
  background: rgba(17, 26, 22, 0.82);
  border: 1px solid rgba(214, 168, 79, 0.16);
  border-radius: 8px;
  box-shadow: 0 16px 38px rgba(0,0,0,0.25);
  padding: 0.85rem;
}

.edge-result-grid {
  display: grid;
  gap: 0.65rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 0.5rem;
}

.edge-metric {
  background: linear-gradient(180deg, rgba(243,241,232,0.055), rgba(243,241,232,0.015));
  border: 1px solid rgba(214,168,79,0.15);
  border-radius: 8px;
  min-height: 92px;
  padding: 0.8rem;
}

.edge-metric.win {
  background:
    linear-gradient(135deg, rgba(29,185,84,0.24), rgba(214,168,79,0.08)),
    #111A16;
  border-color: rgba(29,185,84,0.45);
  grid-column: 1 / -1;
  min-height: 134px;
}

.edge-metric-label {
  color: var(--edge-muted);
  font-size: 0.78rem;
  font-weight: 760;
  text-transform: uppercase;
}

.edge-metric-value {
  color: var(--edge-text);
  font-size: 1.45rem;
  font-weight: 850;
  line-height: 1.12;
  margin-top: 0.25rem;
  overflow-wrap: anywhere;
}

.edge-metric.win .edge-metric-value {
  color: var(--edge-green);
  font-size: clamp(3rem, 18vw, 5.2rem);
}

.edge-history-item {
  border-bottom: 1px solid rgba(243,241,232,0.08);
  padding: 0.75rem 0;
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
  font-size: 0.82rem;
  margin-top: 0.2rem;
}

.stButton > button {
  background: rgba(17, 26, 22, 0.94);
  border: 1px solid rgba(214, 168, 79, 0.18);
  border-radius: 8px;
  color: var(--edge-text);
  min-height: 2.65rem;
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
  min-height: 3.25rem;
}

button[disabled] {
  opacity: 0.36;
}

div[data-testid="stSlider"] {
  padding: 0.2rem 0 0.6rem;
}

div[data-testid="stAlert"] {
  border-radius: 8px;
}

@media (max-width: 520px) {
  .block-container {
    padding-left: 0.72rem;
    padding-right: 0.72rem;
  }

  .edge-panel {
    padding: 0.7rem;
  }

  .edge-card-slot {
    min-height: 78px;
  }
}
"""


def apply_styles() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
