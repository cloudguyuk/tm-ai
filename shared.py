"""Shared constants, CSS, and helpers for TM-AI."""
import os
import json
import base64
import streamlit as st
from litellm import completion

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
            "gpt-5.5",
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.1",
            "gpt-5",
            "gpt-5-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ],
        "litellm_prefix": "azure/",
        "key_label": "AZURE_OPENAI_API_KEY",
        "key_env":   "AZURE_API_KEY",
        "is_azure":  True,
    },
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-preview"],
        "litellm_prefix": "",
        "key_label": "OPENAI_API_KEY",
        "key_env":   "OPENAI_API_KEY",
        "is_azure":  False,
    },
}

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

SEVERITY_CSS = {
    "critical": "severity-critical",
    "high":     "severity-high",
    "medium":   "severity-medium",
    "low":      "severity-low",
}

# ── Shared CSS ────────────────────────────────────────────────────────────────
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0c10;
    color: #e2e8f0;
}
.stApp {
    background-color: #0a0c10;
    background-image:
        linear-gradient(rgba(255,140,0,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,140,0,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
}

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
    color: #64748b;
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
    border: 1px solid #1e2a38 !important;
    background: transparent !important;
    color: #64748b !important;
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
    border: 1px solid #1e2a38 !important;
    color: #64748b !important;
    box-shadow: none !important;
}

/* ── Text area ── */
textarea {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.88rem !important;
    background-color: #0f1318 !important;
    color: #c9d8e8 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 6px !important;
    caret-color: #ff8c00 !important;
}
textarea:focus { border-color: #ff8c00 !important; box-shadow: 0 0 0 2px rgba(255,140,0,0.12) !important; }

/* ── Inputs & selects ── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: #0f1318 !important;
    border-color: #1e2a38 !important;
    color: #c9d8e8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input[type="password"] { letter-spacing: 0.15em; }
.stTextInput label, .stSelectbox label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #64748b !important;
}

/* ── Results ── */
.result-block {
    background: #0f1318;
    border: 1px solid #1e2a38;
    border-left: 3px solid #ff8c00;
    border-radius: 6px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.84rem;
    line-height: 1.7;
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
    background: #13181f;
    border: 1px solid #1e2a38;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.threat-title { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 1rem; color: #ff4b6e; margin-bottom: 0.3rem; }
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
.threat-desc { color: #94a3b8; font-size: 0.83rem; line-height: 1.6; margin-top: 0.4rem; }
.mitigation { color: #64748b; font-size: 0.78rem; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #1e2a38; }
.mitigation strong { color: #00c8ff; }

/* ── Settings cards ── */
.settings-card {
    background: #0f1318;
    border: 1px solid #1e2a38;
    border-radius: 8px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}
.settings-card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #ff8c00;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2a38;
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
.stAlert { background: #0f1318 !important; border: 1px solid #1e2a38 !important; color: #94a3b8 !important; }
.stTextArea label { font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 0.1em !important; color: #64748b !important; text-transform: uppercase !important; }
</style>
"""

def inject_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)

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
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            st.page_link("Home.py", label="🛡️ Threat Model")
        with link_col2:
            st.page_link("pages/1_Settings.py", label="⚙️ Settings")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="tm-divider"></div>', unsafe_allow_html=True)

def get_settings() -> dict:
    """Return current settings from session_state with safe defaults."""
    return {
        "provider_name": st.session_state.get("cfg_provider", "Anthropic (Claude)"),
        "model":         st.session_state.get("cfg_model",    "claude-sonnet-4-20250514"),
        "api_key":       st.session_state.get("cfg_api_key",  ""),
        "azure_api_base":    st.session_state.get("cfg_azure_api_base",    ""),
        "azure_api_version": st.session_state.get("cfg_azure_api_version", "2024-02-01"),
        "azure_deployment":  st.session_state.get("cfg_azure_deployment",  ""),
    }

def settings_complete() -> bool:
    s = get_settings()
    if not s["api_key"]:
        return False
    if PROVIDERS[s["provider_name"]]["is_azure"] and not s["azure_api_base"]:
        return False
    return True

def build_litellm_model_string(provider_cfg: dict, model: str, azure_deployment: str) -> str:
    if provider_cfg["is_azure"]:
        return f"azure/{azure_deployment or model}"
    return f"{provider_cfg['litellm_prefix']}{model}"

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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ],
    }
    if s["api_key"]:
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
    <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:#64748b;
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
            <span class="threat-meta" style="background:rgba(100,116,139,0.15);color:#64748b;border:1px solid rgba(100,116,139,0.2);">{t.get("category","")}</span>
            <div class="threat-desc">{t.get("description","")}</div>
            <div class="mitigation"><strong>Mitigation:</strong> {t.get("mitigation","")}</div>
        </div>
        """, unsafe_allow_html=True)
