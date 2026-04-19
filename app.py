import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PatrimonIA · Simulador",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# PURE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
MESES_PT = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

def fmt(v):
    av = abs(v)
    if av >= 1_000_000: return f"R$ {v/1_000_000:.2f}M"
    if av >= 1_000:     return f"R$ {v/1_000:.1f}K"
    return f"R$ {v:,.0f}"

def fmt_full(v):
    return "R$ " + f"{v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def fmt_date(d: date) -> str:
    return f"{MESES_PT[d.month-1]}/{str(d.year)[2:]}"

def deflate(v, inf_aa, anos):
    return v / (1 + inf_aa / 100) ** anos

def simulate(saldo, anos, rent_aa, aporte0, tc_aa):
    tm    = (1 + rent_aa / 100) ** (1/12) - 1
    meses = int(anos * 12)
    pat, inv, ap = saldo, saldo, aporte0
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
        if p >= 1_000_000: return i / 12
    return None

def date_labels(start: date, n_months: int):
    return [start + relativedelta(months=m) for m in range(n_months + 1)]

def apply_style(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), height=380,
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(family="monospace", size=11, color="rgba(170,190,220,.65)"),
            bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            title="",
            tickfont=dict(size=10, color="rgba(120,145,180,.45)", family="monospace"),
            gridcolor="rgba(255,255,255,.025)", zeroline=False, showline=False,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=10, color="rgba(120,145,180,.45)", family="monospace"),
            gridcolor="rgba(255,255,255,.03)", zeroline=False, showline=False,
            tickformat=",.0f", tickprefix="R$ ",
        ),
        hoverlabel=dict(
            bgcolor="#0E1117", font_family="monospace", font_size=12,
            bordercolor="rgba(0,229,153,.2)",
        ),
    )

def build_ticks(datas, x_anos):
    idxs, lbls = [], []
    for i, d in enumerate(datas):
        if i == 0 or d.month == 1:
            idxs.append(x_anos[i]); lbls.append(fmt_date(d))
    return idxs, lbls

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: #060810 !important;
    color: #DDE4F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"]  { background: transparent !important; border: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container {
    padding: 0 2.8rem 6rem !important;
    max-width: 1440px !important;
    margin: 0 auto !important;
}

/* ── Section labels ──────────────────────────────────────── */
.slabel {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px; letter-spacing: .22em; text-transform: uppercase;
    color: rgba(0,229,153,.5);
    display: flex; align-items: center; gap: 10px;
    margin-bottom: .9rem; margin-top: .15rem;
}
.slabel::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(255,255,255,.04);
}

/* ── Input panel ─────────────────────────────────────────── */
.ipanel {
    background: rgba(255,255,255,.018);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 20px; padding: 1.7rem 1.5rem;
    position: relative; overflow: hidden;
}
.ipanel::before {
    content: ''; position: absolute; top: 0; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,153,.35), transparent);
}

/* ── Number inputs ───────────────────────────────────────── */
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 10px !important;
    color: #DDE4F0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(0,229,153,.45) !important;
    box-shadow: 0 0 0 3px rgba(0,229,153,.06) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] button {
    background: rgba(255,255,255,.04) !important;
    border-color: rgba(255,255,255,.07) !important;
    color: rgba(200,215,235,.5) !important;
}

/* ── Slider ──────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #00E599 !important;
    border-color: #00E599 !important;
    box-shadow: 0 0 10px rgba(0,229,153,.4) !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: rgba(0,229,153,.2) !important;
}

/* ── Widget labels ───────────────────────────────────────── */
label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important; font-weight: 500 !important;
    letter-spacing: .04em !important; text-transform: uppercase !important;
    color: rgba(160,180,215,.45) !important;
}

