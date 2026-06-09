import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    inject_css, render_nav, get_system_prompt, SYSTEM_PROMPT, PROMPT_SESSION_KEY,
)

st.set_page_config(
    page_title="TM-AI · Prompt",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("prompt")

# ── Back button ───────────────────────────────────────────────────────────────
if st.button("← Back to Threat Model", key="go_home"):
    st.switch_page("home.py")

st.markdown("<br>", unsafe_allow_html=True)

# Whether the active prompt differs from the built-in default.
is_customised = bool(st.session_state.get(PROMPT_SESSION_KEY))

# ── Layout: editor + info panel ───────────────────────────────────────────────
col_form, col_gap, col_info = st.columns([6, 0.4, 3])

with col_form:
    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">📝 &nbsp; Threat Model System Prompt</div>
    </div>
    """, unsafe_allow_html=True)

    prompt_input = st.text_area(
        "System prompt",
        value=get_system_prompt(),
        height=460,
        key="inp_system_prompt",
        help="This prompt instructs the model how to produce the threat model. "
             "Edits apply to this session only and are not saved to disk.",
    )

    col_save, col_reset = st.columns([3, 1])
    with col_save:
        if st.button("💾  Use This Prompt", use_container_width=True, key="btn_save_prompt"):
            if prompt_input.strip():
                st.session_state[PROMPT_SESSION_KEY] = prompt_input
                st.success("Prompt updated for this session.")
                st.rerun()
            else:
                st.warning("The prompt cannot be empty.")

    with col_reset:
        if st.button("↺  Reset", use_container_width=True, key="btn_reset_prompt"):
            st.session_state.pop(PROMPT_SESSION_KEY, None)
            st.rerun()

# ── Right column: info panel ──────────────────────────────────────────────────
with col_info:
    if is_customised:
        st.markdown("""
        <div class="config-badge warning">✎ &nbsp; Using a custom prompt</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="config-badge">✓ &nbsp; Using the default prompt</div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="settings-card" style="margin-top:1rem;">
        <div class="settings-card-title">ℹ️ &nbsp; About</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.76rem; color:var(--text-muted); line-height:1.85;">
            This is the <strong style="color:#ff8c00;">system prompt</strong> sent to the
            model alongside your system description when you run a threat model.<br><br>
            Tweak it to change the methodology, output structure, tone, or focus areas.
        </div>
    </div>

    <div class="settings-card">
        <div class="settings-card-title">🔒 &nbsp; Not Persisted</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.76rem; color:var(--text-muted); line-height:1.85;">
            Changes are stored in Streamlit session state only — never written to
            disk.<br><br>
            <strong style="color:var(--text-soft);">↺ Reset</strong> restores the built-in
            default. Closing the browser tab also clears your edits.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "⚠️ The default prompt requires strict JSON output. If you change the "
        "output format, the results view may not render correctly."
    )
