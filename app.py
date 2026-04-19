import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PatrimonIA · Simulador",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# ICON SYSTEM — Lucide (inline SVG, consistent family)
# ══════════════════════════════════════════════════════════════════════════════
# All icons share: stroke-width=1.75, stroke-linecap=round, stroke-linejoin=round
# 24×24 viewBox. Size/color controlled by CSS (currentColor + width/height).
ICONS = {
    "sparkle": '<path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M5.6 18.4L18.4 5.6"/>',
    "wallet": '<path d="M19 7H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M16 14h.01"/><path d="M3 9V7a2 2 0 0 1 2-2h11"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 0 0-16 0"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "trending_up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "percent": '<line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5Z"/>',
    "trending_down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "plus_circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
    "growth": '<path d="M3 3v18h18"/><path d="M7 14l4-4 4 4 5-5"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "bullseye": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/>',
    "piggy": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/>',
    "chart": '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/>',
    "down_tri": '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    "up_tri": '<path d="M12 19V5"/><path d="m5 12 7-7 7 7"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m6.08 9.5-3.5 1.6a1 1 0 0 0 0 1.81l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9a1 1 0 0 0 0-1.83l-3.5-1.59"/><path d="m6.08 14.5-3.5 1.6a1 1 0 0 0 0 1.81l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9a1 1 0 0 0 0-1.83l-3.5-1.59"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "play": '<polygon points="6 4 20 12 6 20 6 4"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "arrow_right": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    "coins": '<circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="m16.71 13.88.7.71-2.82 2.82"/>',
    "banknote": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
}

def icon(name: str, size: int = 16, cls: str = "") -> str:
    """Retorna SVG Lucide inline, herdando cor via currentColor."""
    body = ICONS.get(name, "")
    return (
        f'<svg class="licon {cls}" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</svg>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# CSS — Design system unified
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ─── DESIGN TOKENS ───────────────────────────────────────────────────────── */
:root {
    --bg:            #080C14;
    --bg-soft:       rgba(255,255,255,.025);
    --bg-softer:     rgba(255,255,255,.04);
    --border:        rgba(255,255,255,.07);
    --border-hover:  rgba(92,189,145,.22);
    --text:          #E8EDF5;
    --text-dim:      rgba(200,210,225,.55);
    --text-mute:     rgba(155,175,200,.5);
    --accent:        #5CBD91;
    --accent-soft:   rgba(92,189,145,.12);
    --warn:          #E8A87C;
    --warn-soft:     rgba(232,168,124,.12);

    --r-sm: 10px;
    --r-md: 14px;
    --r-lg: 20px;

    --pad-card: 1.35rem 1.45rem;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main { background: var(--bg) !important; }
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { right: 1rem !important; }

.block-container {
    padding: 0 2.5rem 5rem !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* Lucide icons base */
.licon {
    display: inline-block;
    vertical-align: -0.18em;
    flex-shrink: 0;
    color: currentColor;
}

/* ─── HERO with interactive spotlight ─────────────────────────────────────── */
.hero-wrap {
    position: relative;
    padding: 3.4rem 2rem 2.2rem;
    margin: 1rem 0 1.8rem;
    border-radius: var(--r-lg);
    border: 1px solid var(--border);
    background:
        radial-gradient(600px 300px at var(--mx,50%) var(--my,30%),
            rgba(92,189,145,.14) 0%,
            rgba(92,189,145,.05) 35%,
            transparent 70%),
        linear-gradient(180deg, rgba(92,189,145,.04) 0%, rgba(8,12,20,0) 80%);
    overflow: hidden;
    transition: border-color .6s;
}
.hero-wrap::before {
    /* grain layer */
    content:'';
    position:absolute; inset:0;
    background-image:
        radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,.04) 1px, transparent 0),
        radial-gradient(1px 1px at 70% 80%, rgba(255,255,255,.03) 1px, transparent 0),
        radial-gradient(1px 1px at 40% 60%, rgba(255,255,255,.03) 1px, transparent 0);
    background-size: 180px 180px, 220px 220px, 160px 160px;
    pointer-events: none;
    opacity:.7;
}
.hero-wrap::after {
    /* moving glow that follows cursor */
    content:'';
    position:absolute;
    top: var(--my, 50%);
    left: var(--mx, 50%);
    width: 420px; height: 420px;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle,
        rgba(92,189,145,.18) 0%,
        rgba(92,189,145,.06) 30%,
        transparent 65%);
    pointer-events: none;
    transition: opacity .4s;
    opacity: var(--hero-opacity, 0);
    filter: blur(8px);
    mix-blend-mode: screen;
}
.hero-wrap:hover { border-color: rgba(92,189,145,.18); }
.hero-wrap:hover::after { opacity: 1; }