/* ── Info box ────────────────────────────────────────────── */
.infbox {
    background: rgba(0,229,153,.04);
    border: 1px solid rgba(0,229,153,.12);
    border-radius: 12px; padding: .8rem 1rem; margin: .5rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px; color: rgba(180,210,200,.6); line-height: 1.75;
}
.infbox strong { color: #00E599; }

/* ── Metric grids ────────────────────────────────────────── */
.mgrid3 { display: grid; grid-template-columns: repeat(3,1fr); gap: .85rem; margin-bottom: 1.2rem; }
.mgrid2 { display: grid; grid-template-columns: repeat(2,1fr); gap: .85rem; margin-bottom: 1.2rem; }

.mcard {
    background: rgba(255,255,255,.018);
    border: 1px solid rgba(255,255,255,.055);
    border-radius: 16px; padding: 1.25rem 1.3rem;
    position: relative; overflow: hidden;
    transition: border-color .25s, transform .2s;
}
.mcard::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px;
    background: linear-gradient(90deg, transparent, rgba(0,229,153,.55), transparent);
    opacity: 0; transition: opacity .3s;
}
.mcard:hover { border-color: rgba(0,229,153,.18); transform: translateY(-2px); }
.mcard:hover::after { opacity: 1; }
.mcard.inf::after  { background: linear-gradient(90deg, transparent, rgba(255,168,100,.55), transparent); }
.mcard.inf:hover   { border-color: rgba(255,168,100,.18); }

