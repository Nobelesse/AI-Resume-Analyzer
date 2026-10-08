"""Load first-party styling without interpolating user-provided content."""
from pathlib import Path
import streamlit as st

STYLE_PATH = Path(__file__).resolve().parents[1] / "assets" / "styles.css"


def inject_theme() -> None:
    css = STYLE_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