.hero-content { position: relative; z-index: 2; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(92,189,145,.08);
    border: 1px solid rgba(92,189,145,.28);
    border-radius: 100px;
    padding: 5px 14px 5px 12px;
    font-size: 10.5px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1.3rem;
    font-weight: 600;
    backdrop-filter: blur(4px);
}
.hero-badge .licon { color: var(--accent); }

.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2rem, 3.8vw, 3.3rem);
    font-weight: 800;
    line-height: 1.06;
    letter-spacing: -.03em;
    color: #F0F4FA;
    margin: 0 0 .75rem;
}
.hero-title span {
    color: var(--accent);
    background: linear-gradient(120deg, #5CBD91 0%, #7FD9B0 50%, #5CBD91 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: .98rem;
    color: rgba(200,210,225,.55);
    font-weight: 300;
    max-width: 520px;
    margin: 0;
    line-height: 1.55;
}
.hero-meta {
    display: flex; gap: 1.5rem; flex-wrap: wrap;
    margin-top: 1.8rem; padding-top: 1.4rem;
    border-top: 1px solid rgba(255,255,255,.05);
}
.hero-meta-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 11.5px;
    color: rgba(175,195,215,.5);
    letter-spacing: .04em;
}
.hero-meta-item .licon { color: var(--accent); opacity: .7; }
.hero-meta-item strong {
    color: rgba(220,232,245,.85);
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
}

/* ─── SECTION LABEL ───────────────────────────────────────────────────────── */
.slabel {
    font-family: 'Syne', sans-serif;
    font-size: 10.5px;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: rgba(92,189,145,.65);
    margin: .4rem 0 .95rem;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
}
.slabel .licon { color: rgba(92,189,145,.55); }
.slabel::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(92,189,145,.15), transparent);
}

/* ─── INPUT PANEL ─────────────────────────────────────────────────────────── */
/* Native streamlit container with border — painted as ipanel */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > .ipanel-marker) {
    background: linear-gradient(180deg, rgba(255,255,255,.028), rgba(255,255,255,.015)) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    padding: 1.6rem 1.5rem !important;
}

.ipanel-section {
    padding: .2rem 0;
}
.ipanel-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.06), transparent);
    margin: 1.1rem -.3rem;
    border: none;
}

/* Input overrides */
[data-testid="stNumberInput"] input,
[data-testid="stNumberInput"] input:hover {
    background: rgba(255,255,255,.035) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: .55rem .8rem !important;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(92,189,145,.5) !important;
    box-shadow: 0 0 0 3px rgba(92,189,145,.1) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,.04) !important;
    border-color: rgba(255,255,255,.08) !important;
    color: rgba(200,215,235,.7) !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(92,189,145,.1) !important;
    color: var(--accent) !important;
}

label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: .08em !important;
    color: rgba(180,195,215,.62) !important;
    text-transform: uppercase !important;
    margin-bottom: .35rem !important;
}

/* Slider */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(92,189,145,.15) !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: linear-gradient(90deg, #5CBD91, #7FD9B0) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] ~ div {
    color: var(--accent) !important;
    font-weight: 600 !important;
}

/* ─── METRICS GRID ────────────────────────────────────────────────────────── */
.mgrid3 { display: grid; grid-template-columns: repeat(3,1fr); gap: .85rem; margin-bottom: 1.5rem; }
.mgrid2 { display: grid; grid-template-columns: repeat(2,1fr); gap: .85rem; margin-bottom: 1.5rem; }

@media (max-width: 880px) {
    .mgrid3 { grid-template-columns: repeat(2,1fr); }
    .mgrid2 { grid-template-columns: 1fr; }
}

.mcard {
    background: linear-gradient(180deg, rgba(255,255,255,.028), rgba(255,255,255,.012));
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: var(--pad-card);
    position: relative;
    overflow: hidden;
    transition: border-color .3s, transform .25s, background .3s;
    min-height: 118px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.mcard::before {
    content: '';
    position: absolute;
    top: 0; bottom: 0; left: 0;
    width: 2px;
    background: linear-gradient(180deg, transparent, var(--accent), transparent);
    opacity: 0;
    transition: opacity .3s;
}
.mcard:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
}
.mcard:hover::before { opacity: 1; }
.mcard.inf::before { background: linear-gradient(180deg, transparent, var(--warn), transparent); }
.mcard.inf:hover   { border-color: rgba(232,168,124,.22); }

