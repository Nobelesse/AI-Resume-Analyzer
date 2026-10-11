"""Reusable presentation utilities; all authorization remains server-side."""
import html


def page_header(kicker: str, title: str, description: str, icon: str = "✦") -> None:
    """Render a consistent, static, escaped header without inserting user HTML."""
    parts = [html.escape(str(x), quote=True) for x in (kicker, title, description, icon)]
    import streamlit as st
    st.markdown(
        '<section class="uim2-header">'
        f'<div class="uim2-kicker"><span class="uim2-spark">{parts[3]}</span>{parts[0]}</div>'
        f'<h1>{parts[1]}</h1><p>{parts[2]}</p>'
        '</section>', unsafe_allow_html=True,
    )


def step_label(step: str, text: str) -> None:
    import streamlit as st
    st.markdown(
        f'<div class="uim2-step"><span>{html.escape(str(step))}</span>'
        f'{html.escape(str(text))}</div>', unsafe_allow_html=True,
    )


def section_heading(text: str, description: str = "") -> None:
    import streamlit as st
    st.markdown(
        f'<div class="uim2-section-title">{html.escape(text)}</div>'
        f'<div class="uim2-section-caption">{html.escape(description)}</div>',
        unsafe_allow_html=True,
    )
