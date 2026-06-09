import streamlit as st
import sys, os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from shared import inject_css, render_nav

st.set_page_config(
    page_title="TM-AI · Summary",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("home")

# ── Back button ───────────────────────────────────────────────────────────────
if st.button("← Back to Threat Model", key="go_home"):
    st.switch_page("home.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Guard: no data ────────────────────────────────────────────────────────────
if "tm_result" not in st.session_state:
    st.markdown("""
    <div style="background:rgba(255,150,50,0.07); border:1px solid rgba(255,150,50,0.25);
                border-radius:6px; padding:0.8rem 1.2rem;
                font-family:'Space Mono',monospace; font-size:0.78rem; color:#ff9632;">
        ⚠️ &nbsp; No threat model found — please run a threat model on the home page first.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

data    = st.session_state["tm_result"]
meta    = st.session_state.get("tm_meta", "")
threats = data.get("threats", [])

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800;
            color:var(--text); margin-bottom:0.2rem;">Threat Model Summary</div>
""", unsafe_allow_html=True)

if meta:
    st.markdown(f"""
    <div style="font-family:'Space Mono',monospace; font-size:0.68rem;
                color:var(--text-muted); margin-bottom:1.2rem;">Generated via {meta}</div>
    """, unsafe_allow_html=True)

# ── System summary banner ─────────────────────────────────────────────────────
summary_text = data.get("summary", "")
if summary_text:
    st.markdown(f"""
    <div style="background:var(--card); backdrop-filter:blur(8px); border:1px solid var(--border); border-left:3px solid #ff8c00;
                border-radius:10px; padding:1rem 1.4rem; margin-bottom:1.6rem; box-shadow:var(--shadow);
                font-family:'Space Mono',monospace; font-size:0.84rem; color:var(--text-soft); line-height:1.7;">
        <div style="font-family:'Syne',sans-serif; font-size:0.7rem; font-weight:600;
                    letter-spacing:0.18em; text-transform:uppercase; color:#ff8c00;
                    margin-bottom:0.5rem;">System Summary</div>
        {summary_text}
    </div>
    """, unsafe_allow_html=True)

# ── Severity → priority mapping ───────────────────────────────────────────────
PRIORITY_MAP = {
    "critical": "P1 — Immediate",
    "high":     "P2 — High",
    "medium":   "P3 — Medium",
    "low":      "P4 — Low",
}

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# ── Stat chips ────────────────────────────────────────────────────────────────
SEV_COLOUR = {
    "critical": ("#ff4b6e", "rgba(255,75,110,0.18)",  "rgba(255,75,110,0.3)"),
    "high":     ("#ff9632", "rgba(255,150,50,0.18)",  "rgba(255,150,50,0.3)"),
    "medium":   ("#ffd232", "rgba(255,210,50,0.18)",  "rgba(255,210,50,0.3)"),
    "low":      ("#ff8c00", "rgba(255,140,0,0.12)",   "rgba(255,140,0,0.2)"),
}

def badge(text, fg, bg, border):
    return (
        f'<span style="display:inline-block; font-family:\'Space Mono\',monospace; '
        f'font-size:0.68rem; padding:2px 8px; border-radius:3px; '
        f'background:{bg}; color:{fg}; border:1px solid {border};">{text}</span>'
    )

counts = {}
for t in threats:
    sev = t.get("severity", "Low").lower()
    counts[sev] = counts.get(sev, 0) + 1

chip_html = ""
for sev in ["critical", "high", "medium", "low"]:
    if sev in counts:
        fg, bg, br = SEV_COLOUR[sev]
        chip_html += badge(f"{counts[sev]} {sev.capitalize()}", fg, bg, br) + "&nbsp;"

st.markdown(f"""
<div style="margin-bottom:1.4rem;">
    <span style="font-family:'Space Mono',monospace; font-size:0.72rem;
                 color:var(--text-muted); letter-spacing:0.1em; text-transform:uppercase;
                 margin-right:0.8rem;">{len(threats)} threat(s)</span>
    {chip_html}
</div>
""", unsafe_allow_html=True)

# ── Build DataFrame ───────────────────────────────────────────────────────────
rows = []
for t in threats:
    sev = t.get("severity", "Low")
    rows.append({
        "ID":          t.get("id", ""),
        "Category":    t.get("category", ""),
        "Threat":      t.get("title", ""),
        "Description": t.get("description", ""),
        "Mitigation":  t.get("mitigation", ""),
        "Severity":    sev,
        "Priority":    PRIORITY_MAP.get(sev.lower(), "P4 — Low"),
    })

df = pd.DataFrame(rows)

# Sort by severity
df["_sev_order"] = df["Severity"].str.lower().map(SEV_ORDER).fillna(99)
df = df.sort_values("_sev_order").drop(columns=["_sev_order"]).reset_index(drop=True)

# ── Render table ──────────────────────────────────────────────────────────────
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "ID":          st.column_config.TextColumn("ID",          width=70),
        "Category":    st.column_config.TextColumn("Category",    width=160),
        "Threat":      st.column_config.TextColumn("Threat",      width=200),
        "Description": st.column_config.TextColumn("Description", width=340),
        "Mitigation":  st.column_config.TextColumn("Mitigation",  width=300),
        "Severity":    st.column_config.TextColumn("Severity",    width=100),
        "Priority":    st.column_config.TextColumn("Priority",    width=130),
    },
    height=min(38 + len(df) * 55, 650),
)