.mcard-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: .8rem;
    margin-bottom: .7rem;
}
.mlabel {
    font-size: 10px;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: rgba(160,180,205,.55);
    font-weight: 500;
    line-height: 1.3;
    flex: 1;
}
.micon {
    color: rgba(92,189,145,.45);
    flex-shrink: 0;
    margin-top: -1px;
}
.mcard.inf .micon { color: rgba(232,168,124,.5); }

.mval {
    font-family: 'Syne', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #F0F4FA;
    letter-spacing: -.02em;
    line-height: 1.1;
}
.mval.g { color: var(--accent); }
.mval.w { color: var(--warn); }
.msub {
    font-size: 11px;
    color: rgba(135,158,185,.52);
    margin-top: .35rem;
    line-height: 1.4;
}

/* ─── INFLATION INFO BOX ──────────────────────────────────────────────────── */
.infbox {
    background: linear-gradient(180deg, rgba(232,168,124,.07), rgba(232,168,124,.03));
    border: 1px solid rgba(232,168,124,.2);
    border-radius: var(--r-md);
    padding: .95rem 1.1rem;
    margin: .8rem 0 .3rem;
    font-size: 11.5px;
    color: rgba(200,215,230,.65);
    line-height: 1.75;
}
.infbox-row {
    display: flex; align-items: center; gap: 9px;
    margin-bottom: .3rem;
}
.infbox-row:last-child { margin-bottom: 0; }
.infbox-row .licon { color: var(--warn); opacity: .85; }
.infbox strong {
    color: #F0D9C5;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
}

/* ─── MILESTONE BANNER ────────────────────────────────────────────────────── */
.msbanner {
    background: linear-gradient(135deg, rgba(92,189,145,.1), rgba(92,189,145,.02));
    border: 1px solid rgba(92,189,145,.28);
    border-radius: var(--r-md);
    padding: 1.25rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.msbanner::before {
    content:'';
    position:absolute; top:0; right:0;
    width: 260px; height: 100%;
    background: radial-gradient(ellipse at right, rgba(92,189,145,.1), transparent 70%);
    pointer-events:none;
}
.msbanner.miss {
    background: linear-gradient(135deg, rgba(232,168,124,.08), rgba(232,168,124,.02));
    border-color: rgba(232,168,124,.24);
}
.msbanner.miss::before {
    background: radial-gradient(ellipse at right, rgba(232,168,124,.08), transparent 70%);
}
.msicon-wrap {
    width: 44px; height: 44px;
    border-radius: 12px;
    background: rgba(92,189,145,.12);
    border: 1px solid rgba(92,189,145,.25);
    display: flex; align-items: center; justify-content: center;
    color: var(--accent);
    flex-shrink: 0;
}
.msbanner.miss .msicon-wrap {
    background: rgba(232,168,124,.1);
    border-color: rgba(232,168,124,.25);
    color: var(--warn);
}
.mstxt { position: relative; z-index: 1; }
.mstxt strong {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #F0F4FA;
    display: block;
    margin-bottom: 3px;
    letter-spacing: -.01em;
}
.mstxt span {
    font-size: 12px;
    color: rgba(175,195,215,.58);
    line-height: 1.5;
}

/* ─── CHART WRAPPER ───────────────────────────────────────────────────────── */
.chwrap {
    background: linear-gradient(180deg, rgba(255,255,255,.022), rgba(255,255,255,.008));
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: 1.3rem 1.2rem .8rem;
    margin-bottom: 1.5rem;
}

/* ─── TABS ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,.03) !important;
    border-radius: var(--r-sm) !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    letter-spacing: .02em !important;
    color: rgba(155,178,205,.65) !important;
    padding: .5rem 1.1rem !important;
    background: transparent !important;
    border: none !important;
    transition: all .2s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(200,220,240,.85) !important;
    background: rgba(255,255,255,.02) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(92,189,145,.14) !important;
    color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; margin-top: 1rem; }

/* ─── CUSTOM TABLE ────────────────────────────────────────────────────────── */
.ptable-wrap {
    background: linear-gradient(180deg, rgba(255,255,255,.022), rgba(255,255,255,.008));
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    overflow: hidden;
    margin-bottom: 1rem;
}
.ptable {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Sans', sans-serif;
    font-size: 12.5px;
}
.ptable thead th {
    background: rgba(255,255,255,.025);
    border-bottom: 1px solid var(--border);
    color: rgba(160,180,205,.6);
    font-weight: 500;
    font-size: 10px;
    letter-spacing: .14em;
    text-transform: uppercase;
    padding: .85rem 1rem;
    text-align: right;
    white-space: nowrap;
}
.ptable thead th:first-child,
.ptable thead th:nth-child(2),
.ptable thead th:nth-child(3) { text-align: left; }

.ptable tbody td {
    padding: .75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,.04);
    color: var(--text);
    text-align: right;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.ptable tbody td:first-child,
.ptable tbody td:nth-child(2),
.ptable tbody td:nth-child(3) { text-align: left; }

.ptable tbody tr { transition: background .2s; }
.ptable tbody tr:hover { background: rgba(92,189,145,.035); }
.ptable tbody tr:last-child td { border-bottom: none; }

.ptable .c-date {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: var(--accent);
    font-size: 11.5px;
    letter-spacing: .06em;
}
.ptable .c-period {
    color: rgba(220,230,245,.85);
    font-weight: 500;
}
.ptable .c-age {
    color: rgba(175,195,215,.55);
    font-size: 12px;
}
.ptable .c-pat {
    font-weight: 600;
    color: var(--accent);
}
.ptable .c-real {
    color: var(--warn);
    font-weight: 500;
}
.ptable .c-rend-main { color: var(--accent); font-weight: 500; }
.ptable .c-rend-sub {
    color: rgba(160,180,205,.45);
    font-size: 11px;
    margin-left: 6px;
}

/* ─── HELPER / LIVE SUMMARY ───────────────────────────────────────────────── */
.summary-card {
    background: linear-gradient(135deg, rgba(92,189,145,.08), rgba(92,189,145,.02));
    border: 1px solid rgba(92,189,145,.2);
    border-radius: var(--r-md);
    padding: 1rem 1.1rem;
    margin-top: .3rem;
}
.summary-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 4px 0;
    font-size: 12px;
}
.summary-row .label {
    color: rgba(175,195,215,.55);
    display: flex; align-items: center; gap: 8px;
}
.summary-row .label .licon { color: var(--accent); opacity: .7; }
.summary-row .val {
    color: #F0F4FA;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
    font-size: 12.5px;
}