.mlabel {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px; letter-spacing: .15em; text-transform: uppercase;
    color: rgba(140,165,200,.4); margin-bottom: .5rem; font-weight: 400;
}
.mval {
    font-family: 'Syne', sans-serif;
    font-size: 1.45rem; font-weight: 700;
    color: #DDE4F0; letter-spacing: -.025em; line-height: 1.1;
}
.mval.g { color: #00E599; }
.mval.w { color: #FFA864; }
.msub {
    font-size: 10.5px; color: rgba(130,155,185,.4); margin-top: .3rem;
    font-family: 'JetBrains Mono', monospace;
}
.micon { position: absolute; top: 1rem; right: 1.1rem; font-size: .95rem; opacity: .2; }

/* ── Milestone banner ────────────────────────────────────── */
.msbanner {
    background: rgba(0,229,153,.05);
    border: 1px solid rgba(0,229,153,.2);
    border-radius: 16px; padding: 1.1rem 1.4rem;
    display: flex; align-items: center; gap: 1rem; margin-bottom: 1.3rem;
    position: relative; overflow: hidden;
}
.msbanner::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: #00E599;
}
.msbanner.miss { background: rgba(255,168,100,.04); border-color: rgba(255,168,100,.18); }
.msbanner.miss::before { background: #FFA864; }
.msicon { font-size: 1.6rem; flex-shrink: 0; }
.mstxt strong {
    font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 700;
    color: #00E599; display: block; margin-bottom: 3px;
}
.msbanner.miss .mstxt strong { color: #FFA864; }
.mstxt span {
    font-size: 11.5px; color: rgba(165,185,215,.45);
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chart wrapper ───────────────────────────────────────── */
.chwrap {
    background: rgba(255,255,255,.015);
    border: 1px solid rgba(255,255,255,.055);
    border-radius: 18px; padding: 1.3rem; margin-bottom: 1.3rem;
}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,.025) !important;
    border-radius: 10px !important; padding: 3px !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important;
    letter-spacing: .03em !important;
    color: rgba(145,168,205,.55) !important;
    padding: .36rem 1rem !important;
    background: transparent !important; border: none !important;
    transition: color .2s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,229,153,.12) !important;
    color: #00E599 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; margin-top: 1rem; }

/* ── Button ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00E599, #00B876) !important;
    color: #060810 !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 12px !important;
    letter-spacing: .08em !important;
    padding: .7rem 1.4rem !important; width: 100% !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 20px rgba(0,229,153,.2) !important;
    transition: opacity .2s, transform .2s, box-shadow .2s !important;
}
.stButton > button:hover {
    opacity: .9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(0,229,153,.3) !important;
}

/* ── HR ──────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid rgba(255,255,255,.04) !important; margin: .9rem 0 !important; }

/* ── Footer ──────────────────────────────────────────────── */
.ftxt {
    text-align: center; font-size: 10.5px;
    color: rgba(110,135,165,.25); letter-spacing: .07em;
    padding-top: 2.5rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,229,153,.15); border-radius: 2px; }

/* ── Blink animation ─────────────────────────────────────── */
@keyframes pulse-dot {
  0%,100% { opacity:1; box-shadow: 0 0 8px #00E599; }
  50%      { opacity:.3; box-shadow: 0 0 3px #00E599; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE HEADER — Canvas partículas + repulsão do mouse + grid
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div id="hero-root" style="
    position:relative; width:100%; overflow:hidden;
    border-radius:0 0 28px 28px; margin-bottom:2rem;
    background:#060810;
">
  <!-- Canvas animado -->
  <canvas id="hero-canvas" style="
    position:absolute; inset:0; width:100%; height:100%;
    display:block; z-index:0; cursor:crosshair;
  "></canvas>

  <!-- Vignette / fade inferior -->
  <div style="
    position:absolute; inset:0; z-index:1; pointer-events:none;
    background:
      radial-gradient(ellipse 75% 55% at 50% 0%, rgba(0,229,153,.07) 0%, transparent 65%),
      linear-gradient(to bottom, transparent 55%, #060810 100%);
  "></div>

  <!-- Conteúdo -->
  <div style="position:relative; z-index:2; padding:3rem 2.8rem 2.6rem; display:flex; flex-direction:column; gap:.65rem;">

    <!-- Badge -->
    <div style="
      display:inline-flex; align-items:center; gap:8px;
      background:rgba(0,229,153,.07); border:1px solid rgba(0,229,153,.2);
      border-radius:100px; padding:4px 14px; width:fit-content;
      font-family:'JetBrains Mono',monospace; font-size:10px;
      letter-spacing:.18em; text-transform:uppercase; color:#00E599;
    ">
      <span id="status-dot" style="
        width:6px; height:6px; border-radius:50%; background:#00E599;
        animation:pulse-dot 2s ease-in-out infinite; display:inline-block;
      "></span>
      PatrimonIA &nbsp;·&nbsp; Simulador Patrimonial v3.0
    </div>

    <!-- Título -->
    <h1 style="
      font-family:'Syne',sans-serif;
      font-size:clamp(1.9rem,3.8vw,3.5rem); font-weight:800;
      line-height:1.05; letter-spacing:-.035em;
      color:#EDF2FF; margin:0;
    ">
      Projete sua <span style="color:#00E599;">independência</span><br>financeira com precisão
    </h1>

    <!-- Subtítulo -->
    <p style="
      font-size:.9rem; color:rgba(180,200,230,.38);
      font-weight:300; max-width:460px; margin:0;
      font-family:'DM Sans',sans-serif; line-height:1.65;
    ">
      Simule cenários realistas, pessimistas e otimistas.<br>
      Visualize o impacto real da inflação no seu patrimônio.
    </p>

    <!-- Stats rápidos -->
    <div style="display:flex; gap:2rem; margin-top:.6rem; flex-wrap:wrap; align-items:center;">
      <div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.18em;
          text-transform:uppercase;color:rgba(0,229,153,.4);margin-bottom:3px;">Cenários</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#EDF2FF;">3 Projeções</div>
      </div>
      <div style="width:1px;height:36px;background:rgba(255,255,255,.07);"></div>
      <div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.18em;
          text-transform:uppercase;color:rgba(0,229,153,.4);margin-bottom:3px;">Horizonte</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#EDF2FF;">Até 50 anos</div>
      </div>
      <div style="width:1px;height:36px;background:rgba(255,255,255,.07);"></div>
      <div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:.18em;
          text-transform:uppercase;color:rgba(0,229,153,.4);margin-bottom:3px;">Ajuste</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:700;color:#EDF2FF;">Inflação Real</div>
      </div>
    </div>
  </div>

  <!-- Linha separadora -->
  <div style="
    position:relative; z-index:2; height:1px; margin:0 2.8rem;
    background:linear-gradient(90deg,rgba(0,229,153,.45) 0%,rgba(0,229,153,.06) 50%,transparent 80%);
  "></div>
  <div style="height:2rem;"></div>
</div>

<script>
(function(){
  const PARTICLE_COUNT = 85;
  const GRID_COLS      = 32;
  const GRID_ROWS      = 12;
  const CONNECT_DIST   = 110;
  const REPEL_R        = 140;
  const REPEL_STR      = 0.4;
  const BASE_SPEED     = 0.32;
  const ACCENT         = [0, 229, 153];
  const DIM            = [25, 50, 80];

  const root   = document.getElementById('hero-root');
  const canvas = document.getElementById('hero-canvas');
  const ctx    = canvas.getContext('2d');

  function resize(){
    const r = root.getBoundingClientRect();
    canvas.width  = r.width;
    canvas.height = r.height;
    rebuildGrid();
  }

  let mx = -9999, my = -9999;

  canvas.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    mx = e.clientX - r.left;
    my = e.clientY - r.top;
  });
  canvas.addEventListener('mouseleave', () => { mx = -9999; my = -9999; });

  /* ── Grid ── */
  let gridPts = [];
  function rebuildGrid(){
    gridPts = [];
    for(let c = 0; c < GRID_COLS; c++){
      for(let r = 0; r < GRID_ROWS; r++){
        const bx = (c / (GRID_COLS-1)) * canvas.width;
        const by = (r / (GRID_ROWS-1)) * canvas.height;
        gridPts.push({ bx, by, x: bx, y: by });
      }
    }
  }

  /* ── Particles ── */
  function makeParticles(){
    return Array.from({length: PARTICLE_COUNT}, () => {
      const a = Math.random() * Math.PI * 2;
      return {
        x:  Math.random() * canvas.width,
        y:  Math.random() * canvas.height,
        vx: Math.cos(a) * BASE_SPEED,
        vy: Math.sin(a) * BASE_SPEED,
        r:  Math.random() * 1.6 + 0.5,
        alpha: Math.random() * 0.35 + 0.1,
      };
    });
  }

  resize();
  const particles = makeParticles();
  window.addEventListener('resize', resize);

  function lerp(a, b, t){ return a + (b-a)*t; }
  function dist(ax,ay,bx,by){ return Math.sqrt((ax-bx)**2+(ay-by)**2); }

  function draw(){
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    /* ── Grid dots with mouse repulsion ── */
    for(const g of gridPts){
      const d = dist(g.x, g.y, mx, my);
      if(d < REPEL_R && d > 0){
        const f = (1 - d/REPEL_R) * REPEL_STR * 16;
        g.x += ((g.x-mx)/d) * f;
        g.y += ((g.y-my)/d) * f;
      }
      g.x = lerp(g.x, g.bx, 0.08);
      g.y = lerp(g.y, g.by, 0.08);

      const prox = Math.max(0, 1 - dist(g.x,g.y,mx,my)/REPEL_R);
      const a    = 0.055 + prox * 0.38;
      const sz   = 0.75 + prox * 1.6;
      ctx.beginPath();
      ctx.arc(g.x, g.y, sz, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${lerp(DIM[0],ACCENT[0],prox)},${lerp(DIM[1],ACCENT[1],prox)},${lerp(DIM[2],ACCENT[2],prox)},${a})`;
      ctx.fill();
    }

    /* ── Floating particles ── */
    for(const p of particles){
      const d = dist(p.x, p.y, mx, my);
      if(d < REPEL_R*1.4 && d > 0){
        const f = (1 - d/(REPEL_R*1.4)) * REPEL_STR;
        p.vx += ((p.x-mx)/d)*f;
        p.vy += ((p.y-my)/d)*f;
      }
      p.vx *= 0.975; p.vy *= 0.975;
      const spd = Math.sqrt(p.vx*p.vx + p.vy*p.vy);
      if(spd > BASE_SPEED*3){ p.vx=(p.vx/spd)*BASE_SPEED*3; p.vy=(p.vy/spd)*BASE_SPEED*3; }
      if(spd < BASE_SPEED*0.3 && spd>0){ p.vx+=(p.vx/spd)*0.02; p.vy+=(p.vy/spd)*0.02; }
      p.x += p.vx; p.y += p.vy;
      if(p.x < -10) p.x = W+10;
      if(p.x > W+10) p.x = -10;
      if(p.y < -10) p.y = H+10;
      if(p.y > H+10) p.y = -10;

      const prox = Math.max(0, 1 - dist(p.x,p.y,mx,my)/(REPEL_R*1.4));
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r + prox*1.8, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${lerp(DIM[0],ACCENT[0],prox)},${lerp(DIM[1],ACCENT[1],prox)},${lerp(DIM[2],ACCENT[2],prox)},${p.alpha + prox*0.5})`;
      ctx.fill();
    }

    /* ── Connections between nearby particles ── */
    for(let i = 0; i < particles.length; i++){
      for(let j = i+1; j < particles.length; j++){
        const d = dist(particles[i].x,particles[i].y,particles[j].x,particles[j].y);
        if(d < CONNECT_DIST){
          const mi   = dist(particles[i].x,particles[i].y,mx,my);
          const mj   = dist(particles[j].x,particles[j].y,mx,my);
          const prox = Math.max(0, 1 - Math.min(mi,mj)/(REPEL_R*1.6));
          const a    = (1 - d/CONNECT_DIST) * (0.035 + prox*0.28);
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(${lerp(DIM[0],ACCENT[0],prox)},${lerp(DIM[1],ACCENT[1],prox)},${lerp(DIM[2],ACCENT[2],prox)},${a})`;
          ctx.lineWidth = 0.55 + prox * 1.1;
          ctx.stroke();
        }
      }
    }

    /* ── Cursor glow halo ── */
    if(mx > 0 && mx < W && my > 0 && my < H){
      const g = ctx.createRadialGradient(mx, my, 0, mx, my, REPEL_R);
      g.addColorStop(0,   'rgba(0,229,153,.1)');
      g.addColorStop(0.4, 'rgba(0,229,153,.04)');
      g.addColorStop(1,   'rgba(0,229,153,0)');
      ctx.beginPath();
      ctx.arc(mx, my, REPEL_R, 0, Math.PI*2);
      ctx.fillStyle = g;
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }

  draw();
})();
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
col_in, col_main = st.columns([1, 2.6], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────────────────────────────────────
with col_in:
    st.markdown('<div class="ipanel">', unsafe_allow_html=True)

    st.markdown('<div class="slabel">Patrimônio & Perfil</div>', unsafe_allow_html=True)
    saldo_ini    = st.number_input("Saldo inicial (R$)",  min_value=0.0,  value=50_000.0, step=1_000.0, format="%.2f")
    idade        = st.number_input("Minha idade hoje",    min_value=18,   max_value=80,   value=30,      step=1)
    anos_analise = st.slider("Período de análise (anos)", 1, 50, 20)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="slabel">Rentabilidade</div>', unsafe_allow_html=True)
    rent_nom = st.number_input("Rentabilidade nominal a.a. (%)", min_value=0.0, max_value=60.0, value=12.0, step=0.5, format="%.1f")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="slabel">Inflação Prevista</div>', unsafe_allow_html=True)
    inflacao = st.number_input("Inflação a.a. (%)", min_value=0.0, max_value=30.0, value=4.5, step=0.5, format="%.1f")

    rent_real = ((1 + rent_nom/100) / (1 + inflacao/100) - 1) * 100
    inf_acum  = (1 + inflacao/100)**anos_analise - 1

    st.markdown(f"""
    <div class="infbox">
      › Nominal: <strong>{rent_nom:.1f}% a.a.</strong><br>
      › Real líquido de inflação: <strong>{rent_real:.2f}% a.a.</strong><br>
      › Inflação acumulada ({anos_analise}a): <strong>{inf_acum*100:.0f}%</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="slabel">Aportes</div>', unsafe_allow_html=True)
    aporte_ini = st.number_input("Aporte mensal (R$)",              min_value=0.0, value=2_000.0, step=100.0, format="%.2f")
    tc_aporte  = st.number_input("Crescimento anual do aporte (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, format="%.1f")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.button("◈  Simular Projeção")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
with col_main:
    today    = date.today()
    n_meses  = int(anos_analise * 12)
    datas    = date_labels(today, n_meses)
    x_labels = [fmt_date(d) for d in datas]
    x_anos   = [m / 12 for m in range(n_meses + 1)]

    pess_r, real_r, otim_r = scenarios(saldo_ini, anos_analise, rent_nom, aporte_ini, tc_aporte)
    pat_p, inv_p, _        = pess_r
    pat_r, inv_r, ap_r     = real_r
    pat_o, inv_o, _        = otim_r

    pat_r_def = [deflate(p, inflacao, m/12) for m, p in enumerate(pat_r)]

    pf_r  = pat_r[-1];  pf_p = pat_p[-1];  pf_o = pat_o[-1]
    inv_f = inv_r[-1];  rend_f = pf_r - inv_f
    rend_p = rend_f / inv_f * 100 if inv_f else 0
    pf_def = pat_r_def[-1]
    mult   = pf_r  / max(saldo_ini, 1)
    mult_r = pf_def / max(saldo_ini, 1)
    perda  = pf_r - pf_def

    anos_1m      = find_million(pat_r)
    anos_1m_real = find_million(pat_r_def)
    anos_1m_otim = find_million(pat_o)

    # ── Milestone ────────────────────────────────────────────────────────────
    if anos_1m is not None and anos_1m <= anos_analise:
        data_1m  = today + relativedelta(months=int(anos_1m * 12))
        real_txt = ""
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1m_r = today + relativedelta(months=int(anos_1m_real * 12))
            real_txt  = f" · R$ 1M real em {fmt_date(data_1m_r)}"
        else:
            real_txt = " · Meta real além do período"
        st.markdown(f"""
        <div class="msbanner">
          <div class="msicon">🏆</div>
          <div class="mstxt">
            <strong>R$ 1.000.000 atingido em {fmt_date(data_1m)} — {anos_1m:.1f} anos</strong>
            <span>Aos {idade + anos_1m:.0f} anos · Cenário realista{real_txt}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    elif anos_1m_otim and anos_1m_otim <= anos_analise:
        data_1m_o = today + relativedelta(months=int(anos_1m_otim * 12))
        st.markdown(f"""
        <div class="msbanner miss">
          <div class="msicon">📈</div>
          <div class="mstxt">
            <strong>R$ 1M não atingido no cenário realista neste período</strong>
            <span>Cenário otimista chegaria em {fmt_date(data_1m_o)} ({anos_1m_otim:.1f} anos)</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msbanner miss">
          <div class="msicon">💡</div>
          <div class="mstxt">
            <strong>R$ 1 milhão não atingido em {anos_analise} anos</strong>
            <span>Amplie o período ou aumente o aporte para atingir esta meta</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Métricas nominais ─────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Projeção Nominal · Valores Correntes</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mgrid3">
      <div class="mcard">
        <div class="micon">◎</div>
        <div class="mlabel">Patrimônio Final · Realista</div>
        <div class="mval g">{fmt(pf_r)}</div>
        <div class="msub">{fmt_full(pf_r)}</div>
      </div>
      <div class="mcard">
        <div class="micon">◉</div>
        <div class="mlabel">Total Investido</div>
        <div class="mval">{fmt(inv_f)}</div>
        <div class="msub">{fmt_full(inv_f)}</div>
      </div>
      <div class="mcard">
        <div class="micon">◈</div>
        <div class="mlabel">Rendimento Acumulado</div>
        <div class="mval g">{fmt(rend_f)}</div>
        <div class="msub">+{rend_p:.0f}% sobre o investido</div>
      </div>
      <div class="mcard">
        <div class="micon">▽</div>
        <div class="mlabel">Cenário Pessimista</div>
        <div class="mval w">{fmt(pf_p)}</div>
        <div class="msub">Rent. {rent_nom-1.5:.1f}% a.a.</div>
      </div>
      <div class="mcard">
        <div class="micon">△</div>
        <div class="mlabel">Cenário Otimista</div>
        <div class="mval g">{fmt(pf_o)}</div>
        <div class="msub">Rent. {rent_nom+1.5:.1f}% a.a.</div>
      </div>
      <div class="mcard">
        <div class="micon">×</div>
        <div class="mlabel">Multiplicação Nominal</div>
        <div class="mval">{mult:.1f}×</div>
        <div class="msub">do patrimônio inicial</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Métricas reais ────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Poder de Compra Real · Em R$ de Hoje</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mgrid2">
      <div class="mcard inf">
        <div class="micon">🌡</div>
        <div class="mlabel">Patrimônio Real (R$ de hoje)</div>
        <div class="mval w">{fmt(pf_def)}</div>
        <div class="msub">{fmt_full(pf_def)} · {mult_r:.1f}× o inicial · Cresc. real {rent_real:.2f}% a.a.</div>
      </div>
      <div class="mcard inf">
        <div class="micon">📉</div>
        <div class="mlabel">Corrosão pela Inflação</div>
        <div class="mval w">−{fmt(perda)}</div>
        <div class="msub">Diferença nominal vs. real · Inflação {inflacao:.1f}% a.a. × {anos_analise} anos</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    tick_vals, tick_text = build_ticks(datas, x_anos)

    def add_xticks(fig):
        fig.update_xaxes(tickmode="array", tickvals=tick_vals, ticktext=tick_text)

    tab1, tab2 = st.tabs([
        "  📈  Projeção Nominal · 3 Cenários  ",
        "  🔍  Nominal vs. Poder de Compra Real  ",
    ])

    with tab1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=x_anos + x_anos[::-1], y=pat_o + pat_p[::-1],
            fill="toself", fillcolor="rgba(0,229,153,.04)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=inv_r, name="Total Investido",
            mode="lines", line=dict(color="rgba(180,200,235,.18)", width=1.5, dash="dot"),
            customdata=x_labels,
            hovertemplate="<b>Investido</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_p, name="Pessimista",
            mode="lines", line=dict(color="#FFA864", width=2, dash="dash"),
            customdata=x_labels,
            hovertemplate="<b>Pessimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_o, name="Otimista",
            mode="lines", line=dict(color="rgba(0,229,153,.45)", width=2),
            customdata=x_labels,
            hovertemplate="<b>Otimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_r, name="Realista",
            mode="lines", line=dict(color="#00E599", width=3),
            customdata=x_labels,
            hovertemplate="<b>Realista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        if anos_1m and anos_1m <= anos_analise:
            data_1m = today + relativedelta(months=int(anos_1m * 12))
            fig1.add_vline(x=anos_1m, line_width=1, line_dash="dot",
                           line_color="rgba(0,229,153,.35)",
                           annotation_text=fmt_date(data_1m),
                           annotation_position="top right",
                           annotation_font=dict(color="#00E599", size=11))
            fig1.add_hline(y=1_000_000, line_width=1, line_dash="dot",
                           line_color="rgba(0,229,153,.12)")
        apply_style(fig1); add_xticks(fig1)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=x_anos, y=pat_r, name="Nominal",
            mode="lines", line=dict(color="rgba(0,229,153,.28)", width=2, dash="dot"),
            customdata=x_labels,
            hovertemplate="<b>Nominal</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=x_anos, y=pat_r_def, name="Poder de Compra Real",
            mode="lines", line=dict(color="#FFA864", width=3),
            fill="tozeroy", fillcolor="rgba(255,168,100,.04)",
            customdata=x_labels,
            hovertemplate="<b>Real (R$ hoje)</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        fig2.add_hline(y=1_000_000, line_width=1, line_dash="dot",
                       line_color="rgba(255,168,100,.15)")
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1mr = today + relativedelta(months=int(anos_1m_real * 12))
            fig2.add_vline(x=anos_1m_real, line_width=1, line_dash="dot",
                           line_color="rgba(255,168,100,.4)",
                           annotation_text=f"R$1M real · {fmt_date(data_1mr)}",
                           annotation_position="top right",
                           annotation_font=dict(color="#FFA864", size=11))
        apply_style(fig2); add_xticks(fig2)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tabela de evolução ────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Evolução por Marco · Cenário Realista</div>', unsafe_allow_html=True)

    checkpoints = sorted(set(
        [c for c in [1,2,3,5,7,10,15,20,25,30,35,40,45,50] if c <= anos_analise]
        + [anos_analise]
    ))
    rows = []
    for a in checkpoints:
        idx = int(a * 12)
        if idx >= len(pat_r): continue
        p   = pat_r[idx];  inv = inv_r[idx]
        r   = p - inv;     rp  = r / inv * 100 if inv else 0
        rows.append({
            "Período":         f"{a} ano{'s' if a>1 else ''}",
            "Idade":           f"{int(idade+a)} anos",
            "Aporte Mensal":   fmt(ap_r[idx]),
            "Total Investido": fmt(inv),
            "Patrimônio":      fmt(p),
            "Rendimento":      f"+{fmt(r)} ({rp:.0f}%)",
            "Valor Real":      fmt(pat_r_def[idx]),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        height=min(38 * len(rows) + 40, 520),
        column_config={
            "Período":         st.column_config.TextColumn("Período"),
            "Idade":           st.column_config.TextColumn("Idade"),
            "Aporte Mensal":   st.column_config.TextColumn("Aporte Mensal"),
            "Total Investido": st.column_config.TextColumn("Total Investido"),
            "Patrimônio":      st.column_config.TextColumn("Patrimônio Nom."),
            "Rendimento":      st.column_config.TextColumn("Rendimento"),
            "Valor Real":      st.column_config.TextColumn("Valor Real (hoje)"),
        },
    )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ftxt">
  PatrimonIA · Simulador Patrimonial &nbsp;·&nbsp;
  Projeções são estimativas e não garantem retornos futuros<br>
  Cenários ±1,5pp na rentabilidade e ±15% no aporte &nbsp;·&nbsp;
  Valor real deflacionado pela inflação prevista
</div>
""", unsafe_allow_html=True)
