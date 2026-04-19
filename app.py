import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PatrimonIA · Simulador",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080C14 !important;
    color: #E8EDF5 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main { background: #080C14 !important; }
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 2.5rem 5rem !important; max-width: 1380px !important; margin: 0 auto !important; }

/* Hero */
.hero-wrap   { position: relative; padding: 3.2rem 0 2rem; margin-bottom: 1.8rem; }
.hero-glow   {
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 800px; height: 340px;
    background: radial-gradient(ellipse, rgba(92,189,145,.11) 0%, transparent 68%);
    pointer-events: none;
}
.hero-badge  {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(92,189,145,.08); border: 1px solid rgba(92,189,145,.25);
    border-radius: 100px; padding: 4px 14px; font-size: 11px;
    letter-spacing: .12em; text-transform: uppercase; color: #5CBD91;
    margin-bottom: 1.1rem; font-weight: 500;
}
.hero-title  {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(2rem, 3.8vw, 3.4rem); font-weight: 800;
    line-height: 1.06; letter-spacing: -.03em; color: #F0F4FA; margin-bottom: .7rem;
}
.hero-title span { color: #5CBD91; }
.hero-sub    { font-size: .95rem; color: rgba(200,210,225,.5); font-weight: 300; max-width: 460px; }
.hero-line   {
    width: 100%; height: 1px; margin-top: 2.2rem;
    background: linear-gradient(90deg, rgba(92,189,145,.4) 0%, rgba(92,189,145,.04) 50%, transparent 80%);
}

/* Section label */
.slabel {
    font-family: 'Syne', sans-serif; font-size: 10px; letter-spacing: .18em;
    text-transform: uppercase; color: rgba(92,189,145,.6); margin-bottom: .9rem;
    display: flex; align-items: center; gap: 8px;
}
.slabel::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,.05); }

/* Input panel */
.ipanel {
    background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.07);
    border-radius: 20px; padding: 1.7rem 1.5rem;
}

/* Input overrides */
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,.04) !important; border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important; color: #E8EDF5 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 14px !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(92,189,145,.5) !important;
    box-shadow: 0 0 0 3px rgba(92,189,145,.08) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important; font-size: 11.5px !important;
    font-weight: 500 !important; letter-spacing: .03em !important;
    color: rgba(180,195,215,.65) !important; text-transform: uppercase !important;
}