/* ─── FOOTER ──────────────────────────────────────────────────────────────── */
.ftxt {
    text-align: center;
    font-size: 11px;
    color: rgba(120,145,170,.4);
    letter-spacing: .06em;
    padding-top: 3rem;
    line-height: 1.85;
}
.ftxt .sep { color: rgba(92,189,145,.35); margin: 0 .5rem; }

/* ─── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(92,189,145,.2);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(92,189,145,.35); }

/* Remove default streamlit gaps that create "empty holes" */
[data-testid="stVerticalBlock"] { gap: .5rem !important; }
.element-container:has(> .stMarkdown > div > [style*="display:none"]) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PURE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def fmt(v):
    av = abs(v)
    if av >= 1_000_000: return f"R$ {v/1_000_000:.2f}M"
    if av >= 1_000:     return f"R$ {v/1_000:.1f}K"
    return f"R$ {v:,.0f}"

def fmt_full(v):
    return "R$ " + f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def deflate(v, inf_aa, anos):
    return v / (1 + inf_aa / 100) ** anos

def simulate(saldo, anos, rent_aa, aporte0, tc_aa):
    tm    = (1 + rent_aa / 100) ** (1/12) - 1
    meses = int(anos * 12)
    pat   = saldo
    inv   = saldo
    ap    = aporte0
    pats, invs, aps = [pat], [inv], [ap]
    for m in range(1, meses + 1):
        if m % 12 == 1 and m > 1:
            ap *= (1 + tc_aa / 100)
        pat  = pat * (1 + tm) + ap
        inv += ap
        pats.append(pat); invs.append(inv); aps.append(ap)
    return pats, invs, aps

def scenarios(saldo, anos, rent, aporte, tc):
    return (
        simulate(saldo, anos, rent - 1.5, aporte * 0.85, tc),
        simulate(saldo, anos, rent,       aporte,        tc),
        simulate(saldo, anos, rent + 1.5, aporte * 1.15, tc),
    )

