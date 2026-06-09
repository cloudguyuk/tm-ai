"""Shared constants, CSS, and helpers for TM-AI."""
import os
import json
import base64
import streamlit as st
from dotenv import load_dotenv
from litellm import completion

# Load variables from a local .env file (if present) into the environment.
load_dotenv()

# ── Provider / model definitions ─────────────────────────────────────────────
PROVIDERS = {
    "Anthropic (Claude)": {
        "models": [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-haiku-3-5-20241022",
        ],
        "litellm_prefix": "",
        "key_label": "ANTHROPIC_API_KEY",
        "key_env":   "ANTHROPIC_API_KEY",
        "is_azure":  False,
    },
    "Azure OpenAI": {
        "models": [
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.1",
            "gpt-5-mini",
            "gpt-4.1-mini",
        ],
        "litellm_prefix": "azure/",
        "key_label": "AZURE_OPENAI_API_KEY",
        "key_env":   "AZURE_API_KEY",
        "is_azure":  True,
    },
}

# Environment variable that forces Azure authentication to use the container
# app's managed identity instead of an API key. When set to a truthy value the
# API-key entry is disabled/ignored entirely (see get_settings / the UI).
AZURE_MI_ENV = "AZURE_USE_MANAGED_IDENTITY"

# OAuth scope used when requesting an Azure AD token for Azure OpenAI.
AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


def env_truthy(name: str) -> bool:
    """Return True when an environment variable is set to a truthy value."""
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


SYSTEM_PROMPT = """You are an expert security architect and threat modeller with deep knowledge of STRIDE, MITRE ATT&CK, and OWASP methodologies.

When given a system description, produce a comprehensive threat model as a JSON object with this exact structure:
{
  "summary": "2-3 sentence overview of the system and key risk areas",
  "threats": [
    {
      "id": "T-001",
      "category": "STRIDE category (Spoofing|Tampering|Repudiation|Information Disclosure|Denial of Service|Elevation of Privilege)",
      "title": "Short threat title",
      "severity": "Critical|High|Medium|Low",
      "description": "Clear explanation of the threat and how it could be exploited",
      "mitigation": "Concrete, actionable mitigation steps"
    }
  ]
}

Return ONLY valid JSON. No markdown fences, no preamble."""

# Session-state key holding a user-edited copy of the system prompt. Edits made
# on the Prompt page live here for the duration of the session only — they are
# never written to disk, so the default SYSTEM_PROMPT is restored on restart.
PROMPT_SESSION_KEY = "cfg_system_prompt"


def get_system_prompt() -> str:
    """Return the active threat-model system prompt.

    A prompt edited in this session (stored in session_state) takes precedence;
    otherwise the built-in default SYSTEM_PROMPT is used.
    """
    return st.session_state.get(PROMPT_SESSION_KEY) or SYSTEM_PROMPT

SEVERITY_CSS = {
    "critical": "severity-critical",
    "high":     "severity-high",
    "medium":   "severity-medium",
    "low":      "severity-low",
}

# ── Theme tokens ──────────────────────────────────────────────────────────────
# Each theme defines the colour variables consumed (via var(--token)) by BASE_CSS.
# The brand accents (orange / cyan / red) are intentionally shared across themes.
THEME_KEY = "ui_theme"  # session_state key: "dark" | "light"

THEMES = {
    "dark": """
    --bg: #0a0c10;
    --text: #f1f5f9;
    --text-soft: #c0cdda;
    --text-muted: #9fb1c4;
    --surface: #0f1318;
    --input-text: #c9d8e8;
    --card: rgba(20,26,34,0.7);
    --card-2: rgba(25,31,40,0.65);
    --border: #28384a;
    --shadow: 0 8px 24px rgba(0,0,0,0.35);
    --glow:
        radial-gradient(1200px 600px at 85% -10%, rgba(255,140,0,0.10), transparent 60%),
        radial-gradient(1000px 500px at 0% 110%, rgba(0,200,255,0.06), transparent 55%);
    """,
    "light": """
    --bg: #eef2f7;
    --text: #0f1722;
    --text-soft: #33424f;
    --text-muted: #5a6b7d;
    --surface: #ffffff;
    --input-text: #1a2530;
    --card: rgba(255,255,255,0.82);
    --card-2: rgba(255,255,255,0.72);
    --border: #d4dde6;
    --shadow: 0 10px 30px rgba(15,23,34,0.10);
    --glow:
        radial-gradient(1200px 600px at 85% -10%, rgba(255,140,0,0.13), transparent 60%),
        radial-gradient(1000px 500px at 0% 110%, rgba(0,200,255,0.10), transparent 55%);
    """,
}

