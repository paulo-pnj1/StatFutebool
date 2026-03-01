import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart
from fpdf import FPDF

# ── SETUP ─────────────────────────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="⚽ Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="collapsed"
)

# ── DESIGN SYSTEM — MOBILE FIRST ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #060810;
    color: #cbd5e1;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"] { display: none !important; }

.block-container {
    padding: 0.75rem 0.75rem 5rem !important;
    max-width: 100% !important;
}

[data-testid="stSidebar"] {
    background: #0b0e1a !important;
    border-right: 1px solid #1a2035 !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] .block-container { padding: 0.85rem 0.75rem !important; }

/* TOP BAR */
.top-bar {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.6rem 0.85rem;
    background: rgba(6,8,16,0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #1a2035;
    margin: -0.75rem -0.75rem 0.85rem;
}
.top-bar .tb-icon { font-size: 1.2rem; flex-shrink: 0; }
.top-bar .tb-title { font-size: 0.92rem; font-weight: 700; color: #f1f5f9; letter-spacing:-0.02em; flex:1; }
.top-bar .tb-sub { font-size: 0.58rem; color: #334155; font-family:'JetBrains Mono',monospace; }
.status-dots { display:flex; gap:0.3rem; align-items:center; flex-shrink:0; }
.dot { width:7px; height:7px; border-radius:50%; }
.dot-g { background:#22c55e; box-shadow:0 0 5px #22c55e88; }
.dot-y { background:#eab308; }
.dot-r { background:#ef4444; }

/* LABELS */
.sec-label {
    font-size: 0.59rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: #334155; margin-bottom: 0.48rem;
    margin-top: 0.1rem; display: block;
}

/* MATCH BANNER */
.match-banner {
    background: linear-gradient(135deg,#0f172a,#0d1526);
    border: 1px solid #1e3a5f; border-radius: 12px;
    padding: 0.8rem 1rem; margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}
.match-teams { flex:1; min-width:0; }
.match-teams .mh { font-size:0.9rem; font-weight:700; color:#f1f5f9; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.match-teams .mv { font-size:0.58rem; color:#334155; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin:0.08rem 0; }
.match-teams .ma { font-size:0.85rem; font-weight:600; color:#94a3b8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.match-date { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#475569; background:#0a0f1e; border:1px solid #1a2035; border-radius:6px; padding:0.28rem 0.5rem; white-space:nowrap; flex-shrink:0; }

/* METRIC GRID */
.metric-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.42rem; margin-bottom:0.72rem; }
@media(max-width:480px){ .metric-grid{ grid-template-columns:repeat(2,1fr); } }
.metric-card {
    background:#0b0e1a; border:1px solid #1a2035; border-radius:10px;
    padding:0.58rem 0.45rem; text-align:center; position:relative; overflow:hidden;
}
.metric-card::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; border-radius:10px 10px 0 0; }
.mc-g::before { background:linear-gradient(90deg,#166534,#4ade80); }
.mc-y::before { background:linear-gradient(90deg,#d97706,#fbbf24); }
.mc-r::before { background:linear-gradient(90deg,#991b1b,#f87171); }
.metric-card .mv { font-family:'JetBrains Mono',monospace; font-size:1.4rem; font-weight:700; line-height:1; letter-spacing:-0.03em; }
.mc-g .mv { color:#4ade80; }  .mc-y .mv { color:#fbbf24; }  .mc-r .mv { color:#f87171; }
.metric-card .ml { font-size:0.57rem; font-weight:600; color:#475569; text-transform:uppercase; letter-spacing:0.07em; margin-top:0.16rem; }
.metric-card .mo { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#334155; margin-top:0.1rem; }

/* PROB BARS */
.pbar-wrap { background:#0b0e1a; border:1px solid #1a2035; border-radius:10px; padding:0.65rem 0.82rem; margin-bottom:0.72rem; }
.pbar-row { display:flex; align-items:center; gap:0.52rem; margin-bottom:0.48rem; }
.pbar-row:last-child { margin-bottom:0; }
.pbar-lbl { font-size:0.63rem; color:#64748b; width:68px; flex-shrink:0; font-weight:500; }
.pbar-track { flex:1; height:5px; background:#1a2035; border-radius:3px; overflow:hidden; }
.pbar-fill { height:100%; border-radius:3px; }
.pb-g { background:linear-gradient(90deg,#166534,#4ade80); }
.pb-y { background:linear-gradient(90deg,#92400e,#fbbf24); }
.pb-r { background:linear-gradient(90deg,#7f1d1d,#f87171); }
.pbar-pct { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#94a3b8; width:28px; text-align:right; flex-shrink:0; }

/* ANALYSIS CARD */
.analysis-card { background:#0b0e1a; border:1px solid #1a2035; border-radius:10px; padding:0.65rem 0.8rem; margin-bottom:0.72rem; }
.aline { display:flex; gap:0.48rem; align-items:flex-start; padding:0.3rem 0; border-bottom:1px solid #0f1626; font-size:0.69rem; color:#64748b; line-height:1.45; }
.aline:last-child { border-bottom:none; padding-bottom:0; }
.aline .ai { flex-shrink:0; font-size:0.73rem; line-height:1.45; }

/* H2H */
.h2h-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.42rem; margin-bottom:0.72rem; }
.h2h-tile { background:#0b0e1a; border:1px solid #1a2035; border-radius:10px; padding:0.58rem; text-align:center; }
.h2h-tile .hv { font-family:'JetBrains Mono',monospace; font-size:1.15rem; font-weight:700; color:#60a5fa; }
.h2h-tile .hl { font-size:0.57rem; color:#334155; text-transform:uppercase; letter-spacing:0.06em; margin-top:0.08rem; }

/* PILLS */
.pill-wrap { display:flex; flex-wrap:wrap; gap:0.32rem; margin-bottom:0.72rem; }
.pill { display:inline-flex; align-items:center; gap:0.28rem; padding:0.26rem 0.58rem; border-radius:999px; font-size:0.63rem; font-weight:600; line-height:1; }
.pill-g { background:#052e16; color:#4ade80; border:1px solid #166534; }
.pill-y { background:#1c1400; color:#fbbf24; border:1px solid #713f12; }
.pill-s { background:#0f172a; color:#475569; border:1px solid #1e2535; }

/* TEAM CARD */
.team-card { background:#0b0e1a; border:1px solid #1a2035; border-radius:10px; padding:0.78rem; margin-bottom:0.62rem; }
.tc-hdr { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.6rem; }
.tc-name { font-size:0.8rem; font-weight:700; color:#f1f5f9; }
.tc-badge { font-size:0.54rem; font-weight:700; padding:0.17rem 0.48rem; border-radius:999px; text-transform:uppercase; letter-spacing:0.07em; }
.tb-of { background:#172554; color:#93c5fd; border:1px solid #1d4ed8; }
.tb-df { background:#1c1917; color:#a8a29e; border:1px solid #44403c; }
.tb-eq { background:#1a0f2e; color:#a78bfa; border:1px solid #5b21b6; }
.tc-stats { display:flex; gap:0.48rem; margin-top:0.5rem; padding-top:0.42rem; border-top:1px solid #0f1626; flex-wrap:wrap; }
.tc-stat { font-size:0.6rem; font-weight:500; }

/* EV */
.ev-box { text-align:center; margin-top:0.38rem; padding:0.32rem; background:#060810; border-radius:6px; border:1px solid #1a2035; }
.ev-val { font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:700; }
.ev-lbl { font-size:0.57rem; margin-top:0.08rem; }

/* DIVIDER */
.divider { height:1px; background:#1a2035; margin:0.75rem 0; border:none; }

/* SIDEBAR */
.sb-title { font-size:0.57rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#1e3a5f; padding:0.38rem 0 0.32rem; margin-bottom:0.38rem; border-bottom:1px solid #0f1626; }
.wi { display:flex; align-items:center; padding:0.3rem 0.48rem; background:#060810; border:1px solid #1a2035; border-radius:6px; margin-bottom:0.26rem; font-size:0.65rem; color:#64748b; gap:0.32rem; }

/* STREAMLIT OVERRIDES */
.stTabs [data-baseweb="tab-list"] { background:#0b0e1a !important; border:1px solid #1a2035 !important; border-radius:9px; padding:3px; gap:2px; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#475569 !important; border-radius:7px !important; font-size:0.71rem !important; font-weight:600 !important; padding:0.36rem 0.68rem !important; }
.stTabs [aria-selected="true"] { background:#1e3a5f !important; color:#93c5fd !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:0.78rem !important; }

.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
    font-size:0.61rem !important; font-weight:600 !important; text-transform:uppercase !important;
    letter-spacing:0.09em !important; color:#334155 !important;
}
[data-baseweb="select"] > div:first-child, [data-baseweb="base-input"] {
    background:#0b0e1a !important; border:1px solid #1a2035 !important;
    border-radius:8px !important; font-size:0.75rem !important; color:#cbd5e1 !important;
}
.stButton > button {
    background:linear-gradient(135deg,#1d4ed8,#1e40af) !important;
    color:#fff !important; border:none !important; border-radius:9px !important;
    font-size:0.77rem !important; font-weight:700 !important; padding:0.58rem 1.3rem !important;
    width:100% !important; transition:opacity 0.15s,transform 0.1s !important;
}
.stButton > button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }
.stDownloadButton > button {
    background:#051a05 !important; color:#4ade80 !important;
    border:1px solid #166534 !important; border-radius:8px !important;
    font-size:0.71rem !important; font-weight:600 !important;
}
div[data-testid="stExpander"] { background:#0b0e1a !important; border:1px solid #1a2035 !important; border-radius:9px !important; }
div[data-testid="stExpander"] summary { font-size:0.71rem !important; color:#64748b !important; }
.stDataFrame { font-size:0.67rem !important; }
.stAlert { font-size:0.71rem !important; border-radius:8px !important; }
.stNumberInput input { background:#0b0e1a !important; border:1px solid #1a2035 !important; color:#cbd5e1 !important; border-radius:7px !important; font-family:'JetBrains Mono',monospace !important; font-size:0.75rem !important; }
.stTextInput input { background:#0b0e1a !important; border:1px solid #1a2035 !important; color:#cbd5e1 !important; border-radius:7px !important; font-size:0.75rem !important; }
.stMultiSelect [data-baseweb="tag"] { background:#1e3a5f !important; color:#93c5fd !important; border-radius:4px !important; font-size:0.63rem !important; }
.stProgress > div > div > div { border-radius:3px !important; }

::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#1a2035; border-radius:2px; }

@media(max-width:640px){
    .block-container { padding:0.5rem 0.5rem 4.5rem !important; }
    .top-bar { margin:-0.5rem -0.5rem 0.7rem; }
}
</style>
""", unsafe_allow_html=True)

# ── ENV ────────────────────────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY          = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER            = os.getenv("EMAIL_USER")
EMAIL_PASS            = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY, "Accept": "application/json"}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS     = "https://api.the-odds-api.com/v4"

MARKET_MAP = {
    'btts':'BTTS','over25':'Over 2.5','over15':'Over 1.5',
    'under35':'Under 3.5','under25':'Under 2.5','second_half_more':'2º Tempo +'
}
THRESHOLDS = {'btts':60,'over25':60,'over15':80,'under35':70,'under25':60,'second_half_more':60}

# ── UTILS ─────────────────────────────────────────────────────────────────────
def calculate_value_bet(real_prob, odd):
    if not odd or odd <= 0 or not real_prob: return None
    return round((odd * (real_prob / 100)) - 1, 3)

def get_total_goals(m): return (m['score']['fullTime'].get('home',0) or 0)+(m['score']['fullTime'].get('away',0) or 0)
def get_home_goals(m):  return m['score']['fullTime'].get('home',0) or 0
def get_away_goals(m):  return m['score']['fullTime'].get('away',0) or 0
def get_fh_goals(m):    return (m['score']['halfTime'].get('home',0) or 0)+(m['score']['halfTime'].get('away',0) or 0)
def get_sh_goals(m):    return get_total_goals(m) - get_fh_goals(m)

def mc_cls(p, t): return "mc-g" if p>=t else "mc-y" if p>=t-10 else "mc-r"
def pb_cls(p, t): return "pb-g" if p>=t else "pb-y" if p>=t-10 else "pb-r"

# ── API ────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_fd(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY": return None
    try:
        r = requests.get(f"{BASE_URL_FOOTBALL}/{endpoint}", headers=HEADERS_FOOTBALL, timeout=15)
        if r.status_code == 429: st.error("❌ Rate limit atingido."); return None
        return r.json() if r.status_code == 200 else None
    except Exception: return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_fd("competitions")
    if not data or "competitions" not in data: return {}
    top = ["Premier League","Primera Division","Serie A","Bundesliga","Ligue 1",
           "Primeira Liga","Eredivisie","Jupiler Pro League","Scottish Premiership",
           "UEFA Champions League","UEFA Europa League","UEFA Conference League"]
    return {c["name"]: c["id"] for c in data["competitions"] if c["name"] in top and c.get("currentSeason")}

@st.cache_data(ttl=600)
def get_matches(comp_id):
    today = datetime.now().strftime("%Y-%m-%d")
    nw    = (datetime.now()+timedelta(days=7)).strftime("%Y-%m-%d")
    data  = fetch_fd(f"competitions/{comp_id}/matches?dateFrom={today}&dateTo={nw}")
    return data.get("matches",[]) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile(team_id, comp_id):
    p = {'ataque':5,'defesa':5,'estilo':'equilibrado','over25':50,'btts':50,'over15':70,'under35':70,'under25':50,'second_half_more':50}
    try:
        sd = fetch_fd(f"competitions/{comp_id}/standings")
        if sd and 'standings' in sd:
            for g in sd['standings']:
                for t in g['table']:
                    if t['team']['id'] == team_id:
                        pg,gf,ga = t['playedGames'],t['goalsFor'],t['goalsAgainst']
                        if pg>0:
                            p['ataque'] = min(10,max(1,round((gf/pg/1.4)*7+1)))
                            p['defesa']  = min(10,max(1,round((1.4/max(ga/pg,0.1))*7+1)))
                        break
        md = fetch_fd(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if md and 'matches' in md:
            rm = md['matches'][:10]
            if rm:
                n = len(rm)
                p['over25']           = round(sum(1 for m in rm if get_total_goals(m)>2.5)/n*100)
                p['btts']             = round(sum(1 for m in rm if get_home_goals(m)>0 and get_away_goals(m)>0)/n*100)
                p['over15']           = round(sum(1 for m in rm if get_total_goals(m)>1.5)/n*100)
                p['under35']          = round(sum(1 for m in rm if get_total_goals(m)<3.5)/n*100)
                p['under25']          = round(sum(1 for m in rm if get_total_goals(m)<2.5)/n*100)
                p['second_half_more'] = round(sum(1 for m in rm if get_sh_goals(m)>get_fh_goals(m))/n*100)
        a,d = p['ataque'],p['defesa']
        p['estilo'] = 'ofensivo' if a>=7 and d<=6 else 'defensivo' if d>=7 and a<=6 else 'equilibrado'
        return p
    except Exception: return p

# ── ANALISADOR ────────────────────────────────────────────────────────────────
class Analisador:
    def __init__(self):
        for k,v in [('watchlist',[]),('historico',[])]:
            if k not in st.session_state: st.session_state[k] = v
        self.watchlist = st.session_state.watchlist
        self.historico = st.session_state.historico

    @st.cache_data(ttl=3600)
    def fetch_h2h(_self, hid, aid, limit=5):
        try:
            hm = fetch_fd(f"teams/{hid}/matches?status=FINISHED&limit=20")
            h2h = []
            if hm and 'matches' in hm:
                for m in hm['matches']:
                    if m.get('awayTeam',{}).get('id')==aid or m.get('homeTeam',{}).get('id')==aid:
                        h2h.append(m)
                        if len(h2h)>=limit: break
            n = max(len(h2h),1)
            return {'btts_h2h': sum(1 for m in h2h if get_home_goals(m)>0 and get_away_goals(m)>0)/n*100,
                    'over25_h2h': sum(1 for m in h2h if get_total_goals(m)>2.5)/n*100}
        except Exception: return {'btts_h2h':50,'over25_h2h':50}

    def fetch_live_odds(self, ht, at):
        try:
            if ODDS_API_KEY == "sua_chave_the_odds_api": return []
            r = requests.get(f"{BASE_URL_ODDS}/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals", timeout=10)
            if r.status_code == 200:
                for ev in r.json():
                    if ht.lower() in ev['home_team'].lower() and at.lower() in ev['away_team'].lower():
                        return ev.get('bookmakers',[])
            return []
        except Exception: return []

    def ajustes_estilo(self, hp, ap):
        aj = {k:0 for k in MARKET_MAP}
        hs,as_ = hp['estilo'],ap['estilo']
        if hs=='ofensivo' and as_=='ofensivo':   aj.update({'btts':8,'over25':12,'over15':5,'under35':-10,'under25':-8,'second_half_more':5})
        elif hs=='defensivo' and as_=='defensivo': aj.update({'btts':-10,'over25':-15,'over15':-5,'under35':12,'under25':10,'second_half_more':-5})
        elif 'ofensivo' in [hs,as_]:             aj.update({'btts':3,'over25':2,'over15':2,'under35':-3,'under25':-2,'second_half_more':3})
        if hp['ataque']>=8 and ap['defesa']<=5: aj['btts']+=5;aj['over25']+=8;aj['over15']+=4;aj['under35']-=6;aj['under25']-=5;aj['second_half_more']+=4
        if ap['ataque']>=8 and hp['defesa']<=5: aj['btts']+=5;aj['over25']+=8;aj['over15']+=4;aj['under35']-=6;aj['under25']-=5;aj['second_half_more']+=4
        return aj

    def ajustes_comp(self, competition):
        aj = {k:0 for k in MARKET_MAP}
        if 'Premier League' in competition:  aj.update({'over25':5,'over15':3,'under35':-2,'under25':-1,'second_half_more':2})
        elif 'Serie A' in competition:        aj.update({'btts':-3,'over25':-2,'over15':-1,'under35':4,'under25':3,'second_half_more':-2})
        elif 'Bundesliga' in competition:     aj.update({'btts':5,'over25':8,'over15':5,'under35':-8,'under25':-7,'second_half_more':5})
        return aj

    def analisar(self, ht, at, competition, hid, aid, comp_id, markets):
        hp  = fetch_team_profile(hid, comp_id)
        ap  = fetch_team_profile(aid, comp_id)
        h2h = self.fetch_h2h(hid, aid)
        aj  = self.ajustes_estilo(hp, ap)
        ajc = self.ajustes_comp(competition)

        def calc(b, k, lo, hi, h2=0): return min(hi, max(lo, b+aj[k]+ajc[k]+h2))

        probs = {
            'btts':            calc((hp['btts']+ap['btts'])/2,           'btts',  15,85,(h2h['btts_h2h']-50)/10),
            'over25':          calc((hp['over25']+ap['over25'])/2,        'over25',20,80,(h2h['over25_h2h']-50)/10),
            'over15':          calc((hp['over15']+ap['over15'])/2,        'over15',40,95),
            'under35':         calc((hp['under35']+ap['under35'])/2,      'under35',30,90),
            'under25':         calc((hp['under25']+ap['under25'])/2,      'under25',25,85),
            'second_half_more':calc((hp['second_half_more']+ap['second_half_more'])/2,'second_half_more',20,80)
        }

        res = {f'prob_{k}': round(v,1) for k,v in probs.items()}
        res.update({f'odd_justa_{k}': round(100/v,2) for k,v in probs.items()})
        res['h2h']           = h2h
        res['home_profile']  = hp
        res['away_profile']  = ap
        res['detail_lines']  = self._lines(ht, at, hp, ap, h2h)
        res['recomendacoes'] = self._recs(probs, markets)

        self.historico.append({'home':ht,'away':at,'prob_btts':res['prob_btts'],'prob_over25':res['prob_over25'],'data':datetime.now().strftime('%Y-%m-%d %H:%M')})
        st.session_state.historico = self.historico
        return res

    def _lines(self, ht, at, hp, ap, h2h):
        si = lambda s: "⚡" if s=='ofensivo' else "🛡️" if s=='defensivo' else "⚖️"
        lines = [
            (si(hp['estilo']), f"{ht}: {hp['estilo'].upper()} · Atq {hp['ataque']}/10 · Def {hp['defesa']}/10"),
            (si(ap['estilo']), f"{at}: {ap['estilo'].upper()} · Atq {ap['ataque']}/10 · Def {ap['defesa']}/10"),
            ("🤝", f"H2H: BTTS {h2h['btts_h2h']:.0f}% · Over 2.5 {h2h['over25_h2h']:.0f}%"),
        ]
        if hp['estilo']=='ofensivo' and ap['estilo']=='ofensivo': lines.append(("⚔️","Dois times ofensivos → Alta expectativa de gols"))
        elif hp['estilo']=='defensivo' and ap['estilo']=='defensivo': lines.append(("🔒","Dois times defensivos → Jogo fechado esperado"))
        else: lines.append(("📊","Estilos contrastantes → Jogo equilibrado"))
        if hp['ataque']>=8: lines.append(("✅",f"{ht} tem ataque muito forte"))
        if ap['ataque']>=8: lines.append(("✅",f"{at} tem ataque muito forte"))
        if hp['defesa']<=5: lines.append(("⚠️",f"{ht} tem defesa vulnerável"))
        if ap['defesa']<=5: lines.append(("⚠️",f"{at} tem defesa vulnerável"))
        return lines

    def _recs(self, probs, markets):
        icons = {'btts':'🎯','over25':'⚽','over15':'⚽','under35':'🛡️','under25':'🛡️','second_half_more':'⏱️'}
        recs = []
        for k,v in probs.items():
            if k not in markets: continue
            t = THRESHOLDS[k]
            lbl = f"{icons[k]} {MARKET_MAP[k]}"
            pct = f"{v:.0f}%"
            recs.append(('g',lbl,pct) if v>=t else ('y',lbl,pct) if v>=t-10 else ('s',lbl,pct))
        return recs

    def send_alert(self, mi, analise, email_to):
        if not EMAIL_USER or not EMAIL_PASS: st.warning("Configure EMAIL_USER e EMAIL_PASS no .env."); return
        try:
            msg = MimeMultipart()
            msg['From'],msg['To'] = EMAIL_USER,email_to
            msg['Subject'] = f"⚽ {mi['home_team']} vs {mi['away_team']}"
            body = f"Partida: {mi['home_team']} vs {mi['away_team']}\n\n"
            for k in MARKET_MAP:
                prob = analise.get(f'prob_{k}',0)
                v = calculate_value_bet(prob,2.0)
                if v and v>0.1: body += f"- {k.upper()}: {prob}% | EV: {v:.2f}\n"
            msg.attach(MimeText(body,'plain'))
            s = smtplib.SMTP('smtp.gmail.com',587); s.starttls()
            s.login(EMAIL_USER,EMAIL_PASS); s.sendmail(EMAIL_USER,email_to,msg.as_string()); s.quit()
            st.success("📧 Alerta enviado!")
        except Exception as e: st.error(f"Erro email: {e}")

    def gerar_pdf(self):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial",size=11)
        pdf.cell(200,9,"Relatório de Análises",ln=1,align='C'); pdf.ln(6)
        for a in self.historico[-10:]:
            pdf.cell(200,7,f"{a['home']} vs {a['away']}",ln=1)
            pdf.cell(200,7,f"BTTS: {a['prob_btts']}% | Over 2.5: {a['prob_over25']}%",ln=1)
            pdf.ln(3)
        return pdf.output(dest='S')

# ── RENDER HELPERS ────────────────────────────────────────────────────────────
def render_metric_grid(analise, markets):
    tiles = ""
    for m in markets:
        prob = analise.get(f'prob_{m}',0)
        odd  = analise.get(f'odd_justa_{m}',0)
        c    = mc_cls(prob, THRESHOLDS.get(m,60))
        lbl  = MARKET_MAP.get(m,m)
        tiles += f'<div class="metric-card {c}"><div class="mv">{prob:.0f}<span style="font-size:0.52em;font-weight:400;color:#334155">%</span></div><div class="ml">{lbl}</div><div class="mo">@ {odd}</div></div>'
    st.markdown(f'<div class="metric-grid">{tiles}</div>', unsafe_allow_html=True)

def render_prob_bars(analise, markets):
    rows = ""
    for m in markets:
        prob = analise.get(f'prob_{m}',0)
        c    = pb_cls(prob, THRESHOLDS.get(m,60))
        lbl  = MARKET_MAP.get(m,m)
        rows += f'<div class="pbar-row"><span class="pbar-lbl">{lbl}</span><div class="pbar-track"><div class="pbar-fill {c}" style="width:{prob}%"></div></div><span class="pbar-pct">{prob:.0f}%</span></div>'
    st.markdown(f'<div class="pbar-wrap">{rows}</div>', unsafe_allow_html=True)

def render_detail_card(lines):
    html = "".join(f'<div class="aline"><span class="ai">{ic}</span><span>{tx}</span></div>' for ic,tx in lines)
    st.markdown(f'<div class="analysis-card">{html}</div>', unsafe_allow_html=True)

def render_pills(recs):
    cls = {'g':'pill-g','y':'pill-y','s':'pill-s'}
    pills = "".join(f'<span class="pill {cls[s]}">{lb} <b>{pc}</b></span>' for s,lb,pc in recs)
    st.markdown(f'<div class="pill-wrap">{pills}</div>', unsafe_allow_html=True)

def render_team_card(name, p, side):
    sc = {'ofensivo':'tb-of','defensivo':'tb-df','equilibrado':'tb-eq'}[p['estilo']]
    bars = ""
    for lbl,val in [("Ataque",p['ataque']),("Defesa",p['defesa'])]:
        pct = val*10
        bc  = "pb-g" if val>=7 else "pb-y" if val>=5 else "pb-r"
        bars += f'<div class="pbar-row"><span class="pbar-lbl">{lbl}</span><div class="pbar-track"><div class="pbar-fill {bc}" style="width:{pct}%"></div></div><span class="pbar-pct">{val}/10</span></div>'
    stats = ""
    for lbl,k in [("BTTS","btts"),("O2.5","over25"),("O1.5","over15")]:
        v = p.get(k,0)
        c = "#4ade80" if v>=60 else "#fbbf24" if v>=45 else "#f87171"
        stats += f'<span class="tc-stat" style="color:{c}">{lbl} {v}%</span>'
    st.markdown(f'<div class="team-card"><div class="tc-hdr"><span class="tc-name">{side} {name}</span><span class="tc-badge {sc}">{p["estilo"]}</span></div>{bars}<div class="tc-stats">{stats}</div></div>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    for k,v in [('last_analise',None),('last_match',None),('selected_comp',None)]:
        if k not in st.session_state: st.session_state[k] = v

    an    = Analisador()
    comps = get_competitions()

    # TOP BAR
    api_ok  = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"
    d1 = "dot-g" if api_ok   else "dot-r"
    d2 = "dot-g" if odds_ok  else "dot-y"
    d3 = "dot-g" if EMAIL_USER else "dot-y"

    st.markdown(f"""
    <div class="top-bar">
        <span class="tb-icon">⚽</span>
        <div><div class="tb-title">Bet Analyzer</div><div class="tb-sub">H2H · Value Bet · Alertas</div></div>
        <div class="status-dots">
            <div class="dot {d1}" title="Football API"></div>
            <div class="dot {d2}" title="Odds API"></div>
            <div class="dot {d3}" title="Email"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not comps:
        st.error("❌ Configure FOOTBALL_DATA_API_KEY no .env"); return

    if st.session_state['selected_comp'] not in comps:
        st.session_state['selected_comp'] = list(comps.keys())[0]

    # SIDEBAR
    selected_markets = ['btts','over25','over15','under35','second_half_more']
    with st.sidebar:
        st.markdown('<div class="sb-title">⚙ Mercados</div>', unsafe_allow_html=True)
        default_d = ['BTTS','Over 2.5','Over 1.5','Under 3.5','2º Tempo +']
        rev_map   = {v:k for k,v in MARKET_MAP.items()}
        sel_disp  = st.multiselect("Mercados", list(MARKET_MAP.values()), default=[m for m in default_d if m in MARKET_MAP.values()])
        selected_markets = [rev_map[m] for m in sel_disp]
        st.selectbox("Filtro",["Todos","🔥 Value Bet","🛡️ Baixo Risco (>70%)"])

        st.markdown('<div class="sb-title" style="margin-top:0.55rem">📋 Watchlist</div>', unsafe_allow_html=True)
        new_m = st.text_input("Adicionar", placeholder="Arsenal vs Chelsea", key="nmi")
        if st.button("＋ Adicionar") and new_m:
            an.watchlist.append(new_m); st.session_state.watchlist = an.watchlist; st.rerun()
        for i,mw in enumerate(an.watchlist):
            c1,c2 = st.columns([5,1])
            c1.markdown(f'<div class="wi">⚽ {mw}</div>', unsafe_allow_html=True)
            if c2.button("✕",key=f"r{i}"):
                an.watchlist.pop(i); st.session_state.watchlist = an.watchlist; st.rerun()
        if not an.watchlist:
            st.markdown('<div style="font-size:0.61rem;color:#1e3a5f">Lista vazia</div>', unsafe_allow_html=True)

        st.markdown('<div class="sb-title" style="margin-top:0.55rem">📧 Alertas</div>', unsafe_allow_html=True)
        email_to = st.text_input("Email", value="seu@email.com", key="em_sb")
        if st.button("Enviar Alertas"):
            for ms in an.watchlist:
                try:
                    h,a = ms.split(" vs ")
                    an.send_alert({'home_team':h,'away_team':a,'date':datetime.now()},{'prob_btts':65,'prob_over25':70},email_to)
                except Exception as e: st.error(f"{e}")

    # TABS
    tab1, tab2, tab3 = st.tabs(["🔍 Análise", "📊 Perfis", "📈 Histórico"])

    # ══ TAB 1 ════════════════════════════════════════════════
    with tab1:
        col_comp, col_match = st.columns([1,2])

        with col_comp:
            st.markdown('<span class="sec-label">Competição</span>', unsafe_allow_html=True)
            sel_comp = st.selectbox("comp", list(comps.keys()),
                                    index=list(comps.keys()).index(st.session_state['selected_comp']),
                                    key='comp_sel', label_visibility="collapsed")
            st.session_state['selected_comp'] = sel_comp

        comp_id = comps[sel_comp]

        with col_match:
            st.markdown('<span class="sec-label">Partida</span>', unsafe_allow_html=True)
            with st.spinner("Buscando…"):
                matches = get_matches(comp_id)
            opts = []
            for m in matches:
                if m["status"] in ["SCHEDULED","TIMED"]:
                    try:
                        dt = datetime.fromisoformat(m["utcDate"].replace("Z","+00:00"))
                        opts.append({"id":m["id"],"home_id":m["homeTeam"]["id"],"away_id":m["awayTeam"]["id"],
                                     "disp":f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} · {dt.strftime('%d/%m %H:%M')}",
                                     "home_team":m["homeTeam"]["name"],"away_team":m["awayTeam"]["name"],"date":dt})
                    except: continue

            sel_match = None
            if not opts:
                st.warning("⚠️ Nenhuma partida encontrada.")
            else:
                sel_str   = st.selectbox("partida",[o["disp"] for o in opts],key='match_sel',label_visibility="collapsed")
                sel_match = opts[[o["disp"] for o in opts].index(sel_str)]

        if sel_match:
            st.markdown("")
            if st.button("🚀 Analisar Partida", use_container_width=True):
                with st.spinner(f"Analisando {sel_match['home_team']} vs {sel_match['away_team']}…"):
                    try:
                        res = an.analisar(sel_match['home_team'],sel_match['away_team'],sel_comp,
                                          sel_match['home_id'],sel_match['away_id'],comp_id,selected_markets)
                        st.session_state['last_analise'] = res
                        st.session_state['last_match']   = sel_match
                    except Exception as e: st.error(f"Erro: {e}")

        if st.session_state['last_analise']:
            analise = st.session_state['last_analise']
            match   = st.session_state['last_match']

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            st.markdown(f"""
            <div class="match-banner">
                <div class="match-teams">
                    <div class="mh">🏠 {match['home_team']}</div>
                    <div class="mv">vs</div>
                    <div class="ma">🚩 {match['away_team']}</div>
                </div>
                <span class="match-date">📅 {match['date'].strftime('%d/%m · %H:%M')}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown('<span class="sec-label">Probabilidades</span>', unsafe_allow_html=True)
            render_metric_grid(analise, selected_markets)

            col_l, col_r = st.columns([3,2])

            with col_l:
                st.markdown('<span class="sec-label">Distribuição</span>', unsafe_allow_html=True)
                render_prob_bars(analise, selected_markets)

                h2h = analise['h2h']
                st.markdown(f"""
                <span class="sec-label">Head to Head</span>
                <div class="h2h-grid">
                    <div class="h2h-tile"><div class="hv">{h2h['btts_h2h']:.0f}%</div><div class="hl">BTTS H2H</div></div>
                    <div class="h2h-tile"><div class="hv">{h2h['over25_h2h']:.0f}%</div><div class="hl">Over 2.5 H2H</div></div>
                </div>""", unsafe_allow_html=True)

            with col_r:
                st.markdown('<span class="sec-label">Análise</span>', unsafe_allow_html=True)
                render_detail_card(analise['detail_lines'])
                st.markdown('<span class="sec-label">Recomendações</span>', unsafe_allow_html=True)
                if analise['recomendacoes']: render_pills(analise['recomendacoes'])
                else: st.info("Selecione mercados na sidebar.")

            with st.expander("💰 Calculadora de Value Bet"):
                if selected_markets:
                    n_cols = min(3, len(selected_markets))
                    vcols  = st.columns(n_cols)
                    for j,mkt in enumerate(selected_markets):
                        with vcols[j%n_cols]:
                            prob = analise.get(f'prob_{mkt}',0)
                            oj   = analise.get(f'odd_justa_{mkt}',1.5)
                            lbl  = MARKET_MAP.get(mkt,mkt)
                            or_  = st.number_input(lbl,min_value=1.01,value=float(oj),step=0.01,format="%.2f",key=f"vi_{mkt}")
                            ev   = calculate_value_bet(prob,or_) or 0
                            el   = "✅ VALUE" if ev>0.05 else "✓ Pequeno" if ev>0 else "✗ Sem Value"
                            ec   = "#4ade80" if ev>0.05 else "#fbbf24" if ev>0 else "#475569"
                            st.markdown(f'<div class="ev-box"><div class="ev-val" style="color:{ec}">{ev:.3f}</div><div class="ev-lbl" style="color:{ec}">{el}</div></div>', unsafe_allow_html=True)
                else: st.info("Selecione mercados.")

            lo = an.fetch_live_odds(match['home_team'], match['away_team'])
            if lo:
                with st.expander("📡 Odds ao Vivo"):
                    for bk in lo[:2]:
                        st.markdown(f'<span class="sec-label">{bk["title"]}</span>', unsafe_allow_html=True)
                        mt = next((m for m in bk.get('markets',[]) if m['key']=='totals'),None)
                        if mt:
                            ov = next((o['price'] for o in mt['outcomes'] if o.get('point')==2.5 and o.get('name')=='Over'),'N/A')
                            un = next((o['price'] for o in mt['outcomes'] if o.get('point')==2.5 and o.get('name')=='Under'),'N/A')
                            st.markdown(f'<div class="analysis-card" style="padding:0.52rem 0.75rem"><span style="font-size:0.69rem">Over 2.5 <b style="color:#60a5fa">@{ov}</b> &nbsp; Under 2.5 <b style="color:#60a5fa">@{un}</b></span></div>', unsafe_allow_html=True)

    # ══ TAB 2 ════════════════════════════════════════════════
    with tab2:
        if st.session_state['last_match']:
            m_  = st.session_state['last_match']
            cid = comps[st.session_state['selected_comp']]
            with st.spinner("Carregando perfis…"):
                hp = fetch_team_profile(m_['home_id'], cid)
                ap = fetch_team_profile(m_['away_id'], cid)
            c1,c2 = st.columns(2)
            with c1: render_team_card(m_['home_team'], hp, "🏠")
            with c2: render_team_card(m_['away_team'], ap, "🚩")

            cats = ['Ataque','Defesa','BTTS','Over 2.5','Over 1.5']
            hv   = [hp['ataque']*10,hp['defesa']*10,hp['btts'],hp['over25'],hp['over15']]
            av   = [ap['ataque']*10,ap['defesa']*10,ap['btts'],ap['over25'],ap['over15']]

            fig = go.Figure()
            for name,vals,color,fill in [
                (m_['home_team'],hv,'#3b82f6','rgba(59,130,246,0.12)'),
                (m_['away_team'],av,'#f97316','rgba(249,115,22,0.12)')
            ]:
                fig.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill='toself',name=name,line=dict(color=color,width=2),fillcolor=fill))
            fig.update_layout(
                polar=dict(bgcolor="#0b0e1a",
                           radialaxis=dict(visible=True,range=[0,100],gridcolor="#1a2035",tickfont=dict(size=8,color="#334155")),
                           angularaxis=dict(gridcolor="#1a2035",tickfont=dict(size=9,color="#64748b"))),
                paper_bgcolor="#060810",
                font=dict(family="Inter",color="#64748b"),
                legend=dict(font=dict(size=10,color="#64748b"),bgcolor="rgba(0,0,0,0)",orientation="h",x=0.5,xanchor="center",y=-0.08),
                margin=dict(l=20,r=20,t=20,b=40), height=280
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Analise uma partida primeiro.")

    # ══ TAB 3 ════════════════════════════════════════════════
    with tab3:
        if an.historico:
            df = pd.DataFrame(an.historico)
            df['Média'] = ((df['prob_btts']+df['prob_over25'])/2).round(1)
            st.dataframe(df.sort_values('data',ascending=False).rename(columns={'home':'Casa','away':'Fora','prob_btts':'BTTS %','prob_over25':'O2.5 %','data':'Data'}),use_container_width=True,hide_index=True)
            st.markdown("")
            pdf_b = an.gerar_pdf()
            st.download_button("⬇️ Exportar PDF",data=pdf_b,file_name="relatorio.pdf",mime="application/pdf")
        else:
            st.info("Histórico vazio. Analise uma partida para popular.")

if __name__ == "__main__":
    main()