def find_million(pats):
    for i, p in enumerate(pats):
        if p >= 1_000_000:
            return i / 12
    return None

def apply_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), height=380,
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(family="DM Sans", size=11, color="rgba(175,198,220,.7)"),
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="", tickfont=dict(size=10, color="rgba(135,158,185,.55)", family="DM Sans"),
            gridcolor="rgba(255,255,255,.03)", zeroline=False, showline=False,
        ),
        yaxis=dict(
            title="", tickfont=dict(size=10, color="rgba(135,158,185,.55)", family="DM Sans"),
            gridcolor="rgba(255,255,255,.04)", zeroline=False, showline=False,
            tickformat=",.0f", tickprefix="R$ ",
        ),
        hoverlabel=dict(bgcolor="#111827", font_family="DM Sans", font_size=12,
                        bordercolor="rgba(92,189,145,.25)"),
    )

def date_labels(start: date, n_months: int):
    return [start + relativedelta(months=m) for m in range(n_months + 1)]

MESES_PT = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
def fmt_date(d: date) -> str:
    return f"{MESES_PT[d.month-1]}/{str(d.year)[2:]}"


# ══════════════════════════════════════════════════════════════════════════════
# HERO — interactive spotlight
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-wrap" id="hero">
  <div class="hero-content">
    <div class="hero-badge">{icon("sparkle", 12)} Simulador Patrimonial · v2.2</div>
    <h1 class="hero-title">Sua jornada rumo<br>à <span>independência financeira</span></h1>
    <p class="hero-sub">Projete, simule e visualize o crescimento do seu patrimônio com precisão e clareza.</p>
    <div class="hero-meta">
      <div class="hero-meta-item">{icon("layers", 14)} <strong>3 cenários</strong> simultâneos</div>
      <div class="hero-meta-item">{icon("flame", 14)} Projeção <strong>real</strong> com inflação</div>
      <div class="hero-meta-item">{icon("target", 14)} Milestones <strong>automáticos</strong></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Inject mouse-follow script (runs in parent document via hack).
# Streamlit sandboxes components, so we attach listener to parent via postMessage.
components.html("""
<script>
(function() {
    const doc = window.parent.document;
    let hero = null;
    let rafId = null;
    let targetX = 50, targetY = 30;
    let currentX = 50, currentY = 30;

    function findHero() {
        hero = doc.getElementById('hero');
        if (!hero) { setTimeout(findHero, 200); return; }
        attach();
    }

    function animate() {
        currentX += (targetX - currentX) * 0.12;
        currentY += (targetY - currentY) * 0.12;
        if (hero) {
            hero.style.setProperty('--mx', currentX + '%');
            hero.style.setProperty('--my', currentY + '%');
        }
        rafId = requestAnimationFrame(animate);
    }

    function attach() {
        hero.addEventListener('mousemove', (e) => {
            const r = hero.getBoundingClientRect();
            targetX = ((e.clientX - r.left) / r.width) * 100;
            targetY = ((e.clientY - r.top) / r.height) * 100;
            hero.style.setProperty('--hero-opacity', '1');
        });
        hero.addEventListener('mouseleave', () => {
            targetX = 50; targetY = 30;
            hero.style.setProperty('--hero-opacity', '0');
        });
        if (!rafId) animate();
    }

    findHero();
})();
</script>
""", height=0)


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
col_in, col_main = st.columns([1, 2.5], gap="large")

