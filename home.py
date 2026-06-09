import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import inject_css, render_nav, get_settings, settings_complete, run_threat_model, render_threat_results, PROVIDERS

st.set_page_config(
    page_title="TM-AI · Threat Modelling",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("home")

# ── Config status banner ───────────────────────────────────────────────────────
s = get_settings()
provider_cfg = PROVIDERS[s["provider_name"]]

if not settings_complete():
    st.markdown("""
    <div style="background:rgba(255,150,50,0.07); border:1px solid rgba(255,150,50,0.25);
                border-radius:6px; padding:0.8rem 1.2rem; margin-bottom:1.4rem;
                font-family:'Space Mono',monospace; font-size:0.78rem; color:#ff9632;">
        ⚠️ &nbsp; Model not configured — <strong>visit Settings before running a threat model.</strong>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:rgba(255,140,0,0.05); border:1px solid rgba(255,140,0,0.15);
                border-radius:6px; padding:0.7rem 1.2rem; margin-bottom:1.4rem;
                font-family:'Space Mono',monospace; font-size:0.75rem; color:#ff8c00;">
        ✓ Configured Provider / Model : {s["provider_name"]} / {s["model"]}
    </div>
    """, unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_gap, col_output = st.columns([5, 0.3, 6])

with col_input:
    st.markdown("##### Describe Your System")
    user_input = st.text_area(
        label="System description",
        placeholder=(
            "Describe the system, application, or architecture you want to threat model.\n\n"
            "Example:\n"
            "A web application with a React frontend, Node.js API, and PostgreSQL database. "
            "Users authenticate via OAuth2. The app stores PII and payment card data. "
            "It is hosted on AWS using ECS and RDS, behind an ALB."
        ),
        height=320,
        label_visibility="collapsed",
    )

    uploaded_diagrams = st.file_uploader(
        "Architecture diagrams (optional)",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        accept_multiple_files=True,
        help="Upload architecture or data-flow diagrams to enrich the threat model. "
             "Requires a vision-capable model.",
    )

    run_btn = st.button("🛡️  Threat Model", use_container_width=True)

    st.markdown("""
    <div style="margin-top:1.2rem; font-size:0.74rem; color:#334155;
                font-family:'Space Mono',monospace; line-height:1.9;">
        TM-AI uses the STRIDE framework to surface threats across:<br>
        Spoofing · Tampering · Repudiation · Info Disclosure · DoS · Elevation of Privilege
    </div>
    """, unsafe_allow_html=True)

with col_output:
    st.markdown("##### Threat Model Output")

    if run_btn:
        if not user_input.strip():
            st.warning("Please describe your system before running.")
        elif not settings_complete():
            st.warning("Please complete your model settings first — click ⚙️ Settings above.")
        else:
            with st.spinner(f"Analysing threats via {s['provider_name']} · {s['model']}…"):
                try:
                    result = run_threat_model(user_input.strip(), uploaded_diagrams)
                    st.session_state["tm_result"] = result
                    st.session_state["tm_meta"]   = f"{s['provider_name']} · {s['model']}"
                except Exception as e:
                    st.error(f"Error generating threat model: {e}")

    if "tm_result" in st.session_state:
        meta = st.session_state.get("tm_meta", "")
        if meta:
            st.markdown(f"""
            <div style="font-family:'Space Mono',monospace; font-size:0.68rem;
                        color:#334155; margin-bottom:0.8rem;">Generated via {meta}</div>
            """, unsafe_allow_html=True)
        render_threat_results(st.session_state["tm_result"])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋  Generate Summary", use_container_width=True, key="go_summary"):
            st.switch_page("pages/summary.py")
    else:
        st.markdown("""
        <div style="color:#334155; font-family:'Space Mono',monospace; font-size:0.82rem;
                    line-height:1.9; padding-top:0.5rem;">
            Configure your provider in <strong style="color:var(--text-muted);">⚙️ Settings</strong>,
            describe your<br>system on the left, then click
            <strong style="color:#ff8c00;">Threat Model</strong>.<br><br>
            Results will include:<br>
            — Threat ID, category &amp; severity<br>
            — Detailed threat description<br>
            — Actionable mitigations
        </div>
        """, unsafe_allow_html=True)