def current_theme() -> str:
    """Return the active theme name, defaulting to dark."""
    return "light" if st.session_state.get(THEME_KEY) == "light" else "dark"

# ── Shared CSS ────────────────────────────────────────────────────────────────
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
.stApp {
    background-color: var(--bg);
    background-image: var(--glow);
    background-attachment: fixed;
}

/* Force theme text colour onto Streamlit's native text elements (these
   otherwise inherit Streamlit's own base theme and break in light mode). */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp li, .stApp label,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"] { color: var(--text); }

textarea::placeholder, input::placeholder { color: var(--text-muted) !important; opacity: 1 !important; }

/* File uploader dropzone */
[data-testid="stFileUploaderDropzone"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-soft) !important;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text-soft) !important; }

/* hide default sidebar nav */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"]    { display: none !important; }

/* ── Header ── */
.tm-logo {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -2px;
    color: #ff8c00;
    text-shadow: 0 0 30px rgba(255,140,0,0.45);
    line-height: 1;
}
.tm-logo span { color: #ff4b6e; }
.tm-tagline {
    font-size: 0.82rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}
.tm-divider {
    height: 1px;
    background: linear-gradient(90deg, #ff8c00 0%, rgba(255,140,0,0.1) 60%, transparent 100%);
    margin: 0.8rem 0 1.8rem 0;
}

/* ── Nav bar ── */
.tm-nav-logo {
    padding-top: 1.6rem;
    margin-bottom: 0;
}

/* Style st.page_link nav buttons */
[data-testid="stPageLink"] a {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 5px 14px !important;
    border-radius: 4px !important;
    border: 1px solid var(--border) !important;
    background: transparent !important;
    color: var(--text-muted) !important;
    text-decoration: none !important;
}
[data-testid="stPageLink-active"] a {
    border-color: rgba(255,140,0,0.35) !important;
    color: #ff8c00 !important;
    background: rgba(255,140,0,0.06) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #ff8c00, #00c8ff) !important;
    color: #0a0c10 !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.65rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(255,140,0,0.25) !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 0 35px rgba(255,140,0,0.45) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* secondary / ghost button */
.stButton.secondary > button,
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-muted) !important;
    box-shadow: none !important;
}

/* ── Text area ── */
textarea {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.88rem !important;
    background-color: var(--surface) !important;
    color: var(--input-text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    caret-color: #ff8c00 !important;
}
textarea:focus { border-color: #ff8c00 !important; box-shadow: 0 0 0 2px rgba(255,140,0,0.12) !important; }

/* ── Inputs & selects ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--input-text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input[type="password"] { letter-spacing: 0.15em; }
.stTextInput label, .stSelectbox label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ── Results ── */
.result-block {
    background: var(--card);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-left: 3px solid #ff8c00;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.84rem;
    line-height: 1.7;
    box-shadow: var(--shadow);
}
.result-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #ff8c00;
    margin-bottom: 0.6rem;
}
.threat-item {
    background: var(--card-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.threat-item:hover { border-color: rgba(255,140,0,0.35); transform: translateY(-1px); }
.threat-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.05rem; color: #ff5c7c; margin-bottom: 0.3rem; }
.threat-meta {
    display: inline-block;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 3px;
    margin-right: 6px;
    margin-bottom: 6px;
    font-family: 'Space Mono', monospace;
}
.severity-critical { background: rgba(255,75,110,0.18);  color: #ff4b6e; border: 1px solid rgba(255,75,110,0.3); }
.severity-high     { background: rgba(255,150,50,0.18);   color: #ff9632; border: 1px solid rgba(255,150,50,0.3); }
.severity-medium   { background: rgba(255,210,50,0.18);   color: #ffd232; border: 1px solid rgba(255,210,50,0.3); }
.severity-low      { background: rgba(255,140,0,0.12);    color: #ff8c00; border: 1px solid rgba(255,140,0,0.2); }
.threat-desc { color: var(--text-soft); font-size: 0.83rem; line-height: 1.6; margin-top: 0.4rem; }
.mitigation { color: var(--text-muted); font-size: 0.78rem; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border); }
.mitigation strong { color: #00c8ff; }

/* ── Settings cards ── */
.settings-card {
    background: var(--card);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
}
.settings-card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #ff8c00;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.config-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    padding: 3px 10px;
    border-radius: 3px;
    background: rgba(255,140,0,0.07);
    color: #ff8c00;
    border: 1px solid rgba(255,140,0,0.18);
    margin-top: 0.4rem;
}
.config-badge.warning {
    background: rgba(255,150,50,0.07);
    color: #ff9632;
    border-color: rgba(255,150,50,0.2);
}

.stSpinner > div { border-top-color: #ff8c00 !important; }
.stAlert { background: var(--surface) !important; border: 1px solid var(--border) !important; color: var(--text-soft) !important; }
.stTextArea label { font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 0.1em !important; color: var(--text-muted) !important; text-transform: uppercase !important; }
</style>
"""

def inject_css():
    """Inject the active theme's variables followed by the shared stylesheet."""
    theme_vars = THEMES.get(current_theme(), THEMES["dark"])
    st.markdown(f"<style>:root {{{theme_vars}}}</style>", unsafe_allow_html=True)
    st.markdown(BASE_CSS, unsafe_allow_html=True)

def _sync_theme():
    """Mirror the toggle's state into THEME_KEY (runs before the script reruns,
    so inject_css picks up the new theme on the same interaction)."""
    st.session_state[THEME_KEY] = "light" if st.session_state.get("_theme_toggle") else "dark"

def render_nav(active: str):
    """Render the top nav bar. active = 'home' | 'settings'"""
    col_logo, col_links = st.columns([8, 2])
    with col_logo:
        st.markdown("""
        <div class="tm-nav-logo">
            <div class="tm-logo">TM<span>-</span>AI</div>
            <div class="tm-tagline">AI-Powered Threat Modelling</div>
        </div>
        """, unsafe_allow_html=True)
    with col_links:
        st.markdown("<div style='padding-top:1.6rem; display:flex; gap:6px;'>", unsafe_allow_html=True)
        st.page_link("pages/prompt.py", label="📝 Prompt")
        st.page_link("pages/settings.py", label="⚙️ Settings")
        st.toggle(
            "☀️ Light mode",
            key="_theme_toggle",
            on_change=_sync_theme,
            help="Switch between dark and light mode",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="tm-divider"></div>', unsafe_allow_html=True)

def get_settings() -> dict:
    """Return current settings.

    Values entered in the UI (session_state) take precedence; anything not set
    there falls back to the corresponding environment variable. This lets the
    Azure OpenAI API key, endpoint, deployment, and API version be supplied
    entirely from the environment (e.g. a .env file) with no manual entry.
    """
    provider_name = st.session_state.get("cfg_provider", "Azure OpenAI")
    key_env       = PROVIDERS[provider_name]["key_env"]

    # Managed identity can be forced from the environment (which overrides any
    # API-key configuration) or toggled in the UI for the current session.
    mi_forced = env_truthy(AZURE_MI_ENV)
    use_managed_identity = mi_forced or bool(st.session_state.get("cfg_azure_use_mi", False))

    # When managed identity is in use, the API key is ignored entirely.
    api_key = "" if use_managed_identity else (
        st.session_state.get("cfg_api_key") or os.environ.get(key_env, "")
    )

    return {
        "provider_name": provider_name,
        "model":         st.session_state.get("cfg_model", PROVIDERS[provider_name]["models"][0]),
        "api_key":       api_key,
        "azure_use_managed_identity": use_managed_identity,
        "azure_mi_forced":            mi_forced,
        "azure_api_base":    st.session_state.get("cfg_azure_api_base")    or os.environ.get("AZURE_API_BASE", ""),
        "azure_api_version": st.session_state.get("cfg_azure_api_version") or os.environ.get("AZURE_API_VERSION", "2024-02-01"),
        "azure_deployment":  st.session_state.get("cfg_azure_deployment")  or os.environ.get("AZURE_API_DEPLOYMENT", ""),
    }

def settings_complete() -> bool:
    s = get_settings()
    is_azure = PROVIDERS[s["provider_name"]]["is_azure"]
    # Azure managed identity authenticates without an API key; it still needs
    # the endpoint. All other paths require a key.
    if is_azure and s["azure_use_managed_identity"]:
        return bool(s["azure_api_base"])
    if not s["api_key"]:
        return False
    if is_azure and not s["azure_api_base"]:
        return False
    return True

def build_litellm_model_string(provider_cfg: dict, model: str, azure_deployment: str) -> str:
    if provider_cfg["is_azure"]:
        return f"azure/{azure_deployment or model}"
    return f"{provider_cfg['litellm_prefix']}{model}"

def _azure_managed_identity_token_provider():
    """Build a bearer-token provider backed by the host's managed identity.

    Uses azure.identity's DefaultAzureCredential, which transparently picks up
    the managed identity assigned to the Azure Container App (and falls back to
    other credential sources for local development). An optional
    AZURE_CLIENT_ID selects a specific user-assigned identity.
    """
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError as exc:  # pragma: no cover - surfaced to the user in UI
        raise RuntimeError(
            "Azure managed identity requires the 'azure-identity' package. "
            "Add it to requirements.txt and reinstall."
        ) from exc

    client_id = os.environ.get("AZURE_CLIENT_ID") or None
    credential = DefaultAzureCredential(managed_identity_client_id=client_id)
    return get_bearer_token_provider(credential, AZURE_OPENAI_SCOPE)


def run_threat_model(description: str, images=None) -> dict:
    s            = get_settings()
    provider_cfg = PROVIDERS[s["provider_name"]]
    model_str    = build_litellm_model_string(provider_cfg, s["model"], s["azure_deployment"])

    # Build the user message. When diagrams are supplied, send a multimodal
    # content list (text + images) that vision-capable models understand.
    if images:
        user_content = [{"type": "text", "text": description}]
        for img in images:
            b64  = base64.b64encode(img.getvalue()).decode()
            mime = getattr(img, "type", None) or "image/png"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })
    else:
        user_content = description

    kwargs: dict = {
        "model":      model_str,
        "max_tokens": 2500,
        "messages": [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user",   "content": user_content},
        ],
    }
    if provider_cfg["is_azure"] and s["azure_use_managed_identity"]:
        # Authenticate with the container app's managed identity. A bearer-token
        # provider is passed to LiteLLM/the Azure SDK so tokens are fetched and
        # refreshed automatically — no API key is sent.
        kwargs["azure_ad_token_provider"] = _azure_managed_identity_token_provider()
    elif s["api_key"]:
        kwargs["api_key"] = s["api_key"]

    if provider_cfg["is_azure"]:
        if s["azure_api_base"]:
            kwargs["api_base"] = s["azure_api_base"]
        if s["azure_api_version"]:
            kwargs["api_version"] = s["azure_api_version"]

    response = completion(**kwargs)
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def render_threat_results(data: dict):
    st.markdown(f"""
    <div class="result-block">
        <div class="result-title">System Summary</div>
        {data.get("summary", "")}
    </div>
    """, unsafe_allow_html=True)

    threats = data.get("threats", [])
    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:var(--text-muted);
                letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.8rem;">
        {len(threats)} threat(s) identified
    </div>
    """, unsafe_allow_html=True)

    for t in threats:
        sev       = t.get("severity", "Low").lower()
        sev_class = SEVERITY_CSS.get(sev, "severity-low")
        st.markdown(f"""
        <div class="threat-item">
            <div class="threat-title">{t.get("id","")}&nbsp; {t.get("title","")}</div>
            <span class="threat-meta {sev_class}">{t.get("severity","")}</span>
            <span class="threat-meta" style="background:rgba(100,116,139,0.15);color:var(--text-muted);border:1px solid rgba(100,116,139,0.2);">{t.get("category","")}</span>
            <div class="threat-desc">{t.get("description","")}</div>
            <div class="mitigation"><strong>Mitigation:</strong> {t.get("mitigation","")}</div>
        </div>
        """, unsafe_allow_html=True)
