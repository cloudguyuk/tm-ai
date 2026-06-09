import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import (
    inject_css, render_nav, get_settings, settings_complete, PROVIDERS,
    AZURE_MI_ENV, env_truthy,
)

st.set_page_config(
    page_title="TM-AI · Settings",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("settings")

# ── Back button ───────────────────────────────────────────────────────────────
if st.button("← Back to Threat Model", key="go_home"):
    st.switch_page("home.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Load current saved values ─────────────────────────────────────────────────
s = get_settings()

# ── Layout: two columns ───────────────────────────────────────────────────────
col_form, col_gap, col_info = st.columns([5, 0.4, 4])

with col_form:

    # ── Card: Provider & Model ────────────────────────────────────────────────
    st.markdown("""
    <div class="settings-card">
        <div class="settings-card-title">🔌 &nbsp; Provider &amp; Model</div>
    </div>
    """, unsafe_allow_html=True)

    provider_name = st.selectbox(
        "Provider",
        list(PROVIDERS.keys()),
        index=list(PROVIDERS.keys()).index(s["provider_name"]),
        key="sel_provider",
    )
    provider_cfg = PROVIDERS[provider_name]

    model_list = provider_cfg["models"]
    default_model = s["model"] if s["model"] in model_list else model_list[0]
    model_choice = st.selectbox(
        "Model",
        model_list,
        index=model_list.index(default_model),
        key="sel_model",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Card: API Credentials ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="settings-card">
        <div class="settings-card-title">🔑 &nbsp; API Credentials</div>
    </div>
    """, unsafe_allow_html=True)

    # Managed identity (Azure only). It can be forced on via an environment
    # variable, in which case the toggle is locked and the API key is ignored.
    mi_forced = env_truthy(AZURE_MI_ENV)
    if provider_cfg["is_azure"]:
        use_managed_identity = st.checkbox(
            "Use Azure Managed Identity (no API key)",
            value=mi_forced or st.session_state.get("cfg_azure_use_mi", False),
            disabled=mi_forced,
            key="chk_azure_mi",
            help=(
                "Authenticate to Azure OpenAI using the container app's managed "
                "identity instead of an API key. The identity needs the "
                "'Cognitive Services OpenAI User' role on the resource."
            ),
        )
        if mi_forced:
            st.caption(f"🔒 Forced on by {AZURE_MI_ENV} — API key entry is disabled.")
    else:
        use_managed_identity = False

    # Only pre-fill the field with a key the user explicitly entered/saved in
    # this session. Keys sourced from the environment are never written into the
    # input value (so they aren't sent to the browser / rendered in the DOM).
    env_key_present = bool(os.environ.get(provider_cfg["key_env"]))
    saved_key       = st.session_state.get("cfg_api_key", "")

    if use_managed_identity:
        # Managed identity overrides the API key entirely.
        api_key_input = ""
        api_key = ""
        st.caption("🛡️ Using the host's Azure managed identity — no API key required.")
    else:
        api_key_input = st.text_input(
            provider_cfg["key_label"],
            value=saved_key,
            type="password",
            placeholder=(
                f"Detected from {provider_cfg['key_env']} — leave blank to use it"
                if env_key_present
                else f"Enter your {provider_cfg['key_label']}…"
            ),
            key="inp_api_key",
        )

        # Fall back to the environment-provided key when the user leaves it
        # blank, without ever exposing that value in the input field.
        api_key = api_key_input or os.environ.get(provider_cfg["key_env"], "")

        if env_key_present and not api_key_input:
            st.caption(f"🔑 Using {provider_cfg['key_label']} from the environment.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Card: Azure-specific ──────────────────────────────────────────────────
    if provider_cfg["is_azure"]:
        st.markdown("""
        <div class="settings-card">
            <div class="settings-card-title">☁️ &nbsp; Azure Configuration</div>
        </div>
        """, unsafe_allow_html=True)

        azure_api_base = st.text_input(
            "Azure Endpoint",
            value=s["azure_api_base"] or os.environ.get("AZURE_API_BASE", ""),
            placeholder="https://<resource>.openai.azure.com/",
            key="inp_azure_base",
        )
        azure_api_version = st.text_input(
            "API Version",
            value=s["azure_api_version"] or os.environ.get("AZURE_API_VERSION", "2024-02-01"),
            key="inp_azure_version",
        )
        # Deployment name is taken from the environment; if unset it falls
        # back to the selected model name in build_litellm_model_string.
        azure_deployment = os.environ.get("AZURE_API_DEPLOYMENT", "")
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        azure_api_base    = ""
        azure_api_version = "2024-02-01"
        azure_deployment  = ""

    # ── Save button ───────────────────────────────────────────────────────────
    col_save, col_clear = st.columns([3, 1])
    with col_save:
        if st.button("💾  Save Settings", use_container_width=True, key="btn_save"):
            st.session_state["cfg_provider"]          = provider_name
            st.session_state["cfg_model"]             = model_choice
            st.session_state["cfg_api_key"]           = api_key_input
            st.session_state["cfg_azure_use_mi"]      = use_managed_identity
            st.session_state["cfg_azure_api_base"]    = azure_api_base
            st.session_state["cfg_azure_api_version"] = azure_api_version
            st.session_state["cfg_azure_deployment"]  = azure_deployment
            st.success("Settings saved — ready to threat model.")

    with col_clear:
        if st.button("✕  Clear", use_container_width=True, key="btn_clear"):
            for k in ["cfg_provider","cfg_model","cfg_api_key","cfg_azure_use_mi",
                      "cfg_azure_api_base","cfg_azure_api_version","cfg_azure_deployment"]:
                st.session_state.pop(k, None)
            st.rerun()

# ── Right column: info panel ──────────────────────────────────────────────────
with col_info:
    st.markdown("""
    <div class="settings-card" style="margin-top:0;">
        <div class="settings-card-title">📡 &nbsp; Supported Providers</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.78rem; color:var(--text-muted); line-height:2;">
            <strong style="color:#ff8c00;">Anthropic</strong><br>
            claude-sonnet-4, claude-opus-4,<br>
            claude-haiku-3-5<br><br>
            <strong style="color:#00c8ff;">Azure OpenAI</strong><br>
            gpt-5.5, gpt-5.4, gpt-5.4-mini,<br>
            gpt-5.1, gpt-5, gpt-5-mini,<br>
            gpt-4.1, gpt-4.1-mini, gpt-4.1-nano,<br>
        </div>
    </div>

    <div class="settings-card">
        <div class="settings-card-title">🔒 &nbsp; Privacy</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.76rem; color:var(--text-muted); line-height:1.85;">
            API keys are stored in Streamlit session state only — they are never written to disk or sent anywhere other than the chosen provider's API endpoint.<br><br>
            Keys are cleared when the browser tab is closed.
        </div>
    </div>

    <div class="settings-card">
        <div class="settings-card-title">⚡ &nbsp; Powered By</div>
        <div style="font-family:'Space Mono',monospace; font-size:0.76rem; color:var(--text-muted); line-height:1.85;">
            <span style="color:#ff8c00;">LiteLLM</span> — a unified interface for 100+ LLM providers.<br><br>
            All requests use the <code style="color:var(--text-soft);">completion()</code> API, making it easy to swap providers without changing code.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current config status
    s_live = get_settings()
    if settings_complete():
        st.markdown(f"""
        <div class="config-badge">✓ &nbsp; Configured: {s_live["provider_name"]} · {s_live["model"]}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="config-badge warning">⚠ &nbsp; Not yet configured</div>
        """, unsafe_allow_html=True)