# ── INPUTS ────────────────────────────────────────────────────────────────────
with col_in:
    with st.container(border=True):
        # marker so CSS can target this specific container
        st.markdown('<div class="ipanel-marker" style="display:none"></div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="slabel">{icon("user", 12)} Patrimônio & Perfil</div>',
            unsafe_allow_html=True,
        )
        saldo_ini    = st.number_input("Saldo inicial (R$)", min_value=0.0, value=50_000.0, step=1_000.0, format="%.2f")
        idade        = st.number_input("Minha idade hoje",  min_value=18,  max_value=80,   value=30, step=1)
        anos_analise = st.slider("Período de análise (anos)", 1, 50, 20)

        st.markdown('<hr class="ipanel-divider">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="slabel">{icon("trending_up", 12)} Rentabilidade</div>',
            unsafe_allow_html=True,
        )
        rent_nom = st.number_input("Rentabilidade nominal a.a. (%)", min_value=0.0, max_value=60.0, value=12.0, step=0.5, format="%.1f")

        st.markdown('<hr class="ipanel-divider">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="slabel">{icon("flame", 12)} Inflação Prevista</div>',
            unsafe_allow_html=True,
        )
        inflacao = st.number_input("Inflação a.a. (%)", min_value=0.0, max_value=30.0, value=4.5, step=0.5, format="%.1f")

        rent_real = ((1 + rent_nom/100) / (1 + inflacao/100) - 1) * 100
        inf_acum  = (1 + inflacao/100)**anos_analise - 1

        st.markdown(f"""
        <div class="infbox">
          <div class="infbox-row">{icon("chart", 13)} Crescimento nominal: <strong>{rent_nom:.1f}% a.a.</strong></div>
          <div class="infbox-row">{icon("growth", 13)} Crescimento real: <strong>{rent_real:.2f}% a.a.</strong></div>
          <div class="infbox-row">{icon("trending_down", 13)} Inflação acumulada ({anos_analise} anos): <strong>{inf_acum*100:.0f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="ipanel-divider">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="slabel">{icon("plus_circle", 12)} Aportes</div>',
            unsafe_allow_html=True,
        )
        aporte_ini = st.number_input("Aporte mensal (R$)",              min_value=0.0, value=2_000.0, step=100.0, format="%.2f")
        tc_aporte  = st.number_input("Crescimento anual do aporte (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, format="%.1f")

        # Live summary (replaces fake "Simular" button)
        total_aportes_estim = aporte_ini * 12 * anos_analise  # aprox sem crescimento
        st.markdown(f"""
        <div class="summary-card">
          <div class="summary-row">
            <span class="label">{icon("calendar", 12)} Horizonte</span>
            <span class="val">{anos_analise} anos</span>
          </div>
          <div class="summary-row">
            <span class="label">{icon("user", 12)} Idade final</span>
            <span class="val">{idade + anos_analise} anos</span>
          </div>
          <div class="summary-row">
            <span class="label">{icon("banknote", 12)} Aporte inicial</span>
            <span class="val">{fmt(aporte_ini)}/mês</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── RESULTS ──────────────────────────────────────────────────────────────────
with col_main:
    today     = date.today()
    n_meses   = int(anos_analise * 12)
    datas     = date_labels(today, n_meses)
    x_labels  = [fmt_date(d) for d in datas]
    x_anos    = [m / 12 for m in range(n_meses + 1)]

    pess_r, real_r, otim_r = scenarios(saldo_ini, anos_analise, rent_nom, aporte_ini, tc_aporte)
    pat_p, inv_p, _        = pess_r
    pat_r, inv_r, ap_r     = real_r
    pat_o, inv_o, _        = otim_r

    pat_r_def = [deflate(p, inflacao, m/12) for m, p in enumerate(pat_r)]

    pf_r   = pat_r[-1];  pf_p = pat_p[-1];  pf_o = pat_o[-1]
    inv_f  = inv_r[-1]
    rend_f = pf_r - inv_f
    rend_p = rend_f / inv_f * 100 if inv_f else 0
    pf_def = pat_r_def[-1]
    mult   = pf_r / max(saldo_ini, 1)

    anos_1m      = find_million(pat_r)
    anos_1m_real = find_million(pat_r_def)
    anos_1m_otim = find_million(pat_o)

    # ── Milestone banner ──────────────────────────────────────────────────────
    if anos_1m is not None and anos_1m <= anos_analise:
        data_1m = today + relativedelta(months=int(anos_1m * 12))
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1m_r = today + relativedelta(months=int(anos_1m_real * 12))
            real_txt = f" · R$ 1M real em {fmt_date(data_1m_r)}"
        else:
            real_txt = " · Meta real além do período"
        st.markdown(f"""
        <div class="msbanner">
          <div class="msicon-wrap">{icon("trophy", 22)}</div>
          <div class="mstxt">
            <strong>Você alcança R$ 1.000.000 em {fmt_date(data_1m)} ({anos_1m:.1f} anos)</strong>
            <span>Aos {idade + anos_1m:.0f} anos · Cenário realista{real_txt}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if anos_1m_otim and anos_1m_otim <= anos_analise:
            data_1m_o = today + relativedelta(months=int(anos_1m_otim * 12))
            st.markdown(f"""
            <div class="msbanner miss">
              <div class="msicon-wrap">{icon("trending_up", 22)}</div>
              <div class="mstxt">
                <strong>R$ 1 milhão não atingido no cenário realista neste período</strong>
                <span>No cenário otimista chegaria em {fmt_date(data_1m_o)} ({anos_1m_otim:.1f} anos)</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msbanner miss">
              <div class="msicon-wrap">{icon("lightbulb", 22)}</div>
              <div class="mstxt">
                <strong>R$ 1 milhão não atingido nos {anos_analise} anos analisados</strong>
                <span>Amplie o período ou aumente o aporte mensal para atingir esta meta</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Métricas nominais ─────────────────────────────────────────────────────
    st.markdown(
        f'<div class="slabel">{icon("coins", 12)} Projeção Nominal · Valores Correntes</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div class="mgrid3">
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Patrimônio Final · Realista</div>
          <div class="micon">{icon("bullseye", 18)}</div>
        </div>
        <div>
          <div class="mval g">{fmt(pf_r)}</div>
          <div class="msub">{fmt_full(pf_r)}</div>
        </div>
      </div>
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Total Investido</div>
          <div class="micon">{icon("wallet", 18)}</div>
        </div>
        <div>
          <div class="mval">{fmt(inv_f)}</div>
          <div class="msub">{fmt_full(inv_f)}</div>
        </div>
      </div>
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Rendimento Acumulado</div>
          <div class="micon">{icon("trending_up", 18)}</div>
        </div>
        <div>
          <div class="mval g">{fmt(rend_f)}</div>
          <div class="msub">+{rend_p:.0f}% sobre o investido</div>
        </div>
      </div>
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Cenário Pessimista</div>
          <div class="micon">{icon("down_tri", 18)}</div>
        </div>
        <div>
          <div class="mval w">{fmt(pf_p)}</div>
          <div class="msub">Rentab. {rent_nom-1.5:.1f}% a.a.</div>
        </div>
      </div>
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Cenário Otimista</div>
          <div class="micon">{icon("up_tri", 18)}</div>
        </div>
        <div>
          <div class="mval g">{fmt(pf_o)}</div>
          <div class="msub">Rentab. {rent_nom+1.5:.1f}% a.a.</div>
        </div>
      </div>
      <div class="mcard">
        <div class="mcard-head">
          <div class="mlabel">Multiplicação Nominal</div>
          <div class="micon">{icon("percent", 18)}</div>
        </div>
        <div>
          <div class="mval">{mult:.1f}×</div>
          <div class="msub">do patrimônio inicial</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Métricas reais ────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="slabel">{icon("flame", 12)} Poder de Compra Real · Em R$ de Hoje</div>',
        unsafe_allow_html=True,
    )
    perda = pf_r - pf_def
    mult_r = pf_def / max(saldo_ini, 1)
    st.markdown(f"""
    <div class="mgrid2">
      <div class="mcard inf">
        <div class="mcard-head">
          <div class="mlabel">Patrimônio Real (R$ de hoje)</div>
          <div class="micon">{icon("flame", 18)}</div>
        </div>
        <div>
          <div class="mval w">{fmt(pf_def)}</div>
          <div class="msub">{fmt_full(pf_def)} · Cresc. real {rent_real:.2f}% a.a. · {mult_r:.1f}× o inicial</div>
        </div>
      </div>
      <div class="mcard inf">
        <div class="mcard-head">
          <div class="mlabel">Corrosão pela Inflação</div>
          <div class="micon">{icon("trending_down", 18)}</div>
        </div>
        <div>
          <div class="mval w">−{fmt(perda)}</div>
          <div class="msub">Diferença nominal vs. real · Inflação {inflacao:.1f}% a.a. × {anos_analise} anos</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["Projeção Nominal · 3 Cenários", "Nominal vs. Poder de Compra Real"])

    def build_ticks(datas, max_ticks=12):
        n = len(datas)
        step = max(1, n // max_ticks)
        idxs, lbls = [], []
        for i, d in enumerate(datas):
            if i == 0 or d.month == 1 or (step > 12 and i % step == 0):
                idxs.append(x_anos[i])
                lbls.append(fmt_date(d))
        return idxs, lbls

    tick_vals, tick_text = build_ticks(datas)
    def add_xticks(fig):
        fig.update_xaxes(tickmode="array", tickvals=tick_vals, ticktext=tick_text)

    # Tab 1
    with tab1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=x_anos + x_anos[::-1], y=pat_o + pat_p[::-1],
            fill="toself", fillcolor="rgba(92,189,145,.05)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=inv_r, name="Total Investido",
            mode="lines", line=dict(color="rgba(200,215,235,.2)", width=1.5, dash="dot"),
            customdata=x_labels,
            hovertemplate="<b>Investido</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_p, name="Pessimista",
            mode="lines", line=dict(color="#E8A87C", width=2, dash="dash"),
            customdata=x_labels,
            hovertemplate="<b>Pessimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_o, name="Otimista",
            mode="lines", line=dict(color="rgba(92,189,145,.55)", width=2),
            customdata=x_labels,
            hovertemplate="<b>Otimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_r, name="Realista",
            mode="lines", line=dict(color="#5CBD91", width=3),
            customdata=x_labels,
            hovertemplate="<b>Realista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        if anos_1m and anos_1m <= anos_analise:
            data_1m = today + relativedelta(months=int(anos_1m * 12))
            fig1.add_vline(x=anos_1m, line_width=1, line_dash="dot",
                           line_color="rgba(92,189,145,.4)",
                           annotation_text=fmt_date(data_1m),
                           annotation_position="top right",
                           annotation_font=dict(color="#5CBD91", size=11))
            fig1.add_hline(y=1_000_000, line_width=1, line_dash="dot",
                           line_color="rgba(92,189,145,.15)")
        apply_style(fig1); add_xticks(fig1)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2
    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=x_anos, y=pat_r, name="Nominal",
            mode="lines", line=dict(color="rgba(92,189,145,.3)", width=2, dash="dot"),
            customdata=x_labels,
            hovertemplate="<b>Nominal</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=x_anos, y=pat_r_def, name="Poder de Compra Real",
            mode="lines", line=dict(color="#E8A87C", width=3),
            fill="tozeroy", fillcolor="rgba(232,168,124,.04)",
            customdata=x_labels,
            hovertemplate="<b>Real (R$ hoje)</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig2.add_hline(y=1_000_000, line_width=1, line_dash="dot",
                       line_color="rgba(232,168,124,.18)")
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1mr = today + relativedelta(months=int(anos_1m_real * 12))
            fig2.add_vline(x=anos_1m_real, line_width=1, line_dash="dot",
                           line_color="rgba(232,168,124,.4)",
                           annotation_text=f"R$1M real · {fmt_date(data_1mr)}",
                           annotation_position="top right",
                           annotation_font=dict(color="#E8A87C", size=11))
        apply_style(fig2); add_xticks(fig2)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tabela customizada ───────────────────────────────────────────────────
    st.markdown(
        f'<div class="slabel">{icon("calendar", 12)} Evolução por Marco · Cenário Realista</div>',
        unsafe_allow_html=True,
    )

    checkpoints = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    checkpoints = sorted(set([c for c in checkpoints if c <= anos_analise] + [anos_analise]))

    rows_html = []
    for a in checkpoints:
        idx = int(a * 12)
        if idx >= len(pat_r):
            continue
        p   = pat_r[idx]
        inv = inv_r[idx]
        r   = p - inv
        rp  = r / inv * 100 if inv else 0
        pd_ = pat_r_def[idx]
        ap  = ap_r[idx]
        dt  = datas[idx]
        rows_html.append(f"""
        <tr>
          <td class="c-date">{fmt_date(dt).upper()}</td>
          <td class="c-period">{a} ano{'s' if a>1 else ''}</td>
          <td class="c-age">{int(idade+a)} anos</td>
          <td>{fmt(ap)}</td>
          <td>{fmt(inv)}</td>
          <td class="c-pat">{fmt(p)}</td>
          <td>
            <span class="c-rend-main">+{fmt(r)}</span>
            <span class="c-rend-sub">({rp:.0f}%)</span>
          </td>
          <td class="c-real">{fmt(pd_)}</td>
        </tr>
        """)

    table_html = f"""
    <div class="ptable-wrap">
      <table class="ptable">
        <thead>
          <tr>
            <th>Data</th>
            <th>Período</th>
            <th>Idade</th>
            <th>Aporte Mensal</th>
            <th>Total Investido</th>
            <th>Patrimônio Nom.</th>
            <th>Rendimento</th>
            <th>Valor Real (hoje)</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="ftxt">
  {icon("sparkle", 11)} PatrimonIA · Simulador Patrimonial
  <span class="sep">·</span> Projeções são estimativas e não garantem retornos futuros<br>
  Cenários com ±1,5pp na rentabilidade e ±15% no aporte
  <span class="sep">·</span> Valor real deflacionado pela inflação prevista
</div>
""", unsafe_allow_html=True)