/* Metric grids */
.mgrid3 { display: grid; grid-template-columns: repeat(3,1fr); gap: .9rem; margin-bottom: 1.3rem; }
.mgrid2 { display: grid; grid-template-columns: repeat(2,1fr); gap: .9rem; margin-bottom: 1.3rem; }
.mcard  {
    background: rgba(255,255,255,.025); border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px; padding: 1.3rem 1.4rem; position: relative; overflow: hidden;
    transition: border-color .3s, transform .2s;
}
.mcard::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg,transparent,rgba(92,189,145,.6),transparent);
    opacity: 0; transition: opacity .3s;
}
.mcard:hover { border-color: rgba(92,189,145,.2); transform: translateY(-2px); }
.mcard:hover::before { opacity: 1; }
.mcard.inf::before { background: linear-gradient(90deg,transparent,rgba(232,168,124,.6),transparent); }
.mcard.inf:hover   { border-color: rgba(232,168,124,.2); }
.mlabel { font-size: 10px; letter-spacing: .14em; text-transform: uppercase; color: rgba(155,175,200,.5); margin-bottom: .55rem; font-weight: 500; }
.mval   { font-family: 'Syne',sans-serif; font-size: 1.5rem; font-weight: 700; color: #F0F4FA; letter-spacing: -.02em; line-height: 1.1; }
.mval.g { color: #5CBD91; }
.mval.w { color: #E8A87C; }
.msub   { font-size: 11px; color: rgba(135,158,185,.5); margin-top: .28rem; }
.micon  { position: absolute; top: 1.1rem; right: 1.1rem; font-size: 1rem; opacity: .3; }

/* Inflation info box */
.infbox {
    background: rgba(232,168,124,.06); border: 1px solid rgba(232,168,124,.18);
    border-radius: 12px; padding: .85rem 1.1rem; margin: .6rem 0;
    font-size: 12px; color: rgba(200,215,230,.6); line-height: 1.65;
}
.infbox strong { color: #E8A87C; font-family: 'Syne', sans-serif; }

/* Milestone banner */
.msbanner {
    background: linear-gradient(135deg,rgba(92,189,145,.08),rgba(92,189,145,.02));
    border: 1px solid rgba(92,189,145,.25); border-radius: 16px;
    padding: 1.2rem 1.5rem; display: flex; align-items: center; gap: 1rem; margin-bottom: 1.4rem;
}
.msbanner.miss { background: rgba(232,168,124,.06); border-color: rgba(232,168,124,.2); }
.msicon { font-size: 1.7rem; flex-shrink: 0; }
.mstxt strong { font-family: 'Syne',sans-serif; font-size: .98rem; font-weight: 700; color: #5CBD91; display: block; margin-bottom: 2px; }
.msbanner.miss .mstxt strong { color: #E8A87C; }
.mstxt span { font-size: 12px; color: rgba(175,195,215,.55); }

/* Chart wrap */
.chwrap {
    background: rgba(255,255,255,.02); border: 1px solid rgba(255,255,255,.06);
    border-radius: 20px; padding: 1.4rem; margin-bottom: 1.4rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,.03) !important; border-radius: 10px !important;
    padding: 3px !important; border: 1px solid rgba(255,255,255,.07) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; font-family: 'DM Sans',sans-serif !important;
    font-size: 12px !important; font-weight: 500 !important; letter-spacing: .03em !important;
    color: rgba(155,178,205,.6) !important; padding: .38rem 1rem !important;
    background: transparent !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: rgba(92,189,145,.15) !important; color: #5CBD91 !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; margin-top: 1rem; }

/* Button */
.stButton > button {
    background: linear-gradient(135deg,#5CBD91,#3DA876) !important;
    color: #080C14 !important; border: none !important; border-radius: 12px !important;
    font-family: 'Syne',sans-serif !important; font-weight: 700 !important;
    font-size: 13px !important; letter-spacing: .06em !important;
    padding: .65rem 1.4rem !important; width: 100% !important; text-transform: uppercase !important;
    box-shadow: 0 4px 20px rgba(92,189,145,.25) !important;
}
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }

hr { border: none; border-top: 1px solid rgba(255,255,255,.05) !important; margin: 1rem 0 !important; }
.ftxt { text-align: center; font-size: 11px; color: rgba(120,145,170,.3); letter-spacing: .07em; padding-top: 2.5rem; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: rgba(92,189,145,.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ── Pure functions ────────────────────────────────────────────────────────────
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
    """
    Simula mês a mês.
    O aporte cresce tc_aa% todo início de ano (todo ano, sem limite).
    Retorna listas de comprimento (anos*12 + 1), índice 0 = hoje.
    """
    tm    = (1 + rent_aa / 100) ** (1/12) - 1
    meses = int(anos * 12)
    pat   = saldo
    inv   = saldo
    ap    = aporte0

    pats  = [pat]
    invs  = [inv]
    aps   = [ap]

    for m in range(1, meses + 1):
        # Início de cada novo ano completo: cresce o aporte
        if m % 12 == 1 and m > 1:
            ap *= (1 + tc_aa / 100)
        pat  = pat * (1 + tm) + ap
        inv += ap
        pats.append(pat)
        invs.append(inv)
        aps.append(ap)

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
        margin=dict(l=10, r=10, t=10, b=10), height=370,
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
    """Gera lista de datas mensais a partir de start."""
    return [start + relativedelta(months=m) for m in range(n_months + 1)]

MESES_PT = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]

def fmt_date(d: date) -> str:
    return f"{MESES_PT[d.month-1]}/{str(d.year)[2:]}"


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-glow"></div>
  <div class="hero-badge">◈ Simulador Patrimonial · v2.1</div>
  <h1 class="hero-title">Sua jornada rumo<br>à <span>independência financeira</span></h1>
  <p class="hero-sub">Projete, simule e visualize o crescimento do seu patrimônio com precisão e clareza.</p>
  <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
col_in, col_main = st.columns([1, 2.5], gap="large")

# ── INPUTS ───────────────────────────────────────────────────────────────────
with col_in:
    st.markdown('<div class="ipanel">', unsafe_allow_html=True)

    st.markdown('<div class="slabel">Patrimônio & Perfil</div>', unsafe_allow_html=True)
    saldo_ini    = st.number_input("Saldo inicial (R$)", min_value=0.0, value=50_000.0, step=1_000.0, format="%.2f")
    idade        = st.number_input("Minha idade hoje",  min_value=18,  max_value=80,   value=30, step=1)
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
      📊 &nbsp;Crescimento <strong>nominal</strong>: {rent_nom:.1f}% a.a.<br>
      🌡 &nbsp;Crescimento <strong>real</strong> (líquido de inflação): <strong>{rent_real:.2f}% a.a.</strong><br>
      📉 &nbsp;Inflação acumulada em {anos_analise} anos: <strong>{inf_acum*100:.0f}%</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="slabel">Aportes</div>', unsafe_allow_html=True)
    aporte_ini = st.number_input("Aporte mensal (R$)",              min_value=0.0, value=2_000.0, step=100.0, format="%.2f")
    tc_aporte  = st.number_input("Crescimento anual do aporte (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.5, format="%.1f")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.button("◈ Simular Projeção")

    st.markdown('</div>', unsafe_allow_html=True)


# ── RESULTS ──────────────────────────────────────────────────────────────────
with col_main:

    today      = date.today()
    n_meses    = int(anos_analise * 12)
    datas      = date_labels(today, n_meses)           # list[date]
    x_labels   = [fmt_date(d) for d in datas]          # "abr/26", "mai/26" …
    x_anos     = [m / 12 for m in range(n_meses + 1)]  # eixo numérico

    pess_r, real_r, otim_r = scenarios(saldo_ini, anos_analise, rent_nom, aporte_ini, tc_aporte)
    pat_p, inv_p, _        = pess_r
    pat_r, inv_r, ap_r     = real_r
    pat_o, inv_o, _        = otim_r

    # Deflacionar
    pat_r_def = [deflate(p, inflacao, m/12) for m, p in enumerate(pat_r)]

    # Finais
    pf_r   = pat_r[-1];  pf_p = pat_p[-1];  pf_o = pat_o[-1]
    inv_f  = inv_r[-1]
    rend_f = pf_r - inv_f
    rend_p = rend_f / inv_f * 100 if inv_f else 0
    pf_def = pat_r_def[-1]
    mult   = pf_r / max(saldo_ini, 1)

    # Milestones
    anos_1m      = find_million(pat_r)
    anos_1m_real = find_million(pat_r_def)
    anos_1m_otim = find_million(pat_o)

    # ── Milestone banner ──────────────────────────────────────────────────────
    if anos_1m is not None and anos_1m <= anos_analise:
        data_1m = today + relativedelta(months=int(anos_1m * 12))
        real_txt = ""
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1m_r = today + relativedelta(months=int(anos_1m_real * 12))
            real_txt = f" · R$ 1M real em {fmt_date(data_1m_r)}"
        else:
            real_txt = " · Meta real além do período"
        st.markdown(f"""
        <div class="msbanner">
          <div class="msicon">🏆</div>
          <div class="mstxt">
            <strong>Você alcança R$ 1.000.000 em {fmt_date(data_1m)} ({anos_1m:.1f} anos)!</strong>
            <span>Aos {idade + anos_1m:.0f} anos · Cenário realista{real_txt}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if anos_1m_otim and anos_1m_otim <= anos_analise:
            data_1m_o = today + relativedelta(months=int(anos_1m_otim * 12))
            st.markdown(f"""
            <div class="msbanner miss">
              <div class="msicon">📈</div>
              <div class="mstxt">
                <strong>R$ 1 milhão não atingido no cenário realista neste período</strong>
                <span>No cenário otimista chegaria em {fmt_date(data_1m_o)} ({anos_1m_otim:.1f} anos)</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msbanner miss">
              <div class="msicon">💡</div>
              <div class="mstxt">
                <strong>R$ 1 milhão não atingido nos {anos_analise} anos analisados</strong>
                <span>Amplie o período ou aumente o aporte mensal para atingir esta meta</span>
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
        <div class="msub">Rentab. {rent_nom-1.5:.1f}% a.a.</div>
      </div>
      <div class="mcard">
        <div class="micon">△</div>
        <div class="mlabel">Cenário Otimista</div>
        <div class="mval g">{fmt(pf_o)}</div>
        <div class="msub">Rentab. {rent_nom+1.5:.1f}% a.a.</div>
      </div>
      <div class="mcard">
        <div class="micon">◷</div>
        <div class="mlabel">Multiplicação Nominal</div>
        <div class="mval">{mult:.1f}×</div>
        <div class="msub">do patrimônio inicial</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Métricas reais ────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Poder de Compra Real · Em R$ de Hoje</div>', unsafe_allow_html=True)
    perda = pf_r - pf_def
    mult_r = pf_def / max(saldo_ini, 1)
    st.markdown(f"""
    <div class="mgrid2">
      <div class="mcard inf">
        <div class="micon">🌡</div>
        <div class="mlabel">Patrimônio Real (R$ de hoje)</div>
        <div class="mval w">{fmt(pf_def)}</div>
        <div class="msub">{fmt_full(pf_def)} · Cresc. real {rent_real:.2f}% a.a. · {mult_r:.1f}× o inicial</div>
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
    tab1, tab2 = st.tabs(["📈  Projeção Nominal · 3 Cenários", "🔍  Nominal vs. Poder de Compra Real"])

    # Tick customizado: mostrar apenas Jan de cada ano + primeiro mês
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
        fig.update_xaxes(
            tickmode="array",
            tickvals=tick_vals,
            ticktext=tick_text,
        )

    # ── Tab 1: nominal ────────────────────────────────────────────────────────
    with tab1:
        fig1 = go.Figure()

        # Banda otim→pess
        fig1.add_trace(go.Scatter(
            x=x_anos + x_anos[::-1], y=pat_o + pat_p[::-1],
            fill="toself", fillcolor="rgba(92,189,145,.05)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip",
        ))
        # Investido
        fig1.add_trace(go.Scatter(
            x=x_anos, y=inv_r, name="Total Investido",
            mode="lines", line=dict(color="rgba(200,215,235,.2)", width=1.5, dash="dot"),
            customdata=x_labels,
            hovertemplate="<b>Investido</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        # Pessimista
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_p, name="Pessimista",
            mode="lines", line=dict(color="#E8A87C", width=2, dash="dash"),
            customdata=x_labels,
            hovertemplate="<b>Pessimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        # Otimista
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_o, name="Otimista",
            mode="lines", line=dict(color="rgba(92,189,145,.55)", width=2),
            customdata=x_labels,
            hovertemplate="<b>Otimista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))
        # Realista
        fig1.add_trace(go.Scatter(
            x=x_anos, y=pat_r, name="Realista",
            mode="lines", line=dict(color="#5CBD91", width=3),
            customdata=x_labels,
            hovertemplate="<b>Realista</b> %{customdata}: R$ %{y:,.0f}<extra></extra>",
        ))

        if anos_1m and anos_1m <= anos_analise:
            data_1m = today + relativedelta(months=int(anos_1m * 12))
            fig1.add_vline(x=anos_1m, line_width=1, line_dash="dot", line_color="rgba(92,189,145,.4)",
                annotation_text=fmt_date(data_1m), annotation_position="top right",
                annotation_font=dict(color="#5CBD91", size=11))
            fig1.add_hline(y=1_000_000, line_width=1, line_dash="dot", line_color="rgba(92,189,145,.15)")

        apply_style(fig1)
        add_xticks(fig1)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 2: real vs nominal ────────────────────────────────────────────────
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

        fig2.add_hline(y=1_000_000, line_width=1, line_dash="dot", line_color="rgba(232,168,124,.18)")
        if anos_1m_real and anos_1m_real <= anos_analise:
            data_1mr = today + relativedelta(months=int(anos_1m_real * 12))
            fig2.add_vline(x=anos_1m_real, line_width=1, line_dash="dot", line_color="rgba(232,168,124,.4)",
                annotation_text=f"R$1M real · {fmt_date(data_1mr)}", annotation_position="top right",
                annotation_font=dict(color="#E8A87C", size=11))

        apply_style(fig2)
        add_xticks(fig2)
        st.markdown('<div class="chwrap">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tabela anual ──────────────────────────────────────────────────────────
    st.markdown('<div class="slabel">Evolução por Marco · Cenário Realista</div>', unsafe_allow_html=True)

    checkpoints = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    checkpoints = sorted(set([c for c in checkpoints if c <= anos_analise] + [anos_analise]))

    rows = []
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
        rows.append({
            "Data":            fmt_date(dt).upper(),
            "Período":         f"{a} ano{'s' if a>1 else ''}",
            "Idade":           f"{int(idade+a)} anos",
            "Aporte Mensal":   fmt(ap),
            "Total Investido": fmt(inv),
            "Patrimônio":      fmt(p),
            "Rendimento":      f"+{fmt(r)}  ({rp:.0f}%)",
            "Valor Real":      fmt(pd_),
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        height=min(38 * len(rows) + 40, 540),
        column_config={
            "Data":            st.column_config.TextColumn("Data"),
            "Período":         st.column_config.TextColumn("Período"),
            "Idade":           st.column_config.TextColumn("Idade"),
            "Aporte Mensal":   st.column_config.TextColumn("Aporte Mensal"),
            "Total Investido": st.column_config.TextColumn("Total Investido"),
            "Patrimônio":      st.column_config.TextColumn("Patrimônio Nom."),
            "Rendimento":      st.column_config.TextColumn("Rendimento"),
            "Valor Real":      st.column_config.TextColumn("Valor Real (hoje)"),
        },
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ftxt">
  PatrimonIA · Simulador Patrimonial &nbsp;·&nbsp; Projeções são estimativas e não garantem retornos futuros<br>
  Cenários com ±1,5pp na rentabilidade e ±15% no aporte &nbsp;·&nbsp; Valor real deflacionado pela inflação prevista
</div>
""", unsafe_allow_html=True)
