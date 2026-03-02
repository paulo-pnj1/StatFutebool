import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fpdf import FPDF
import time

load_dotenv()

st.set_page_config(
    page_title="Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #f5f4f0;
    color: #1a1a1a;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"],
[data-testid="stStatusWidget"],
.stActionButton,
div[data-testid="stDecoration"] { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── NAV ── */
.nav-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2.5rem;
    background: #fff;
    border-bottom: 1px solid #e8e6e0;
}
.nav-logo {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.nav-logo span { color: #2d6a4f; }
.nav-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    color: #888;
}
.dot {
    width: 7px; height: 7px; border-radius: 50%; display: inline-block;
}
.dot-on  { background: #52b788; }
.dot-off { background: #e07a5f; }
.dot-warn{ background: #f2c94c; }

/* ── TABS ── */
.stButton button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    padding: 0.5rem 1rem !important;
    border: 1px solid #e8e6e0 !important;
}
.stButton button[kind="primary"] {
    background: #1a1a1a !important;
    color: #fff !important;
    border-color: #1a1a1a !important;
}
.stButton button[kind="secondary"] {
    background: #fff !important;
    color: #555 !important;
}
.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

/* ── CONTENT WRAPPER ── */
.content {
    padding: 2rem 2.5rem;
    max-width: 1100px;
    margin: 0 auto;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 0.75rem;
}

/* ── MATCH CARD ── */
.match-card {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: all 0.15s ease;
    cursor: pointer;
}
.match-card:hover {
    border-color: #2d6a4f;
    box-shadow: 0 2px 12px rgba(45,106,79,0.1);
}
.match-card.active {
    border-color: #2d6a4f;
    background: #f0faf5;
}
.match-teams {
    font-weight: 600;
    font-size: 0.95rem;
    color: #1a1a1a;
    margin-bottom: 0.35rem;
}
.match-meta {
    font-size: 0.78rem;
    color: #999;
    font-family: 'DM Mono', monospace;
}

/* ── ANALYSIS CARD ── */
.analysis-wrap {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}
.analysis-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.analysis-title .badge {
    font-size: 0.7rem;
    font-weight: 500;
    background: #e8f5ee;
    color: #2d6a4f;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
}

/* ── PROB ROW ── */
.prob-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.9rem;
}
.prob-label {
    width: 110px;
    font-size: 0.85rem;
    color: #555;
    flex-shrink: 0;
}
.prob-track {
    flex: 1;
    height: 6px;
    background: #f0ede8;
    border-radius: 99px;
    overflow: hidden;
}
.prob-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s ease;
}
.fill-hi  { background: #52b788; }
.fill-mid { background: #f2c94c; }
.fill-lo  { background: #e07a5f; }
.prob-val {
    width: 42px;
    text-align: right;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #1a1a1a;
}
.prob-odd {
    width: 60px;
    text-align: right;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #999;
}

/* ── METRIC CHIPS ── */
.chips {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.chip {
    background: #f5f4f0;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    text-align: center;
    min-width: 90px;
}
.chip-val {
    font-size: 1.4rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    color: #1a1a1a;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.chip-lbl {
    font-size: 0.7rem;
    color: #999;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── PROFILE CARD ── */
.profile-card {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 12px;
    padding: 1.25rem;
}
.profile-name {
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 1rem;
    color: #1a1a1a;
}
.profile-style {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.style-off { background: #fff0ec; color: #e07a5f; }
.style-def { background: #eef4ff; color: #4a86e8; }
.style-eq  { background: #f5f4f0; color: #888; }

/* ── HISTORY ── */
.hist-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.85rem 1rem;
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}
.hist-match { font-weight: 500; font-size: 0.9rem; }
.hist-date  { font-size: 0.78rem; color: #999; font-family: 'DM Mono', monospace; }

/* ── STREAMLIT OVERRIDES ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #fff !important;
    border: 1px solid #e8e6e0 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #1a1a1a !important;
    font-size: 0.88rem !important;
}
.stNumberInput input {
    background: #fff !important;
    border: 1px solid #e8e6e0 !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
}
.stAlert {
    background: #f0faf5 !important;
    border: 1px solid #b7e4c7 !important;
    border-radius: 10px !important;
    color: #2d6a4f !important;
}
.stExpander {
    border: 1px solid #e8e6e0 !important;
    border-radius: 12px !important;
    background: #fff !important;
}
.stProgress > div > div > div {
    background: #52b788 !important;
}
div[data-testid="metric-container"] {
    background: #fff;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 0.75rem 1rem;
}
div[data-testid="metric-container"] label {
    font-size: 0.75rem !important;
    color: #999 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="metric-container"] [data-testid="metric-value"] {
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem !important;
    color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY          = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")

HEADERS_FD   = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
BASE_FD      = "https://api.football-data.org/v4"
BASE_ODDS    = "https://api.the-odds-api.com/v4"

MARKET_MAP = {
    'btts':             'BTTS',
    'over25':           'Over 2.5',
    'over15':           'Over 1.5',
    'under35':          'Under 3.5',
    'under25':          'Under 2.5',
    'second_half_more': '2º Tempo +',
}
THRESHOLDS = {
    'btts': 60, 'over25': 60, 'over15': 80,
    'under35': 70, 'under25': 60, 'second_half_more': 60,
}
CURRENCIES = {
    'EUR': {'symbol': '€',  'flag': '🇪🇺'},
    'BRL': {'symbol': 'R$', 'flag': '🇧🇷'},
    'USD': {'symbol': '$',  'flag': '🇺🇸'},
    'AOA': {'symbol': 'Kz', 'flag': '🇦🇴'},
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def g_total(m): return (m['score']['fullTime'].get('home') or 0) + (m['score']['fullTime'].get('away') or 0)
def g_home(m):  return m['score']['fullTime'].get('home') or 0
def g_away(m):  return m['score']['fullTime'].get('away') or 0
def g_fh(m):    return (m['score']['halfTime'].get('home') or 0) + (m['score']['halfTime'].get('away') or 0)
def g_sh(m):    return g_total(m) - g_fh(m)

# ── API ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_fd(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        r = requests.get(f"{BASE_FD}/{endpoint}", headers=HEADERS_FD, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_fd("competitions")
    if not data:
        return {}
    top = ["Premier League","Primera Division","Serie A","Bundesliga","Ligue 1",
           "Primeira Liga","Eredivisie","UEFA Champions League"]
    return {c["name"]: c["id"] for c in data.get("competitions", [])
            if c["name"] in top and c.get("currentSeason")}

@st.cache_data(ttl=600)
def get_matches(comp_id):
    today = datetime.now().strftime("%Y-%m-%d")
    nxt   = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data  = fetch_fd(f"competitions/{comp_id}/matches?dateFrom={today}&dateTo={nxt}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile(team_id, comp_id):
    p = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado',
         'over25': 50, 'btts': 50, 'over15': 70, 'under35': 70,
         'under25': 50, 'second_half_more': 50}
    try:
        sd = fetch_fd(f"competitions/{comp_id}/standings")
        if sd:
            for g in sd.get('standings', []):
                for t in g.get('table', []):
                    if t['team']['id'] == team_id:
                        pg = t['playedGames']; gf = t['goalsFor']; ga = t['goalsAgainst']
                        if pg > 0:
                            p['ataque'] = min(10, max(1, round((gf/pg/1.4)*7+1)))
                            p['defesa'] = min(10, max(1, round((1.4/max(ga/pg,0.1))*7+1)))
                        break
        md = fetch_fd(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if md:
            rm = md.get('matches', [])[:10]
            if rm:
                n = len(rm)
                p['over25']           = round(sum(1 for m in rm if g_total(m) > 2.5)/n*100)
                p['btts']             = round(sum(1 for m in rm if g_home(m)>0 and g_away(m)>0)/n*100)
                p['over15']           = round(sum(1 for m in rm if g_total(m) > 1.5)/n*100)
                p['under35']          = round(sum(1 for m in rm if g_total(m) < 3.5)/n*100)
                p['under25']          = round(sum(1 for m in rm if g_total(m) < 2.5)/n*100)
                p['second_half_more'] = round(sum(1 for m in rm if g_sh(m) > g_fh(m))/n*100)
        a, d = p['ataque'], p['defesa']
        p['estilo'] = 'ofensivo' if a>=7 and d<=6 else 'defensivo' if d>=7 and a<=6 else 'equilibrado'
    except Exception:
        pass
    return p

# ── ANALYZER ─────────────────────────────────────────────────────────────────
class Analisador:
    def __init__(self):
        if 'historico' not in st.session_state:
            st.session_state.historico = []

    @st.cache_data(ttl=3600)
    def fetch_h2h(_self, hid, aid, limit=5):
        try:
            hm = fetch_fd(f"teams/{hid}/matches?status=FINISHED&limit=20")
            h2h = []
            if hm:
                for m in hm.get('matches', []):
                    if m.get('awayTeam',{}).get('id')==aid or m.get('homeTeam',{}).get('id')==aid:
                        h2h.append(m)
                        if len(h2h) >= limit: break
            n = max(len(h2h),1)
            return {
                'btts_h2h':  sum(1 for m in h2h if g_home(m)>0 and g_away(m)>0)/n*100,
                'over25_h2h': sum(1 for m in h2h if g_total(m)>2.5)/n*100,
            }
        except Exception:
            return {'btts_h2h': 50, 'over25_h2h': 50}

    def ajustes_estilo(self, hp, ap):
        aj = {k: 0 for k in MARKET_MAP}
        hs, as_ = hp['estilo'], ap['estilo']
        if hs=='ofensivo' and as_=='ofensivo':
            aj.update({'btts':8,'over25':12,'over15':5,'under35':-10,'under25':-8,'second_half_more':5})
        elif hs=='defensivo' and as_=='defensivo':
            aj.update({'btts':-10,'over25':-15,'over15':-5,'under35':12,'under25':10,'second_half_more':-5})
        elif 'ofensivo' in [hs, as_]:
            aj.update({'btts':3,'over25':2,'over15':2,'under35':-3,'under25':-2,'second_half_more':3})
        if hp['ataque']>=8 and ap['defesa']<=5:
            for k in ['btts','over25','over15','second_half_more']: aj[k]+=5
            for k in ['under35','under25']: aj[k]-=5
        if ap['ataque']>=8 and hp['defesa']<=5:
            for k in ['btts','over25','over15','second_half_more']: aj[k]+=5
            for k in ['under35','under25']: aj[k]-=5
        return aj

    def ajustes_comp(self, competition):
        aj = {k: 0 for k in MARKET_MAP}
        if 'Premier League' in competition:
            aj.update({'over25':5,'over15':3,'under35':-2,'under25':-1,'second_half_more':2})
        elif 'Serie A' in competition:
            aj.update({'btts':-3,'over25':-2,'over15':-1,'under35':4,'under25':3,'second_half_more':-2})
        elif 'Bundesliga' in competition:
            aj.update({'btts':5,'over25':8,'over15':5,'under35':-8,'under25':-7,'second_half_more':5})
        return aj

    def analisar(self, ht, at, competition, hid, aid, comp_id, markets):
        hp  = fetch_team_profile(hid, comp_id)
        ap  = fetch_team_profile(aid, comp_id)
        h2h = self.fetch_h2h(hid, aid)
        aj  = self.ajustes_estilo(hp, ap)
        ajc = self.ajustes_comp(competition)

        def calc(b, k, lo, hi, h2=0):
            return min(hi, max(lo, b + aj[k] + ajc[k] + h2))

        probs = {
            'btts':             calc((hp['btts']+ap['btts'])/2,           'btts',15,85,(h2h['btts_h2h']-50)/10),
            'over25':           calc((hp['over25']+ap['over25'])/2,       'over25',20,80,(h2h['over25_h2h']-50)/10),
            'over15':           calc((hp['over15']+ap['over15'])/2,       'over15',40,95),
            'under35':          calc((hp['under35']+ap['under35'])/2,     'under35',30,90),
            'under25':          calc((hp['under25']+ap['under25'])/2,     'under25',25,85),
            'second_half_more': calc((hp['second_half_more']+ap['second_half_more'])/2,'second_half_more',20,80),
        }

        res = {f'prob_{k}': round(v,1) for k,v in probs.items()}
        res.update({f'odd_justa_{k}': round(100/v,2) for k,v in probs.items()})
        res['h2h'] = h2h
        res['home_profile'] = hp
        res['away_profile']  = ap

        # recommendations
        recs = []
        for k, v in probs.items():
            if k not in markets: continue
            t = THRESHOLDS[k]
            recs.append({
                'key': k, 'label': MARKET_MAP[k], 'prob': v,
                'cls': 'hi' if v>=t else 'mid' if v>=t-10 else 'lo',
            })
        res['recomendacoes'] = recs

        st.session_state.historico.append({
            'home': ht, 'away': at,
            'probs': {k: round(v,1) for k,v in probs.items()},
            'data': datetime.now().strftime('%d/%m %H:%M'),
        })
        return res

    def gerar_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial","B",12)
        pdf.cell(200,9,"Bet Analyzer — Histórico",ln=1,align='C')
        pdf.ln(5)
        pdf.set_font("Arial",size=9)
        for a in reversed(st.session_state.historico[-20:]):
            pdf.set_font("Arial","B",9)
            pdf.cell(200,6,f"{a['home']} vs {a['away']}",ln=1)
            pdf.set_font("Arial",size=8)
            pdf.cell(200,5,f"  {a['data']}",ln=1)
            for k,v in a['probs'].items():
                pdf.cell(200,4,f"    {MARKET_MAP.get(k,k)}: {v}%",ln=1)
            pdf.ln(3)
        return pdf.output(dest='S').encode('latin-1',errors='ignore')


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    for k, d in [
        ('page','analyze'), ('selected_match',None), ('currency','EUR'),
        ('analysis',None), ('selected_markets',['btts','over25','over15']),
    ]:
        if k not in st.session_state:
            st.session_state[k] = d

    an    = Analisador()
    comps = get_competitions()
    api_ok  = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"
    c_info  = CURRENCIES[st.session_state.currency]

    # ── NAV ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="nav-wrap">
        <div class="nav-logo">⚽ <span>Bet</span>Analyzer</div>
        <div class="nav-status">
            <span class="dot {'dot-on' if api_ok else 'dot-off'}"></span> Football API
            &nbsp;&nbsp;
            <span class="dot {'dot-on' if odds_ok else 'dot-warn'}"></span> Odds API
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content">', unsafe_allow_html=True)

    # ── TOP ROW: tabs + currency ──────────────────────────────────────────────
    col_tabs, col_curr, col_market = st.columns([3, 1, 2])

    with col_tabs:
        t1, t2, t3 = st.columns(3)
        with t1:
            if st.button("Análise", key="nav_a",
                         type="primary" if st.session_state.page=='analyze' else "secondary",
                         use_container_width=True):
                st.session_state.page = 'analyze'; st.rerun()
        with t2:
            if st.button("Perfis", key="nav_p",
                         type="primary" if st.session_state.page=='profiles' else "secondary",
                         use_container_width=True):
                st.session_state.page = 'profiles'; st.rerun()
        with t3:
            if st.button("Histórico", key="nav_h",
                         type="primary" if st.session_state.page=='history' else "secondary",
                         use_container_width=True):
                st.session_state.page = 'history'; st.rerun()

    with col_curr:
        opts = [f"{v['flag']} {k}" for k,v in CURRENCIES.items()]
        idx  = list(CURRENCIES.keys()).index(st.session_state.currency)
        sel  = st.selectbox("Moeda", opts, index=idx,
                            label_visibility="collapsed", key="curr_sel")
        new  = list(CURRENCIES.keys())[opts.index(sel)]
        if new != st.session_state.currency:
            st.session_state.currency = new; st.rerun()

    with col_market:
        rev  = {v:k for k,v in MARKET_MAP.items()}
        sel_m = st.multiselect("Mercados",list(MARKET_MAP.values()),
                               default=[MARKET_MAP[m] for m in st.session_state.selected_markets if m in MARKET_MAP],
                               label_visibility="collapsed", key="mkt_sel")
        st.session_state.selected_markets = [rev[m] for m in sel_m if m in rev]

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── COMPETITION + MATCHES ─────────────────────────────────────────────────
    if comps:
        comp_list = list(comps.keys())
        st.markdown('<div class="section-title">Competição</div>', unsafe_allow_html=True)
        selected_comp = st.selectbox("Competição", comp_list, index=0,
                                     key="comp_sel", label_visibility="collapsed")
        comp_id = comps[selected_comp]

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Partidas (próximos 7 dias)</div>', unsafe_allow_html=True)

        with st.spinner("Carregando partidas..."):
            matches = get_matches(comp_id)

        scheduled = [m for m in matches[:16] if m["status"] in ["SCHEDULED","TIMED"]]

        if not scheduled:
            st.info("Nenhuma partida encontrada para esta competição.")
        else:
            # grid 3 cols
            cols_per_row = 3
            rows = [scheduled[i:i+cols_per_row] for i in range(0, len(scheduled), cols_per_row)]
            for row in rows:
                cols = st.columns(cols_per_row)
                for col, m in zip(cols, row):
                    try:
                        dt = datetime.fromisoformat(m["utcDate"].replace("Z","+00:00"))
                        ht = m["homeTeam"]["name"]
                        at = m["awayTeam"]["name"]
                        is_sel = (st.session_state.selected_match and
                                  st.session_state.selected_match.get('id') == m["id"])
                        with col:
                            label = f"{'✓ ' if is_sel else ''}{ht} vs {at}\n{dt.strftime('%d/%m')} · {dt.strftime('%H:%M')}"
                            if st.button(label, key=f"m_{m['id']}", use_container_width=True,
                                         type="primary" if is_sel else "secondary"):
                                st.session_state.selected_match = {
                                    'id': m["id"],
                                    'home_id':   m["homeTeam"]["id"],
                                    'away_id':   m["awayTeam"]["id"],
                                    'home_team': ht,
                                    'away_team': at,
                                    'date': dt,
                                }
                                st.session_state.analysis = None
                                st.rerun()
                    except Exception:
                        continue

    # ── ANALYZE PANEL ─────────────────────────────────────────────────────────
    if st.session_state.selected_match:
        match = st.session_state.selected_match
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Partida selecionada</div>', unsafe_allow_html=True)

        col_info, col_odd, col_stake, col_btn = st.columns([3, 1, 1, 2])
        with col_info:
            st.markdown(f"""
            <div style="padding: 0.6rem 0; font-weight:600; font-size:1rem;">
                {match['home_team']} <span style="color:#999;font-weight:400;font-size:0.85rem;margin:0 0.5rem;">vs</span> {match['away_team']}
            </div>
            """, unsafe_allow_html=True)
        with col_odd:
            odd = st.number_input("Odd", min_value=1.01, value=2.00, step=0.05,
                                  format="%.2f", label_visibility="visible")
        with col_stake:
            stake = st.number_input(f"Stake ({c_info['symbol']})", min_value=0.0,
                                    value=10.0, step=1.0, format="%.2f",
                                    label_visibility="visible")
        with col_btn:
            st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
            if st.button("Analisar →", key="run_analysis", use_container_width=True, type="primary"):
                if not st.session_state.selected_markets:
                    st.warning("Selecione pelo menos um mercado.")
                else:
                    with st.spinner("Analisando..."):
                        result = an.analisar(
                            match['home_team'], match['away_team'],
                            selected_comp,
                            match['home_id'], match['away_id'],
                            comp_id, st.session_state.selected_markets
                        )
                        st.session_state.analysis = result
                    st.rerun()

    # ── PAGE CONTENT ──────────────────────────────────────────────────────────

    # ─ ANALYZE PAGE ─
    if st.session_state.page == 'analyze':
        if st.session_state.analysis:
            analise = st.session_state.analysis
            match   = st.session_state.selected_match

            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

            # chips
            chips_markets = ['btts','over25','over15']
            st.markdown('<div class="chips">' +
                ''.join(f'<div class="chip"><div class="chip-val">{analise[f"prob_{k}"]:.0f}%</div>'
                        f'<div class="chip-lbl">{MARKET_MAP[k]}</div></div>'
                        for k in chips_markets) +
                '</div>', unsafe_allow_html=True)

            # probability bars
            st.markdown('<div class="section-title">Probabilidades</div>', unsafe_allow_html=True)
            for rec in analise['recomendacoes']:
                fill_cls = {'hi':'fill-hi','mid':'fill-mid','lo':'fill-lo'}[rec['cls']]
                odd_justa = analise[f"odd_justa_{rec['key']}"]
                st.markdown(f"""
                <div class="prob-row">
                    <span class="prob-label">{rec['label']}</span>
                    <div class="prob-track">
                        <div class="prob-fill {fill_cls}" style="width:{rec['prob']}%"></div>
                    </div>
                    <span class="prob-val">{rec['prob']:.0f}%</span>
                    <span class="prob-odd">{odd_justa}</span>
                </div>
                """, unsafe_allow_html=True)

            # H2H
            if 'h2h' in analise:
                h2h = analise['h2h']
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown('<div class="section-title">Head to Head</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("BTTS H2H", f"{h2h['btts_h2h']:.0f}%")
                with c2:
                    st.metric("Over 2.5 H2H", f"{h2h['over25_h2h']:.0f}%")

            # Value bet
            if st.session_state.selected_match:
                ev = round((odd * (analise['prob_btts']/100)) - 1, 3)
                if ev > 0:
                    st.success(f"✓ Value bet detectado  —  EV: +{ev:.3f}")
                else:
                    st.info(f"EV calculado: {ev:.3f}")

        else:
            if not st.session_state.selected_match:
                st.markdown("""
                <div style="text-align:center;padding:3rem 0;color:#999;">
                    <div style="font-size:2rem;margin-bottom:0.75rem;">⚽</div>
                    <div style="font-size:1rem;font-weight:500;">Selecione uma partida para começar</div>
                    <div style="font-size:0.85rem;margin-top:0.4rem;">Escolha a competição e clique numa partida acima</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:2rem 0;color:#999;">
                    <div style="font-size:0.95rem;">Clique em <strong>Analisar →</strong> para ver as probabilidades</div>
                </div>
                """, unsafe_allow_html=True)

    # ─ PROFILES PAGE ─
    elif st.session_state.page == 'profiles':
        if st.session_state.selected_match and comps:
            match = st.session_state.selected_match
            with st.spinner("Carregando perfis..."):
                hp = fetch_team_profile(match['home_id'], comp_id)
                ap = fetch_team_profile(match['away_id'], comp_id)

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for col, team_name, profile in [(c1, match['home_team'], hp), (c2, match['away_team'], ap)]:
                with col:
                    style_cls = {'ofensivo':'style-off','defensivo':'style-def','equilibrado':'style-eq'}[profile['estilo']]
                    st.markdown(f"""
                    <div class="profile-card">
                        <div class="profile-name">{'🏠' if team_name==match['home_team'] else '🚩'} {team_name}</div>
                        <div class="profile-style {style_cls}">{profile['estilo'].upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                    st.progress(profile['ataque']/10, text=f"Ataque  {profile['ataque']}/10")
                    st.progress(profile['defesa']/10,  text=f"Defesa  {profile['defesa']}/10")
                    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("BTTS",       f"{profile['btts']}%")
                    mc2.metric("Over 2.5",   f"{profile['over25']}%")
                    mc3.metric("Over 1.5",   f"{profile['over15']}%")
        else:
            st.info("Selecione uma partida primeiro.")

    # ─ HISTORY PAGE ─
    elif st.session_state.page == 'history':
        hist = st.session_state.historico
        if hist:
            col_ttl, col_pdf = st.columns([3,1])
            with col_ttl:
                st.markdown(f'<div class="section-title">{len(hist)} análises</div>', unsafe_allow_html=True)
            with col_pdf:
                if st.button("Exportar PDF", key="pdf_btn", use_container_width=True):
                    pdf_data = an.gerar_pdf()
                    st.download_button("⬇ Download",data=pdf_data,
                                       file_name="bet_analyzer.pdf",
                                       mime="application/pdf",
                                       use_container_width=True)

            for entry in reversed(hist[-20:]):
                probs_str = "  ·  ".join(f"{MARKET_MAP.get(k,k)} {v}%" for k,v in list(entry['probs'].items())[:3])
                st.markdown(f"""
                <div class="hist-row">
                    <div>
                        <div class="hist-match">{entry['home']} vs {entry['away']}</div>
                        <div style="font-size:0.78rem;color:#999;margin-top:0.2rem;">{probs_str}</div>
                    </div>
                    <div class="hist-date">{entry['data']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 0;color:#999;">
                <div style="font-size:2rem;margin-bottom:0.75rem;">📈</div>
                <div>Nenhuma análise ainda. Faça uma análise para começar.</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # .content


if __name__ == "__main__":
    main()
