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

load_dotenv()

st.set_page_config(
    page_title="⚽ Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #f8fafc;
    color: #1e293b;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"] { display: none !important; }

.block-container { padding: 0.75rem 0.75rem 5rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    min-width: 265px !important; max-width: 265px !important;
}
[data-testid="stSidebar"] .block-container { padding: 0.85rem 0.75rem !important; }

/* TOP BAR */
.top-bar {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.65rem 1rem;
    background: rgba(255,255,255,0.97);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #e2e8f0;
    margin: -0.75rem -0.75rem 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.tb-icon { font-size: 1.25rem; flex-shrink: 0; }
.tb-title { font-size: 0.95rem; font-weight: 700; color: #0f172a; letter-spacing:-0.02em; flex:1; }
.tb-sub { font-size: 0.58rem; color: #94a3b8; font-family:'JetBrains Mono',monospace; }
.status-dots { display:flex; gap:0.3rem; align-items:center; flex-shrink:0; }
.dot { width:7px; height:7px; border-radius:50%; }
.dot-g { background:#22c55e; box-shadow:0 0 6px #22c55e99; }
.dot-y { background:#f59e0b; }
.dot-r { background:#ef4444; }

/* CURRENCY CHIP */
.currency-chip {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.22rem 0.6rem;
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 999px; font-size: 0.68rem; font-weight: 700;
    color: #1d4ed8; font-family: 'JetBrains Mono', monospace;
}

/* LABELS */
.sec-label {
    font-size: 0.59rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.12em; color: #94a3b8;
    margin-bottom: 0.45rem; margin-top: 0.1rem; display: block;
}

/* MATCH BANNER */
.match-banner {
    background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
    border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 0.85rem 1rem; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}
.match-teams { flex:1; min-width:0; }
.match-teams .mh { font-size:0.92rem; font-weight:700; color:#0f172a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.match-teams .mv { font-size:0.58rem; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin:0.07rem 0; }
.match-teams .ma { font-size:0.88rem; font-weight:600; color:#475569; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.match-date { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#64748b; background:#fff; border:1px solid #e2e8f0; border-radius:6px; padding:0.28rem 0.55rem; white-space:nowrap; flex-shrink:0; box-shadow:0 1px 2px rgba(0,0,0,0.04); }

/* METRIC GRID */
.metric-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.45rem; margin-bottom:0.75rem; }
@media(max-width:480px){ .metric-grid{ grid-template-columns:repeat(2,1fr); } }
.metric-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:10px;
    padding:0.62rem 0.5rem; text-align:center; position:relative; overflow:hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.metric-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:10px 10px 0 0; }
.mc-g::before { background: linear-gradient(90deg,#16a34a,#4ade80); }
.mc-y::before { background: linear-gradient(90deg,#d97706,#fbbf24); }
.mc-r::before { background: linear-gradient(90deg,#dc2626,#f87171); }
.metric-card .mv { font-family:'JetBrains Mono',monospace; font-size:1.45rem; font-weight:700; line-height:1; letter-spacing:-0.03em; }
.mc-g .mv { color:#16a34a; } .mc-y .mv { color:#d97706; } .mc-r .mv { color:#dc2626; }
.metric-card .ml { font-size:0.57rem; font-weight:600; color:#94a3b8; text-transform:uppercase; letter-spacing:0.07em; margin-top:0.17rem; }
.metric-card .mo { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#cbd5e1; margin-top:0.1rem; }

/* PROB BARS */
.pbar-wrap { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:0.68rem 0.85rem; margin-bottom:0.75rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.pbar-row { display:flex; align-items:center; gap:0.52rem; margin-bottom:0.5rem; }
.pbar-row:last-child { margin-bottom:0; }
.pbar-lbl { font-size:0.63rem; color:#64748b; width:72px; flex-shrink:0; font-weight:500; }
.pbar-track { flex:1; height:6px; background:#f1f5f9; border-radius:3px; overflow:hidden; }
.pbar-fill { height:100%; border-radius:3px; }
.pb-g { background: linear-gradient(90deg,#16a34a,#4ade80); }
.pb-y { background: linear-gradient(90deg,#d97706,#fbbf24); }
.pb-r { background: linear-gradient(90deg,#dc2626,#f87171); }
.pbar-pct { font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#475569; width:30px; text-align:right; flex-shrink:0; }

/* ANALYSIS CARD */
.analysis-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:0.68rem 0.85rem; margin-bottom:0.75rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.aline { display:flex; gap:0.48rem; align-items:flex-start; padding:0.32rem 0; border-bottom:1px solid #f8fafc; font-size:0.7rem; color:#475569; line-height:1.45; }
.aline:last-child { border-bottom:none; padding-bottom:0; }
.aline .ai { flex-shrink:0; font-size:0.75rem; line-height:1.45; }

/* H2H */
.h2h-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.45rem; margin-bottom:0.75rem; }
.h2h-tile { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:0.6rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.h2h-tile .hv { font-family:'JetBrains Mono',monospace; font-size:1.18rem; font-weight:700; color:#2563eb; }
.h2h-tile .hl { font-size:0.58rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.06em; margin-top:0.1rem; }

/* PILLS */
.pill-wrap { display:flex; flex-wrap:wrap; gap:0.32rem; margin-bottom:0.75rem; }
.pill { display:inline-flex; align-items:center; gap:0.28rem; padding:0.28rem 0.62rem; border-radius:999px; font-size:0.64rem; font-weight:600; line-height:1; }
.pill-g { background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; }
.pill-y { background:#fef9c3; color:#a16207; border:1px solid #fde68a; }
.pill-s { background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0; }

/* TEAM CARD */
.team-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:0.8rem; margin-bottom:0.65rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.tc-hdr { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.62rem; }
.tc-name { font-size:0.82rem; font-weight:700; color:#0f172a; }
.tc-badge { font-size:0.55rem; font-weight:700; padding:0.18rem 0.5rem; border-radius:999px; text-transform:uppercase; letter-spacing:0.07em; }
.tb-of { background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe; }
.tb-df { background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0; }
.tb-eq { background:#f5f3ff; color:#7c3aed; border:1px solid #ddd6fe; }
.tc-stats { display:flex; gap:0.5rem; margin-top:0.52rem; padding-top:0.44rem; border-top:1px solid #f1f5f9; flex-wrap:wrap; }
.tc-stat { font-size:0.61rem; font-weight:600; }

/* EV BOX */
.ev-box { text-align:center; margin-top:0.4rem; padding:0.35rem; background:#f8fafc; border-radius:7px; border:1px solid #e2e8f0; }
.ev-val { font-family:'JetBrains Mono',monospace; font-size:1.08rem; font-weight:700; }
.ev-lbl { font-size:0.58rem; margin-top:0.1rem; color:#94a3b8; }

/* HIST CARDS */
.hist-card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:0.68rem 0.88rem; display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.45rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.hist-card-left { flex:1; min-width:0; }
.hist-match { font-size:0.8rem; font-weight:700; color:#0f172a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.hist-date { font-size:0.6rem; color:#94a3b8; font-family:'JetBrains Mono',monospace; margin-top:0.12rem; }
.hist-right { display:flex; flex-direction:column; align-items:flex-end; gap:0.28rem; flex-shrink:0; }
.hist-market { font-size:0.63rem; font-weight:700; padding:0.23rem 0.58rem; border-radius:999px; }
.hm-g { background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; }
.hm-y { background:#fef9c3; color:#a16207; border:1px solid #fde68a; }
.hm-r { background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0; }
.hist-prob { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#94a3b8; }
.hist-pills { display:flex; flex-wrap:wrap; gap:0.22rem; margin-top:0.3rem; }
.hist-mini-pill { font-size:0.56rem; padding:0.15rem 0.38rem; border-radius:999px; font-weight:600; }

/* DIVIDER */
.divider { height:1px; background:#e2e8f0; margin:0.75rem 0; border:none; }

/* SIDEBAR */
.sb-title { font-size:0.57rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#94a3b8; padding:0.38rem 0 0.3rem; margin-bottom:0.35rem; border-bottom:1px solid #f1f5f9; }
.wi { display:flex; align-items:center; padding:0.3rem 0.48rem; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; margin-bottom:0.25rem; font-size:0.65rem; color:#64748b; gap:0.32rem; }

/* STREAMLIT OVERRIDES */
.stTabs [data-baseweb="tab-list"] { background:#f1f5f9 !important; border:1px solid #e2e8f0 !important; border-radius:9px; padding:3px; gap:2px; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#94a3b8 !important; border-radius:7px !important; font-size:0.72rem !important; font-weight:600 !important; padding:0.38rem 0.72rem !important; }
.stTabs [aria-selected="true"] { background:#ffffff !important; color:#2563eb !important; box-shadow:0 1px 3px rgba(0,0,0,0.08) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:0.8rem !important; }

.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
    font-size:0.61rem !important; font-weight:600 !important; text-transform:uppercase !important;
    letter-spacing:0.09em !important; color:#94a3b8 !important;
}
[data-baseweb="select"] > div:first-child, [data-baseweb="base-input"] {
    background:#ffffff !important; border:1px solid #e2e8f0 !important;
    border-radius:8px !important; font-size:0.76rem !important; color:#1e293b !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color:#fff !important; border:none !important; border-radius:9px !important;
    font-size:0.78rem !important; font-weight:700 !important; padding:0.6rem 1.3rem !important;
    width:100% !important; transition:opacity 0.15s, transform 0.1s !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.28) !important;
}
.stButton > button:hover { opacity:0.9 !important; transform:translateY(-1px) !important; }
.stDownloadButton > button {
    background:#f0fdf4 !important; color:#15803d !important;
    border:1px solid #bbf7d0 !important; border-radius:8px !important;
    font-size:0.71rem !important; font-weight:600 !important;
}
div[data-testid="stExpander"] { background:#fff !important; border:1px solid #e2e8f0 !important; border-radius:9px !important; box-shadow:0 1px 3px rgba(0,0,0,0.04) !important; }
div[data-testid="stExpander"] summary { font-size:0.72rem !important; color:#64748b !important; }
.stDataFrame { font-size:0.68rem !important; }
.stAlert { font-size:0.72rem !important; border-radius:8px !important; }
.stNumberInput input { background:#fff !important; border:1px solid #e2e8f0 !important; color:#1e293b !important; border-radius:7px !important; font-family:'JetBrains Mono',monospace !important; font-size:0.76rem !important; }
.stTextInput input { background:#fff !important; border:1px solid #e2e8f0 !important; color:#1e293b !important; border-radius:7px !important; font-size:0.76rem !important; }
.stMultiSelect [data-baseweb="tag"] { background:#dbeafe !important; color:#1d4ed8 !important; border-radius:4px !important; font-size:0.64rem !important; }
.stProgress > div > div > div { border-radius:3px !important; }

::-webkit-scrollbar { width:3px; height:3px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#e2e8f0; border-radius:2px; }

@media(max-width:640px){
    .block-container { padding:0.5rem 0.5rem 4.5rem !important; }
    .top-bar { margin:-0.5rem -0.5rem 0.75rem; }
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

# Moedas disponíveis
CURRENCIES = {
    'AOA': {'symbol': 'Kz', 'flag': '🇦🇴', 'name': 'Kwanza'},
    'EUR': {'symbol': '€',  'flag': '🇪🇺', 'name': 'Euro'},
    'BRL': {'symbol': 'R$', 'flag': '🇧🇷', 'name': 'Real'},
    'USD': {'symbol': '$',  'flag': '🇺🇸', 'name': 'Dólar'},
}

# ── UTILS ─────────────────────────────────────────────────────────────────────
def fmt_money(value, currency_key):
    c = CURRENCIES.get(currency_key, CURRENCIES['EUR'])
    return f"{c['symbol']}{value:,.2f}"

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
        if hs=='ofensivo' and as_=='ofensivo':     aj.update({'btts':8,'over25':12,'over15':5,'under35':-10,'under25':-8,'second_half_more':5})
        elif hs=='defensivo' and as_=='defensivo': aj.update({'btts':-10,'over25':-15,'over15':-5,'under35':12,'under25':10,'second_half_more':-5})
        elif 'ofensivo' in [hs,as_]:              aj.update({'btts':3,'over25':2,'over15':2,'under35':-3,'under25':-2,'second_half_more':3})
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
            'btts':             calc((hp['btts']+ap['btts'])/2,                          'btts',  15, 85, (h2h['btts_h2h']-50)/10),
            'over25':           calc((hp['over25']+ap['over25'])/2,                       'over25',20, 80, (h2h['over25_h2h']-50)/10),
            'over15':           calc((hp['over15']+ap['over15'])/2,                       'over15',40, 95),
            'under35':          calc((hp['under35']+ap['under35'])/2,                     'under35',30, 90),
            'under25':          calc((hp['under25']+ap['under25'])/2,                     'under25',25, 85),
            'second_half_more': calc((hp['second_half_more']+ap['second_half_more'])/2,   'second_half_more',20,80)
        }

        res = {f'prob_{k}': round(v,1) for k,v in probs.items()}
        res.update({f'odd_justa_{k}': round(100/v,2) for k,v in probs.items()})
        res['h2h']           = h2h
        res['home_profile']  = hp
        res['away_profile']  = ap
        res['detail_lines']  = self._lines(ht, at, hp, ap, h2h)
        res['recomendacoes'] = self._recs(probs, markets)

        self.historico.append({
            'home': ht, 'away': at,
            'prob_btts': res['prob_btts'], 'prob_over25': res['prob_over25'],
            'mercado_escolhido': markets[0] if markets else '',
            'mercados_todos': markets,
            'probs': {k: round(v,1) for k,v in probs.items()},
            'data': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
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

    def gerar_pdf(self, currency_key='EUR'):
        c = CURRENCIES.get(currency_key, CURRENCIES['EUR'])
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial","B",size=12)
        pdf.cell(200,9,f"Relatorio Bet Analyzer ({c['name']})",ln=1,align='C'); pdf.ln(5)
        pdf.set_font("Arial",size=9)
        pdf.cell(200,6,f"Total de apostas: {len(self.historico)}",ln=1); pdf.ln(3)
        MMAP = {"btts":"BTTS","over25":"Over 2.5","over15":"Over 1.5","under35":"Under 3.5","under25":"Under 2.5","second_half_more":"2o Tempo+"}
        for a in list(reversed(self.historico))[-20:]:
            mkey   = a.get('mercado_escolhido','')
            mlabel = MMAP.get(mkey, mkey.upper())
            odd_ap = a.get('odd_apostada',0)
            ev     = a.get('ev',0)
            stake  = a.get('stake',0)
            prob_m = a.get('probs',{}).get(mkey, a.get('prob_btts',0))
            pdf.set_font("Arial","B",size=9)
            pdf.cell(200,6,f"{a['home']} vs {a['away']}",ln=1)
            pdf.set_font("Arial",size=8)
            stake_str = f"{c['symbol']}{stake:.2f}" if stake else "-"
            pdf.cell(200,5,f"  {a['data']}  |  {mlabel}  |  Prob: {prob_m}%  |  Odd: {odd_ap:.2f}  |  Stake: {stake_str}  |  EV: {ev:+.3f}",ln=1)
            pdf.ln(2)
        return pdf.output(dest='S')

# ── RENDER HELPERS ────────────────────────────────────────────────────────────
def render_metric_grid(analise, markets):
    tiles = ""
    for m in markets:
        prob = analise.get(f'prob_{m}',0)
        odd  = analise.get(f'odd_justa_{m}',0)
        c    = mc_cls(prob, THRESHOLDS.get(m,60))
        lbl  = MARKET_MAP.get(m,m)
        tiles += f'<div class="metric-card {c}"><div class="mv">{prob:.0f}<span style="font-size:0.52em;font-weight:400;color:#cbd5e1">%</span></div><div class="ml">{lbl}</div><div class="mo">@ {odd}</div></div>'
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
        c = "#16a34a" if v>=60 else "#d97706" if v>=45 else "#dc2626"
        stats += f'<span class="tc-stat" style="color:{c}">{lbl} {v}%</span>'
    st.markdown(f'<div class="team-card"><div class="tc-hdr"><span class="tc-name">{side} {name}</span><span class="tc-badge {sc}">{p["estilo"]}</span></div>{bars}<div class="tc-stats">{stats}</div></div>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    for k,v in [('last_analise',None),('last_match',None),('selected_comp',None),('currency','EUR')]:
        if k not in st.session_state: st.session_state[k] = v

    an    = Analisador()
    comps = get_competitions()
    curr  = st.session_state['currency']
    c_info = CURRENCIES.get(curr, CURRENCIES['EUR'])

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    api_ok  = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"
    d1 = "dot-g" if api_ok   else "dot-r"
    d2 = "dot-g" if odds_ok  else "dot-y"
    d3 = "dot-g" if EMAIL_USER else "dot-y"

    st.markdown(f"""
    <div class="top-bar">
        <span class="tb-icon">⚽</span>
        <div style="flex:1">
            <div class="tb-title">Bet Analyzer</div>
            <div class="tb-sub">H2H · Value Bet · Alertas</div>
        </div>
        <span class="currency-chip">{c_info['flag']} {curr} {c_info['symbol']}</span>
        <div class="status-dots" style="margin-left:0.5rem">
            <div class="dot {d1}" title="Football API"></div>
            <div class="dot {d2}" title="Odds API"></div>
            <div class="dot {d3}" title="Email"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not comps:
        st.error("❌ Configure FOOTBALL_DATA_API_KEY no .env"); return

    if st.session_state['selected_comp'] not in comps:
        st.session_state['selected_comp'] = list(comps.keys())[0]

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    selected_markets = ['btts','over25','over15','under35','second_half_more']
    with st.sidebar:
        # ── Moeda ─────────────────────────────────────────────────────────────
        st.markdown('<div class="sb-title">💱 Moeda</div>', unsafe_allow_html=True)
        currency_opts = [f"{v['flag']} {k} — {v['name']}" for k, v in CURRENCIES.items()]
        curr_keys     = list(CURRENCIES.keys())
        curr_idx      = curr_keys.index(curr) if curr in curr_keys else 0
        sel_currency  = st.selectbox("Moeda", currency_opts, index=curr_idx, key="currency_sel", label_visibility="collapsed")
        new_curr      = curr_keys[currency_opts.index(sel_currency)]
        if new_curr != st.session_state['currency']:
            st.session_state['currency'] = new_curr
            st.rerun()

        # ── Mercados ──────────────────────────────────────────────────────────
        st.markdown('<div class="sb-title" style="margin-top:0.6rem">⚙ Mercados</div>', unsafe_allow_html=True)
        default_d = ['BTTS','Over 2.5','Over 1.5','Under 3.5','2º Tempo +']
        rev_map   = {v:k for k,v in MARKET_MAP.items()}
        sel_disp  = st.multiselect("Mercados", list(MARKET_MAP.values()), default=[m for m in default_d if m in MARKET_MAP.values()])
        selected_markets = [rev_map[m] for m in sel_disp]
        st.selectbox("Filtro",["Todos","🔥 Value Bet","🛡️ Baixo Risco (>70%)"])

        # ── Watchlist ─────────────────────────────────────────────────────────
        st.markdown('<div class="sb-title" style="margin-top:0.6rem">📋 Watchlist</div>', unsafe_allow_html=True)
        new_m = st.text_input("Adicionar", placeholder="Arsenal vs Chelsea", key="nmi")
        if st.button("＋ Adicionar") and new_m:
            an.watchlist.append(new_m); st.session_state.watchlist = an.watchlist; st.rerun()
        for i,mw in enumerate(an.watchlist):
            c1,c2 = st.columns([5,1])
            c1.markdown(f'<div class="wi">⚽ {mw}</div>', unsafe_allow_html=True)
            if c2.button("✕",key=f"r{i}"):
                an.watchlist.pop(i); st.session_state.watchlist = an.watchlist; st.rerun()
        if not an.watchlist:
            st.markdown('<div style="font-size:0.62rem;color:#94a3b8;padding:0.2rem 0">Lista vazia</div>', unsafe_allow_html=True)

        # ── Alertas ───────────────────────────────────────────────────────────
        st.markdown('<div class="sb-title" style="margin-top:0.6rem">📧 Alertas</div>', unsafe_allow_html=True)
        email_to = st.text_input("Email", value="seu@email.com", key="em_sb")
        if st.button("Enviar Alertas"):
            for ms in an.watchlist:
                try:
                    h,a = ms.split(" vs ")
                    an.send_alert({'home_team':h,'away_team':a,'date':datetime.now()},{'prob_btts':65,'prob_over25':70},email_to)
                except Exception as e: st.error(f"{e}")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔍 Análise", "📊 Perfis", "📈 Histórico"])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — ANÁLISE
    # ══════════════════════════════════════════════════════════
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
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ── Seletor de mercado + aposta ───────────────────────────────────
            st.markdown('<span class="sec-label">Mercado desta Aposta</span>', unsafe_allow_html=True)
            mc1, mc2, mc3 = st.columns([2,1,1])
            with mc1:
                mercado_jogo_disp = st.selectbox("Mercado principal", options=list(MARKET_MAP.values()),
                                                  key='mercado_jogo_sel', label_visibility="collapsed")
                mercado_jogo = {v:k for k,v in MARKET_MAP.items()}[mercado_jogo_disp]
            with mc2:
                odd_apostada = st.number_input("Odd apostada", min_value=1.01, value=2.00, step=0.05, format="%.2f", key="odd_input")
            with mc3:
                stake = st.number_input(f"Stake ({c_info['symbol']})", min_value=0.0, value=10.0, step=1.0, format="%.2f", key="stake_input")

            # Preview EV em tempo real (se já houver análise anterior)
            if st.session_state.get('last_analise'):
                prob_prev = st.session_state['last_analise'].get(f'prob_{mercado_jogo}', 0)
                ev_prev   = calculate_value_bet(prob_prev, odd_apostada) or 0
                retorno   = stake * odd_apostada
                lucro     = retorno - stake
                ev_c = "#16a34a" if ev_prev > 0.05 else "#d97706" if ev_prev > 0 else "#dc2626"
                st.markdown(f"""
                <div style="display:flex;gap:0.45rem;margin-top:0.35rem;flex-wrap:wrap">
                    <div class="ev-box" style="flex:1;min-width:75px">
                        <div class="ev-val" style="color:{ev_c}">{ev_prev:+.3f}</div>
                        <div class="ev-lbl">Expected Value</div>
                    </div>
                    <div class="ev-box" style="flex:1;min-width:75px">
                        <div class="ev-val" style="color:#2563eb">{prob_prev:.0f}%</div>
                        <div class="ev-lbl">Prob. Modelo</div>
                    </div>
                    <div class="ev-box" style="flex:1;min-width:75px">
                        <div class="ev-val" style="color:#7c3aed">{fmt_money(retorno, curr)}</div>
                        <div class="ev-lbl">Retorno</div>
                    </div>
                    <div class="ev-box" style="flex:1;min-width:75px">
                        <div class="ev-val" style="color:{'#16a34a' if lucro>=0 else '#dc2626'}">{fmt_money(lucro, curr)}</div>
                        <div class="ev-lbl">Lucro</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("")
            if st.button("🚀 Analisar Partida", use_container_width=True):
                with st.spinner(f"Analisando {sel_match['home_team']} vs {sel_match['away_team']}…"):
                    try:
                        markets_to_use = list(set(selected_markets + [mercado_jogo]))
                        res = an.analisar(sel_match['home_team'],sel_match['away_team'],sel_comp,
                                          sel_match['home_id'],sel_match['away_id'],comp_id,markets_to_use)
                        res['mercado_escolhido'] = mercado_jogo
                        res['odd_apostada']      = odd_apostada
                        res['stake']             = stake
                        res['currency']          = curr
                        if an.historico:
                            an.historico[-1]['mercado_escolhido'] = mercado_jogo
                            an.historico[-1]['odd_apostada']      = odd_apostada
                            an.historico[-1]['stake']             = stake
                            an.historico[-1]['currency']          = curr
                            an.historico[-1]['ev'] = round(calculate_value_bet(
                                an.historico[-1]['probs'].get(mercado_jogo, 50), odd_apostada) or 0, 3)
                            st.session_state.historico = an.historico
                        st.session_state['last_analise'] = res
                        st.session_state['last_match']   = sel_match
                    except Exception as e: st.error(f"Erro: {e}")

        # ── Resultados ────────────────────────────────────────────────────────
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
                            ec   = "#16a34a" if ev>0.05 else "#d97706" if ev>0 else "#94a3b8"
                            st.markdown(f'<div class="ev-box"><div class="ev-val" style="color:{ec}">{ev:+.3f}</div><div class="ev-lbl">{el}</div></div>', unsafe_allow_html=True)
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
                            st.markdown(f'<div class="analysis-card" style="padding:0.52rem 0.75rem"><span style="font-size:0.7rem">Over 2.5 <b style="color:#2563eb">@{ov}</b> &nbsp; Under 2.5 <b style="color:#2563eb">@{un}</b></span></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 2 — PERFIS
    # ══════════════════════════════════════════════════════════
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
                (m_['home_team'],hv,'#2563eb','rgba(37,99,235,0.10)'),
                (m_['away_team'],av,'#ea580c','rgba(234,88,12,0.10)')
            ]:
                fig.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill='toself',name=name,
                                               line=dict(color=color,width=2),fillcolor=fill))
            fig.update_layout(
                polar=dict(bgcolor="#ffffff",
                           radialaxis=dict(visible=True,range=[0,100],gridcolor="#e2e8f0",tickfont=dict(size=8,color="#94a3b8")),
                           angularaxis=dict(gridcolor="#e2e8f0",tickfont=dict(size=9,color="#64748b"))),
                paper_bgcolor="#f8fafc",
                font=dict(family="Inter",color="#64748b"),
                legend=dict(font=dict(size=10,color="#475569"),bgcolor="rgba(0,0,0,0)",orientation="h",x=0.5,xanchor="center",y=-0.08),
                margin=dict(l=20,r=20,t=20,b=40), height=290
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Analise uma partida primeiro.")

    # ══════════════════════════════════════════════════════════
    # TAB 3 — HISTÓRICO
    # ══════════════════════════════════════════════════════════
    with tab3:
        if an.historico:
            hist_sorted = list(reversed(an.historico))

            # Filtros
            fa, fb, fc = st.columns([2,2,1])
            with fa:
                filtro_mercado = st.selectbox("Filtrar mercado",["Todos"]+list(MARKET_MAP.values()),
                                               key="hist_fm",label_visibility="collapsed")
            with fb:
                filtro_ev = st.selectbox("Filtrar EV",
                    ["Todos","✅ Com Value (EV > 0)","🔥 EV Forte (> 0.05)","✗ Sem Value"],
                    key="hist_fev",label_visibility="collapsed")
            with fc:
                if st.button("🗑 Limpar",key="hist_clear"):
                    st.session_state.historico = []; an.historico.clear(); st.rerun()

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            icons_m  = {'btts':'🎯','over25':'⚽','over15':'⚽','under35':'🛡️','under25':'🛡️','second_half_more':'⏱️'}
            rev_map_h = {v:k for k,v in MARKET_MAP.items()}

            filtered = []
            for entry in hist_sorted:
                mkey = entry.get('mercado_escolhido','')
                ev   = entry.get('ev', 0)
                if filtro_mercado != "Todos" and mkey != rev_map_h.get(filtro_mercado,mkey): continue
                if filtro_ev == "✅ Com Value (EV > 0)" and ev <= 0: continue
                if filtro_ev == "🔥 EV Forte (> 0.05)" and ev <= 0.05: continue
                if filtro_ev == "✗ Sem Value" and ev > 0: continue
                filtered.append(entry)

            if not filtered:
                st.info("Nenhuma aposta encontrada com esses filtros.")
            else:
                total     = len(filtered)
                com_value = sum(1 for e in filtered if e.get('ev',0) > 0)
                ev_medio  = round(sum(e.get('ev',0) for e in filtered)/total,3) if total else 0
                stake_tot = sum(e.get('stake',0) for e in filtered)

                sm1,sm2,sm3,sm4 = st.columns(4)
                for col,lbl,val,c in [
                    (sm1,"APOSTAS",str(total),"#2563eb"),
                    (sm2,"COM VALUE",f"{com_value}/{total}","#16a34a"),
                    (sm3,"EV MÉDIO",f"{ev_medio:+.3f}","#16a34a" if ev_medio>0 else "#dc2626"),
                    (sm4,"STAKE",fmt_money(stake_tot,curr),"#7c3aed"),
                ]:
                    col.markdown(f"""
                    <div class="metric-card" style="margin-bottom:0.65rem">
                        <div class="mv" style="color:{c};font-size:1.1rem">{val}</div>
                        <div class="ml">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

                for entry in filtered:
                    mkey    = entry.get('mercado_escolhido','btts')
                    mlabel  = MARKET_MAP.get(mkey, mkey)
                    micon   = icons_m.get(mkey,'🎯')
                    ev      = entry.get('ev', 0)
                    odd_ap  = entry.get('odd_apostada', 0)
                    stake_e = entry.get('stake', 0)
                    entry_curr = entry.get('currency', curr)
                    retorno = stake_e * odd_ap if odd_ap else 0
                    lucro   = retorno - stake_e
                    probs   = entry.get('probs', {})
                    prob_m  = probs.get(mkey, entry.get('prob_btts',0))

                    if ev > 0.05:  ev_cls,ev_c = "hm-g","#16a34a"
                    elif ev > 0:   ev_cls,ev_c = "hm-y","#d97706"
                    else:          ev_cls,ev_c = "hm-r","#dc2626"

                    mini_pills = ""
                    for k,v in probs.items():
                        if k == mkey: continue
                        t  = THRESHOLDS.get(k,60)
                        pc = "pill-g" if v>=t else "pill-y" if v>=t-10 else "pill-s"
                        mini_pills += f'<span class="hist-mini-pill {pc}">{MARKET_MAP.get(k,k)} {v:.0f}%</span>'

                    stake_html  = f'<span style="font-size:0.62rem;color:#7c3aed;font-family:JetBrains Mono,monospace">{fmt_money(stake_e, entry_curr)}</span>' if stake_e else ''
                    odd_html    = f'<span style="font-size:0.62rem;color:#2563eb;font-family:JetBrains Mono,monospace">@ {odd_ap:.2f}</span>' if odd_ap else ''
                    lucro_c     = "#16a34a" if lucro >= 0 else "#dc2626"
                    lucro_html  = f'<span style="font-size:0.62rem;color:{lucro_c};font-family:JetBrains Mono,monospace">{fmt_money(lucro, entry_curr)}</span>' if odd_ap else ''

                    st.markdown(f"""
                    <div class="hist-card">
                        <div class="hist-card-left">
                            <div class="hist-match">🏠 {entry['home']} <span style="color:#94a3b8;font-weight:400">vs</span> 🚩 {entry['away']}</div>
                            <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.22rem;flex-wrap:wrap">
                                <span class="hist-date">{entry['data']}</span>
                                {odd_html}{stake_html}{lucro_html}
                            </div>
                            <div class="hist-pills">{mini_pills}</div>
                        </div>
                        <div class="hist-right">
                            <span class="hist-market {ev_cls}">{micon} {mlabel}</span>
                            <span class="hist-prob">{prob_m:.0f}% prob</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;font-weight:700;color:{ev_c}">EV {ev:+.3f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                pdf_b = an.gerar_pdf(curr)
                st.download_button("⬇️ Exportar PDF", data=pdf_b, file_name="relatorio_bets.pdf", mime="application/pdf")
        else:
            st.info("Histórico vazio. Analise uma partida para popular.")

if __name__ == "__main__":
    main()
