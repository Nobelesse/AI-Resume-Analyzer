"""Reusable presentational components (no sensitive or user-supplied HTML)."""
from html import escape
import streamlit as st
from app.ui.motion import render_motion_scene

def sidebar_identity() -> None:
    st.markdown('<div class="sidebar-brand"><span class="brand-orbit">✦</span><span>RESUME<span class="brand-accent">INTEL</span></span></div>', unsafe_allow_html=True)

def section_heading(eyebrow: str, title: str, description: str = "") -> None:
    st.markdown(f'<div class="eyebrow">{escape(eyebrow)}</div><h2 class="section-heading">{escape(title)}</h2><p class="section-copy">{escape(description)}</p>', unsafe_allow_html=True)

def metric_tile(label: str, value: str, note: str, kind: str = "violet") -> None:
    classes = {"violet", "cyan", "green"}
    if kind not in classes:
        kind = "violet"
    st.markdown(f'<div class="metric-tile {kind}"><span class="metric-label">{escape(label)}</span><strong>{escape(value)}</strong><small>{escape(note)}</small></div>', unsafe_allow_html=True)

def feature_tile(icon: str, title: str, description: str, flag: str = "PLANNED") -> None:
    st.markdown(f'<div class="feature-card"><div class="card-top"><span class="feature-icon">{escape(icon)}</span><span class="feature-flag">{escape(flag)}</span></div><h3>{escape(title)}</h3><p>{escape(description)}</p><span class="card-arrow">↗</span></div>', unsafe_allow_html=True)

def motion_demo(height: int = 360) -> None:
    render_motion_scene(height=height)
