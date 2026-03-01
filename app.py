
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText as MimeText
from email.mime.multipart import MIMEMultipart as MimeMultipart
import io
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO INICIAL ---
load_dotenv()

st.set_page_config(
    page_title="⚽ Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

# ── DESIGN SYSTEM ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: #0a0d14;
    color: #e2e8f0;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0f1420 !important;
    border-right: 1px solid #1e2535 !important;
}
[data-testid="stSidebar"] .block-container { padding: 1rem !important; }
[data-testid="stSidebarNav"] { display: none; }

/* ── TYPOGRAPHY ── */
h1, h2, h3 { font-weight: 600; letter-spacing: -0.02em; }

/* ── APP HEADER ── */
.app-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid #1e2d45;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.app-header .logo { font-size: 1.5rem; }
.app-header h1 { font-size: 1.1rem; color: #f1f5f9; margin: 0; }
.app-header .subtitle { font-size: 0.72rem; color: #64748b; font-family: 'DM Mono', monospace; }
.api-badge {
    margin-left: auto;
    display: flex;
    gap: 0.4rem;
    align-items: center;
}
.badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 0.25rem 0.55rem;
    border-radius: 4px;
    font-weight: 500;
    letter-spacing: 0.03em;
}
.badge-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-yellow { background: #451a03; color: #fbbf24; border: 1px solid #78350f; }
.badge-red    { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }

/* ── CARDS ── */
.card {
    background: #111827;
    border: 1px solid #1e2535;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
}
.card-sm {
    background: #111827;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
}
.card-title {
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #475569;
    margin-bottom: 0.5rem;
}

/* ── METRIC TILES ── */
.metric-tile {
    background: #0f172a;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 0.65rem 0.75rem;
    text-align: center;
}
.metric-tile .val  { font-size: 1.4rem; font-weight: 600; line-height: 1.1; font-family: 'DM Mono', monospace; }
.metric-tile .lbl  { font-size: 0.63rem; color: #64748b; margin-top: 0.15rem; letter-spacing: 0.04em; text-transform: uppercase; }
.metric-tile .sub  { font-size: 0.68rem; color: #94a3b8; margin-top: 0.2rem; font-family: 'DM Mono', monospace; }
.metric-green .val { color: #4ade80; }
.metric-yellow .val { color: #fbbf24; }
.metric-red .val   { color: #f87171; }

/* ── PROB BARS ── */
.prob-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.45rem; }
.prob-label { font-size: 0.68rem; color: #94a3b8; width: 90px; flex-shrink: 0; }
.prob-bar-wrap { flex: 1; height: 6px; background: #1e2535; border-radius: 3px; overflow: hidden; }
.prob-bar { height: 100%; border-radius: 3px; }
.bar-green  { background: linear-gradient(90deg, #16a34a, #4ade80); }
.bar-yellow { background: linear-gradient(90deg, #d97706, #fbbf24); }
.bar-red    { background: linear-gradient(90deg, #b91c1c, #f87171); }
.prob-pct { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #e2e8f0; width: 34px; text-align: right; }

/* ── REC PILLS ── */
.rec-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.65rem;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 500;
    margin: 0.2rem 0.2rem 0.2rem 0;
    line-height: 1;
}
.rec-strong { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.rec-mid    { background: #1c1917; color: #fbbf24; border: 1px solid #78350f; }
.rec-low    { background: #1c1917; color: #94a3b8; border: 1px solid #374151; }

/* ── DETAIL LINES ── */
.detail-line {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid #1e2535;
    font-size: 0.73rem;
    color: #94a3b8;
    line-height: 1.4;
}
.detail-line:last-child { border-bottom: none; }
.detail-line .icon { flex-shrink: 0; font-size: 0.8rem; }

/* ── TEAM HEADER ── */
.team-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0.9rem;
    background: #0f172a;
    border: 1px solid #1e2535;
    border-radius: 8px;
    margin-bottom: 0.7rem;
}
.team-name { font-size: 0.85rem; font-weight: 600; color: #f1f5f9; }
.team-style {
    font-size: 0.6rem;
    padding: 0.18rem 0.5rem;
    border-radius: 999px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.style-of { background: #172554; color: #93c5fd; border: 1px solid #1e40af; }
.style-df { background: #1c1917; color: #a8a29e; border: 1px solid #44403c; }
.style-eq { background: #1a1a2e; color: #a78bfa; border: 1px solid #4c1d95; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1420 !important;
    border-radius: 8px;
    padding: 3px;
    gap: 2px;
    border: 1px solid #1e2535;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: #1e2d45 !important;
    color: #93c5fd !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 0.75rem !important; }

/* ── STREAMLIT OVERRIDES ── */
.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
    font-size: 0.72rem !important;
    color: #64748b !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #111827 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
    color: #e2e8f0 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stDownloadButton > button {
    background: #0f2a0f !important;
    color: #4ade80 !important;
    border: 1px solid #166534 !important;
    border-radius: 7px !important;
    font-size: 0.75rem !important;
}
.stExpander {
    background: #111827 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 8px !important;
}
.stExpander summary { font-size: 0.75rem !important; color: #94a3b8 !important; }
.stDataFrame { font-size: 0.72rem !important; }
.stSuccess, .stInfo, .stWarning, .stError {
    font-size: 0.73rem !important;
    border-radius: 6px !important;
    padding: 0.5rem 0.75rem !important;
}
.stProgress > div > div > div { border-radius: 3px !important; }

/* ── NUMBER INPUT ── */
.stNumberInput input {
    background: #0f172a !important;
    border: 1px solid #1e2535 !important;
    color: #e2e8f0 !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── SECTION TITLES ── */
.sec-title {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #475569;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e2535;
    margin-bottom: 0.65rem;
}

/* ── H2H ROW ── */
.h2h-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.4rem;
}
.h2h-item {
    flex: 1;
    background: #0f172a;
    border: 1px solid #1e2535;
    border-radius: 6px;
    padding: 0.4rem 0.6rem;
    text-align: center;
}
.h2h-item .h2h-val { font-family: 'DM Mono', monospace; font-size: 1rem; font-weight: 600; color: #93c5fd; }
.h2h-item .h2h-lbl { font-size: 0.6rem; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── WATCHLIST ── */
.watch-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.3rem 0.5rem;
    background: #0f172a;
    border: 1px solid #1e2535;
    border-radius: 5px;
    margin-bottom: 0.3rem;
    font-size: 0.7rem;
    color: #94a3b8;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0d14; }
::-webkit-scrollbar-thumb { background: #1e2535; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── VARIÁVEIS DE AMBIENTE ──────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY, "Accept": "application/json"}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS = "https://api.the-odds-api.com/v4"

# ── FUNÇÕES UTILITÁRIAS ────────────────────────────────────────────────────────
def calculate_implied_probability(odd):
    return round(100 / odd, 2) if odd and odd > 0 else None

def calculate_value_bet(real_prob, odd):
    if not odd or odd <= 0 or not real_prob:
        return None
    return round((odd * (real_prob / 100)) - 1, 3)

def get_total_goals(match):
    return (match['score']['fullTime'].get('home', 0) or 0) + (match['score']['fullTime'].get('away', 0) or 0)

def get_home_goals(match):
    return match['score']['fullTime'].get('home', 0) or 0

def get_away_goals(match):
    return match['score']['fullTime'].get('away', 0) or 0

def get_first_half_goals(match):
    return (match['score']['halfTime'].get('home', 0) or 0) + (match['score']['halfTime'].get('away', 0) or 0)

def get_second_half_goals(match):
    return get_total_goals(match) - get_first_half_goals(match)

def prob_color(p, t=60):
    if p >= t:      return "green"
    if p >= t - 10: return "yellow"
    return "red"

def prob_bar_class(p, t=60):
    if p >= t:      return "bar-green"
    if p >= t - 10: return "bar-yellow"
    return "bar-red"

def metric_class(p, t=60):
    if p >= t:      return "metric-green"
    if p >= t - 10: return "metric-yellow"
    return "metric-red"

# ── API ────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_football_data(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        url = f"{BASE_URL_FOOTBALL}/{endpoint}"
        response = requests.get(url, headers=HEADERS_FOOTBALL, timeout=15)
        if response.status_code == 429:
            st.error("❌ Rate limit atingido. Tente mais tarde.")
            return None
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_football_data("competitions")
    if data and "competitions" in data:
        top = ["Premier League","Primera Division","Serie A","Bundesliga","Ligue 1",
               "Primeira Liga","Eredivisie","Jupiler Pro League","Scottish Premiership",
               "UEFA Champions League","UEFA Europa League","UEFA Conference League"]
        return {c["name"]: c["id"] for c in data["competitions"]
                if c["name"] in top and c.get("currentSeason")}
    return {}

@st.cache_data(ttl=600)
def get_matches(competition_id):
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_football_data(f"competitions/{competition_id}/matches?dateFrom={today}&dateTo={next_week}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile_cached(team_id, comp_id):
    profile = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado',
               'over25': 50, 'btts': 50, 'over15': 70, 'under35': 70,
               'under25': 50, 'second_half_more': 50}
    try:
        standings_data = fetch_football_data(f"competitions/{comp_id}/standings")
        if standings_data and 'standings' in standings_data:
            for group in standings_data['standings']:
                for t in group['table']:
                    if t['team']['id'] == team_id:
                        p, gf, ga = t['playedGames'], t['goalsFor'], t['goalsAgainst']
                        if p > 0:
                            profile['ataque'] = min(10, max(1, round((gf/p/1.4)*7+1)))
                            profile['defesa']  = min(10, max(1, round((1.4/max(ga/p,0.1))*7+1)))
                        break

        matches_data = fetch_football_data(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if matches_data and 'matches' in matches_data:
            rm = matches_data['matches'][:10]
            if rm:
                n = len(rm)
                profile['over25']          = round(sum(1 for m in rm if get_total_goals(m) > 2.5)/n*100)
                profile['btts']            = round(sum(1 for m in rm if get_home_goals(m)>0 and get_away_goals(m)>0)/n*100)
                profile['over15']          = round(sum(1 for m in rm if get_total_goals(m) > 1.5)/n*100)
                profile['under35']         = round(sum(1 for m in rm if get_total_goals(m) < 3.5)/n*100)
                profile['under25']         = round(sum(1 for m in rm if get_total_goals(m) < 2.5)/n*100)
                profile['second_half_more']= round(sum(1 for m in rm if get_second_half_goals(m)>get_first_half_goals(m))/n*100)

        a, d = profile['ataque'], profile['defesa']
        profile['estilo'] = 'ofensivo' if a>=7 and d<=6 else 'defensivo' if d>=7 and a<=6 else 'equilibrado'
        return profile
    except Exception:
        return profile

# ── MOTOR DE ANÁLISE ──────────────────────────────────────────────────────────
class AnalisadorAutomatico:
    def __init__(self):
        if 'watchlist' not in st.session_state:          st.session_state.watchlist = []
        if 'historico_analises' not in st.session_state: st.session_state.historico_analises = []
        self.watchlist = st.session_state.watchlist
        self.historico_analises = st.session_state.historico_analises

    def save_historico(self, analise, home_team, away_team):
        self.historico_analises.append({
            'home': home_team, 'away': away_team,
            'prob_btts': analise['prob_btts'], 'prob_over25': analise['prob_over25'],
            'data': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        st.session_state.historico_analises = self.historico_analises

    @st.cache_data(ttl=3600)
    def fetch_h2h(_self, home_id, away_id, limit=5):
        try:
            home_matches = fetch_football_data(f"teams/{home_id}/matches?status=FINISHED&limit=20")
            h2h = []
            if home_matches and 'matches' in home_matches:
                for m in home_matches['matches']:
                    if m.get('awayTeam',{}).get('id')==away_id or m.get('homeTeam',{}).get('id')==away_id:
                        h2h.append(m)
                        if len(h2h) >= limit: break
            n = max(len(h2h), 1)
            return {
                'btts_h2h':   sum(1 for m in h2h if get_home_goals(m)>0 and get_away_goals(m)>0)/n*100,
                'over25_h2h': sum(1 for m in h2h if get_total_goals(m)>2.5)/n*100
            }
        except Exception:
            return {'btts_h2h': 50, 'over25_h2h': 50}

    def fetch_live_odds(self, home_team, away_team):
        try:
            if ODDS_API_KEY == "sua_chave_the_odds_api": return []
            url = f"{BASE_URL_ODDS}/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                for event in response.json():
                    if home_team.lower() in event['home_team'].lower() and away_team.lower() in event['away_team'].lower():
                        return event.get('bookmakers', [])
            return []
        except Exception:
            return []

    def calcular_ajustes_estilo(self, home, away):
        aj = {'btts':0,'over25':0,'over15':0,'under35':0,'under25':0,'second_half_more':0}
        hs, as_ = home['estilo'], away['estilo']
        if hs=='ofensivo' and as_=='ofensivo':
            aj.update({'btts':8,'over25':12,'over15':5,'under35':-10,'under25':-8,'second_half_more':5})
        elif hs=='defensivo' and as_=='defensivo':
            aj.update({'btts':-10,'over25':-15,'over15':-5,'under35':12,'under25':10,'second_half_more':-5})
        elif 'ofensivo' in [hs,as_]:
            aj.update({'btts':3,'over25':2,'over15':2,'under35':-3,'under25':-2,'second_half_more':3})
        if home['ataque']>=8 and away['defesa']<=5:
            for k in ['btts','over25','over15']: aj[k]+=5 if k=='btts' else 8 if k=='over25' else 4
            for k in ['under35','under25']: aj[k]-=6 if k=='under35' else 5
            aj['second_half_more']+=4
        if away['ataque']>=8 and home['defesa']<=5:
            for k in ['btts','over25','over15']: aj[k]+=5 if k=='btts' else 8 if k=='over25' else 4
            for k in ['under35','under25']: aj[k]-=6 if k=='under35' else 5
            aj['second_half_more']+=4
        return aj

    def calcular_ajustes_competicao(self, competition):
        aj = {'btts':0,'over25':0,'over15':0,'under35':0,'under25':0,'second_half_more':0}
        if 'Premier League' in competition:
            aj.update({'over25':5,'over15':3,'under35':-2,'under25':-1,'second_half_more':2})
        elif 'Serie A' in competition:
            aj.update({'btts':-3,'over25':-2,'over15':-1,'under35':4,'under25':3,'second_half_more':-2})
        elif 'Bundesliga' in competition:
            aj.update({'btts':5,'over25':8,'over15':5,'under35':-8,'under25':-7,'second_half_more':5})
        return aj

    def analisar_partida_automatica(self, home_team, away_team, competition, home_id, away_id, comp_id, selected_markets):
        hp  = fetch_team_profile_cached(home_id, comp_id)
        ap  = fetch_team_profile_cached(away_id, comp_id)
        h2h = self.fetch_h2h(home_id, away_id)
        aj  = self.calcular_ajustes_estilo(hp, ap)
        ajc = self.calcular_ajustes_competicao(competition)

        def calc(base, key, lo, hi):
            return min(hi, max(lo, base + aj[key] + ajc[key]))

        pb_base  = (hp['btts']+ap['btts'])/2
        po25_base= (hp['over25']+ap['over25'])/2
        po15_base= (hp['over15']+ap['over15'])/2
        pu35_base= (hp['under35']+ap['under35'])/2
        pu25_base= (hp['under25']+ap['under25'])/2
        ps2h_base= (hp['second_half_more']+ap['second_half_more'])/2

        h2b  = (h2h['btts_h2h']-50)/10
        h2o  = (h2h['over25_h2h']-50)/10

        prob_btts   = min(85,max(15, pb_base   + aj['btts']  +ajc['btts']  +h2b))
        prob_over25 = min(80,max(20, po25_base + aj['over25']+ajc['over25']+h2o))
        prob_over15 = min(95,max(40, calc(po15_base,'over15',40,95)))
        prob_under35= min(90,max(30, calc(pu35_base,'under35',30,90)))
        prob_under25= min(85,max(25, calc(pu25_base,'under25',25,85)))
        prob_s2h    = min(80,max(20, calc(ps2h_base,'second_half_more',20,80)))

        analise = {
            'prob_btts': round(prob_btts,1), 'prob_over25': round(prob_over25,1),
            'prob_over15': round(prob_over15,1), 'prob_under35': round(prob_under35,1),
            'prob_under25': round(prob_under25,1), 'prob_second_half_more': round(prob_s2h,1),
            'odd_justa_btts': round(100/prob_btts,2), 'odd_justa_over25': round(100/prob_over25,2),
            'odd_justa_over15': round(100/prob_over15,2), 'odd_justa_under35': round(100/prob_under35,2),
            'odd_justa_under25': round(100/prob_under25,2), 'odd_justa_second_half_more': round(100/prob_s2h,2),
            'h2h': h2h, 'home_profile': hp, 'away_profile': ap,
            'analise_detalhada': self._detail_lines(home_team, away_team, hp, ap, h2h),
            'recomendacao': self._recomend(prob_btts,prob_over25,prob_over15,prob_under35,prob_under25,prob_s2h,selected_markets)
        }
        self.save_historico(analise, home_team, away_team)
        return analise

    def _detail_lines(self, ht, at, hp, ap, h2h):
        def style_icon(s): return "⚡" if s=='ofensivo' else "🛡️" if s=='defensivo' else "⚖️"
        lines = [
            (style_icon(hp['estilo']), f"{ht}: {hp['estilo'].upper()} · Atq {hp['ataque']}/10 · Def {hp['defesa']}/10"),
            (style_icon(ap['estilo']), f"{at}: {ap['estilo'].upper()} · Atq {ap['ataque']}/10 · Def {ap['defesa']}/10"),
            ("🤝", f"H2H: BTTS {h2h['btts_h2h']:.0f}% · Over 2.5 {h2h['over25_h2h']:.0f}%"),
        ]
        if hp['estilo']=='ofensivo' and ap['estilo']=='ofensivo':
            lines.append(("⚔️", "Dois times ofensivos → Alta expectativa de gols"))
        elif hp['estilo']=='defensivo' and ap['estilo']=='defensivo':
            lines.append(("🔒", "Dois times defensivos → Jogo fechado esperado"))
        else:
            lines.append(("📊", "Estilos contrastantes → Jogo equilibrado"))
        if hp['ataque']>=8: lines.append(("✅", f"{ht} tem ataque muito forte"))
        if ap['ataque']>=8: lines.append(("✅", f"{at} tem ataque muito forte"))
        if hp['defesa']<=5: lines.append(("⚠️", f"{ht} tem defesa vulnerável"))
        if ap['defesa']<=5: lines.append(("⚠️", f"{at} tem defesa vulnerável"))
        return lines

    def _recomend(self, pb,po25,po15,pu35,pu25,ps2h,markets):
        recs = []
        checks = [
            ('btts',pb,'🎯','BTTS'),('over25',po25,'⚽','Over 2.5'),
            ('over15',po15,'⚽','Over 1.5'),('under35',pu35,'🛡️','Under 3.5'),
            ('under25',pu25,'🛡️','Under 2.5'),('second_half_more',ps2h,'⏱️','2ª Tempo')
        ]
        thresh = {'btts':60,'over25':60,'over15':80,'under35':70,'under25':60,'second_half_more':60}
        for key,prob,icon,label in checks:
            if key not in markets: continue
            t = thresh[key]
            if prob>=t:       recs.append(('strong', f"{icon} {label}", f"{prob:.0f}%"))
            elif prob>=t-10:  recs.append(('mid',    f"{icon} {label}", f"{prob:.0f}%"))
            else:             recs.append(('low',    f"{icon} {label}", f"{prob:.0f}%"))
        return recs

    def send_alert(self, match_info, analise, email_to):
        if not EMAIL_USER or not EMAIL_PASS:
            st.warning("Configure EMAIL_USER e EMAIL_PASS no .env.")
            return
        try:
            msg = MimeMultipart()
            msg['From'], msg['To'] = EMAIL_USER, email_to
            msg['Subject'] = f"⚽ {match_info['home_team']} vs {match_info['away_team']}"
            body = f"Partida: {match_info['home_team']} vs {match_info['away_team']}\n\n"
            for k in ['btts','over25','over15','under35','under25','second_half_more']:
                prob = analise.get(f'prob_{k}', 0)
                v = calculate_value_bet(prob, 2.0)
                if v and v>0.1: body += f"- {k.upper()}: {prob}% | EV: {v:.2f}\n"
            msg.attach(MimeText(body,'plain'))
            s = smtplib.SMTP('smtp.gmail.com',587); s.starttls()
            s.login(EMAIL_USER,EMAIL_PASS); s.sendmail(EMAIL_USER,email_to,msg.as_string()); s.quit()
            st.success("📧 Alerta enviado!")
        except Exception as e:
            st.error(f"Erro email: {e}")

    def gerar_relatorio_pdf(self, analises):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial",size=12)
        pdf.cell(200,10,"Relatório de Análises",ln=1,align='C'); pdf.ln(8)
        for a in analises[-10:]:
            pdf.cell(200,8,f"{a['home']} vs {a['away']}",ln=1)
            pdf.cell(200,8,f"BTTS: {a['prob_btts']}% | Over 2.5: {a['prob_over25']}%",ln=1)
            pdf.ln(4)
        return pdf.output(dest='S')

# ── HELPERS DE RENDER ──────────────────────────────────────────────────────────
MARKET_MAP = {
    'btts':'BTTS','over25':'Over 2.5','over15':'Over 1.5',
    'under35':'Under 3.5','under25':'Under 2.5','second_half_more':'2ª Tempo'
}

def render_prob_bars(analise, markets):
    thresholds = {'btts':60,'over25':60,'over15':80,'under35':70,'under25':60,'second_half_more':60}
    html = ""
    for m in markets:
        prob = analise.get(f'prob_{m}', 0)
        t = thresholds.get(m, 60)
        bc = prob_bar_class(prob, t)
        label = MARKET_MAP.get(m, m)
        html += f"""
        <div class="prob-row">
            <span class="prob-label">{label}</span>
            <div class="prob-bar-wrap"><div class="prob-bar {bc}" style="width:{prob}%"></div></div>
            <span class="prob-pct">{prob:.0f}%</span>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)

def render_metric_tiles(analise, markets):
    thresholds = {'btts':60,'over25':60,'over15':80,'under35':70,'under25':60,'second_half_more':60}
    n = len(markets)
    if n == 0: return
    cols = st.columns(n)
    for i, m in enumerate(markets):
        prob = analise.get(f'prob_{m}', 0)
        odd  = analise.get(f'odd_justa_{m}', 0)
        t    = thresholds.get(m, 60)
        mc   = metric_class(prob, t)
        label = MARKET_MAP.get(m, m)
        with cols[i]:
            st.markdown(f"""
            <div class="metric-tile {mc}">
                <div class="val">{prob:.0f}<span style="font-size:0.6em;color:#64748b">%</span></div>
                <div class="lbl">{label}</div>
                <div class="sub">@ {odd}</div>
            </div>""", unsafe_allow_html=True)

def render_team_card(name, profile, side="🏠"):
    style_css = {'ofensivo':'style-of','defensivo':'style-df','equilibrado':'style-eq'}[profile['estilo']]
    bars = ""
    for label, val in [("Ataque", profile['ataque']), ("Defesa", profile['defesa'])]:
        pct = val * 10
        bar_c = "bar-green" if val>=7 else "bar-yellow" if val>=5 else "bar-red"
        bars += f"""
        <div class="prob-row" style="margin-bottom:0.35rem">
            <span class="prob-label">{label}</span>
            <div class="prob-bar-wrap"><div class="prob-bar {bar_c}" style="width:{pct}%"></div></div>
            <span class="prob-pct">{val}/10</span>
        </div>"""
    stats = ""
    for lbl, k in [("BTTS","btts"),("Over 2.5","over25"),("Over 1.5","over15")]:
        v = profile.get(k,0)
        c = "#4ade80" if v>=60 else "#fbbf24" if v>=45 else "#f87171"
        stats += f'<span style="font-size:0.65rem;color:{c};margin-right:0.6rem">{lbl}: {v}%</span>'

    st.markdown(f"""
    <div class="card">
        <div class="team-header">
            <span class="team-name">{side} {name}</span>
            <span class="team-style {style_css}">{profile['estilo']}</span>
        </div>
        {bars}
        <div style="margin-top:0.5rem;padding-top:0.4rem;border-top:1px solid #1e2535">{stats}</div>
    </div>""", unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    # Session state init
    for k, v in [('last_analise',None),('last_match',None),('selected_comp_name',None)]:
        if k not in st.session_state: st.session_state[k] = v

    analisador   = AnalisadorAutomatico()
    competitions = get_competitions()

    # ── APP HEADER ────────────────────────────────────────────────────────────
    api_ok    = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok   = ODDS_API_KEY != "sua_chave_the_odds_api"
    api_badge = f'<span class="badge {"badge-green" if api_ok else "badge-red"}">{"✓" if api_ok else "✗"} Football</span>'
    odds_badge= f'<span class="badge {"badge-green" if odds_ok else "badge-yellow"}">{"✓" if odds_ok else "!"} Odds</span>'
    email_badge=f'<span class="badge {"badge-green" if EMAIL_USER else "badge-yellow"}">{"✓" if EMAIL_USER else "!"} Email</span>'

    st.markdown(f"""
    <div class="app-header">
        <span class="logo">⚽</span>
        <div>
            <h1>Bet Analyzer</h1>
            <div class="subtitle">Análise automática · H2H · Value Bet · Alertas</div>
        </div>
        <div class="api-badge">{api_badge}{odds_badge}{email_badge}</div>
    </div>""", unsafe_allow_html=True)

    if not competitions:
        if api_ok:
            st.error("❌ Falha ao carregar competições. Verifique sua FOOTBALL_DATA_API_KEY.")
        else:
            st.error("❌ Configure a variável FOOTBALL_DATA_API_KEY no arquivo .env")
        return

    if st.session_state['selected_comp_name'] not in competitions:
        st.session_state['selected_comp_name'] = list(competitions.keys())[0]

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    st.sidebar.markdown('<p class="sec-title">⚙ Configuração</p>', unsafe_allow_html=True)

    default_display = ['BTTS','Over 2.5','Over 1.5','Under 3.5','2ª Tempo']
    rev_map = {v:k for k,v in MARKET_MAP.items()}

    selected_markets_display = st.sidebar.multiselect(
        "Mercados Ativos",
        options=list(MARKET_MAP.values()),
        default=[m for m in default_display if m in MARKET_MAP.values()]
    )
    selected_markets = [rev_map[m] for m in selected_markets_display]

    risco_filter = st.sidebar.selectbox(
        "Filtro",
        ["Todos","🔥 Value Bet","🛡️ Baixo Risco (>70%)"]
    )

    st.sidebar.markdown('<p class="sec-title" style="margin-top:0.6rem">📋 Watchlist</p>', unsafe_allow_html=True)
    new_match = st.sidebar.text_input("Adicionar (Home vs Away)", placeholder="ex: Arsenal vs Chelsea", key="new_match_input")
    if st.sidebar.button("＋ Adicionar") and new_match:
        analisador.watchlist.append(new_match)
        st.session_state.watchlist = analisador.watchlist
        st.rerun()

    for i, match in enumerate(analisador.watchlist):
        c1, c2 = st.sidebar.columns([4,1])
        c1.markdown(f'<div class="watch-item">⚽ {match}</div>', unsafe_allow_html=True)
        if c2.button("✕", key=f"rem_{i}"):
            analisador.watchlist.pop(i)
            st.session_state.watchlist = analisador.watchlist
            st.rerun()

    if not analisador.watchlist:
        st.sidebar.markdown('<div style="font-size:0.68rem;color:#475569;padding:0.3rem 0">Watchlist vazia</div>', unsafe_allow_html=True)

    st.sidebar.markdown('<p class="sec-title" style="margin-top:0.6rem">📧 Alertas</p>', unsafe_allow_html=True)
    email_to = st.sidebar.text_input("Email destino", value="seu@email.com")
    if st.sidebar.button("Enviar Alertas"):
        for ms in analisador.watchlist:
            try:
                home, away = ms.split(" vs ")
                analisador.send_alert({'home_team':home,'away_team':away,'date':datetime.now()},
                                      {'prob_btts':65,'prob_over25':70},email_to)
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔍 Análise", "📊 Perfis", "📈 Histórico"])

    # ── TAB 1: ANÁLISE ────────────────────────────────────────────────────────
    with tab1:
        left, right = st.columns([1,2])

        with left:
            st.markdown('<p class="sec-title">Competição</p>', unsafe_allow_html=True)
            selected_comp_name = st.selectbox(
                "Competição",
                options=list(competitions.keys()),
                key='comp_select',
                index=list(competitions.keys()).index(st.session_state['selected_comp_name']),
                label_visibility="collapsed"
            )
            st.session_state['selected_comp_name'] = selected_comp_name

        competition_id = competitions[selected_comp_name]

        with right:
            st.markdown('<p class="sec-title">Partida</p>', unsafe_allow_html=True)
            with st.spinner("Buscando partidas..."):
                matches = get_matches(competition_id)

            match_options = []
            for m in matches:
                if m["status"] in ["SCHEDULED","TIMED"]:
                    try:
                        dt = datetime.fromisoformat(m["utcDate"].replace("Z","+00:00"))
                        match_options.append({
                            "id": m["id"],
                            "home_id": m["homeTeam"]["id"],
                            "away_id": m["awayTeam"]["id"],
                            "display": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} · {dt.strftime('%d/%m %H:%M')}",
                            "home_team": m["homeTeam"]["name"],
                            "away_team": m["awayTeam"]["name"],
                            "date": dt
                        })
                    except: continue

            if not match_options:
                st.warning("⚠️ Nenhuma partida futura encontrada.")
                selected_match = None
            else:
                sel_str = st.selectbox("Partida", [m["display"] for m in match_options], label_visibility="collapsed")
                selected_match = match_options[[m["display"] for m in match_options].index(sel_str)]

        if selected_match:
            st.markdown("")
            if st.button("🚀 Iniciar Análise", use_container_width=True):
                with st.spinner(f"Analisando {selected_match['home_team']} vs {selected_match['away_team']}…"):
                    try:
                        analise = analisador.analisar_partida_automatica(
                            selected_match['home_team'], selected_match['away_team'],
                            selected_comp_name,
                            selected_match['home_id'], selected_match['away_id'],
                            competition_id, selected_markets
                        )
                        st.session_state['last_analise'] = analise
                        st.session_state['last_match']   = selected_match
                    except Exception as e:
                        st.error(f"Erro na análise: {e}")

        # RESULTS
        if st.session_state['last_analise']:
            analise = st.session_state['last_analise']
            match   = st.session_state['last_match']

            st.markdown('<hr style="border-color:#1e2535;margin:0.8rem 0">', unsafe_allow_html=True)

            # Match title bar
            st.markdown(f"""
            <div class="card" style="display:flex;align-items:center;justify-content:space-between;padding:0.55rem 0.9rem">
                <span style="font-size:0.85rem;font-weight:600;color:#f1f5f9">
                    🏠 {match['home_team']}
                    <span style="color:#475569;font-weight:400;margin:0 0.5rem">vs</span>
                    🚩 {match['away_team']}
                </span>
                <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#64748b;background:#0f172a;padding:0.25rem 0.6rem;border-radius:4px;border:1px solid #1e2535">
                    📅 {match['date'].strftime('%d/%m · %H:%M')}
                </span>
            </div>""", unsafe_allow_html=True)

            # ── Métricas + Barras + Detalhes ─────────────────────────────────
            col_probs, col_detail = st.columns([3, 2])

            with col_probs:
                st.markdown('<p class="sec-title">Probabilidades</p>', unsafe_allow_html=True)
                render_metric_tiles(analise, selected_markets)

                st.markdown('<p class="sec-title" style="margin-top:0.7rem">Distribuição</p>', unsafe_allow_html=True)
                render_prob_bars(analise, selected_markets)

                # H2H inline
                h2h = analise['h2h']
                st.markdown(f"""
                <p class="sec-title" style="margin-top:0.7rem">Head to Head</p>
                <div class="h2h-row">
                    <div class="h2h-item">
                        <div class="h2h-val">{h2h['btts_h2h']:.0f}%</div>
                        <div class="h2h-lbl">BTTS H2H</div>
                    </div>
                    <div class="h2h-item">
                        <div class="h2h-val">{h2h['over25_h2h']:.0f}%</div>
                        <div class="h2h-lbl">Over 2.5 H2H</div>
                    </div>
                </div>""", unsafe_allow_html=True)

            with col_detail:
                st.markdown('<p class="sec-title">Análise</p>', unsafe_allow_html=True)
                lines_html = ""
                for icon, text in analise['analise_detalhada']:
                    lines_html += f'<div class="detail-line"><span class="icon">{icon}</span><span>{text}</span></div>'
                st.markdown(f'<div class="card-sm">{lines_html}</div>', unsafe_allow_html=True)

                st.markdown('<p class="sec-title" style="margin-top:0.6rem">Recomendações</p>', unsafe_allow_html=True)
                pills_html = ""
                cls_map = {'strong':'rec-strong','mid':'rec-mid','low':'rec-low'}
                for strength, label, pct in analise['recomendacao']:
                    c = cls_map.get(strength,'rec-low')
                    pills_html += f'<span class="rec-pill {c}">{label} <b>{pct}</b></span>'
                if pills_html:
                    st.markdown(f'<div class="card-sm">{pills_html}</div>', unsafe_allow_html=True)
                else:
                    st.info("Selecione mercados na sidebar.")

            # ── Value Bet Calculator ──────────────────────────────────────────
            with st.expander("💰 Calculadora de Value Bet"):
                if selected_markets:
                    cols = st.columns(min(4, len(selected_markets)))
                    for j, market in enumerate(selected_markets):
                        with cols[j % min(4, len(selected_markets))]:
                            prob     = analise.get(f'prob_{market}', 0)
                            odd_just = analise.get(f'odd_justa_{market}', 1.5)
                            label    = MARKET_MAP.get(market, market)
                            odd_real = st.number_input(f"{label}", min_value=1.01, value=float(odd_just),
                                                       step=0.01, format="%.2f", key=f"ov_{market}")
                            ev = calculate_value_bet(prob, odd_real)
                            if ev is None: ev = 0
                            ev_label = "✅ VALUE" if ev>0.05 else "✓ Pequeno" if ev>0 else "✗ Sem Value"
                            color = "#4ade80" if ev>0.05 else "#fbbf24" if ev>0 else "#64748b"
                            st.markdown(f"""
                            <div style="text-align:center;margin-top:0.3rem">
                                <div style="font-family:'DM Mono',monospace;font-size:1rem;font-weight:600;color:{color}">{ev:.3f}</div>
                                <div style="font-size:0.62rem;color:{color}">{ev_label}</div>
                            </div>""", unsafe_allow_html=True)
                else:
                    st.info("Selecione mercados para calcular.")

            # ── Live Odds ─────────────────────────────────────────────────────
            live_odds = analisador.fetch_live_odds(match['home_team'], match['away_team'])
            if live_odds:
                with st.expander("📡 Odds ao Vivo"):
                    for bk in live_odds[:2]:
                        st.markdown(f'<p class="sec-title">{bk["title"]}</p>', unsafe_allow_html=True)
                        mt = next((m for m in bk.get('markets',[]) if m['key']=='totals'), None)
                        if mt:
                            ov = next((o['price'] for o in mt['outcomes'] if o.get('point')==2.5 and o.get('name')=='Over'),'N/A')
                            un = next((o['price'] for o in mt['outcomes'] if o.get('point')==2.5 and o.get('name')=='Under'),'N/A')
                            st.markdown(f"""
                            <div class="card-sm">
                                <span style="font-size:0.72rem">Over 2.5: <b style="color:#93c5fd">@{ov}</b> &nbsp; Under 2.5: <b style="color:#93c5fd">@{un}</b></span>
                            </div>""", unsafe_allow_html=True)

    # ── TAB 2: PERFIS ─────────────────────────────────────────────────────────
    with tab2:
        if st.session_state['last_match']:
            m      = st.session_state['last_match']
            comp_id= competitions[st.session_state['selected_comp_name']]
            with st.spinner("Carregando perfis…"):
                hp = fetch_team_profile_cached(m['home_id'], comp_id)
                ap = fetch_team_profile_cached(m['away_id'], comp_id)
            c1, c2 = st.columns(2)
            with c1: render_team_card(m['home_team'], hp, "🏠")
            with c2: render_team_card(m['away_team'], ap, "🚩")

            # Radar comparison
            cats = ['Ataque','Defesa','BTTS','Over 2.5','Over 1.5']
            hp_v = [hp['ataque']*10, hp['defesa']*10, hp['btts'], hp['over25'], hp['over15']]
            ap_v = [ap['ataque']*10, ap['defesa']*10, ap['btts'], ap['over25'], ap['over15']]

            fig = go.Figure()
            for name, vals, color in [(m['home_team'], hp_v, '#3b82f6'),(m['away_team'], ap_v, '#f97316')]:
                fig.add_trace(go.Scatterpolar(
                    r=vals+[vals[0]], theta=cats+[cats[0]],
                    fill='toself', name=name,
                    line=dict(color=color, width=2),
                    fillcolor=color.replace(')',',0.15)').replace('rgb','rgba') if 'rgb' in color else color+'26'
                ))
            fig.update_layout(
                polar=dict(
                    bgcolor='#0f172a',
                    radialaxis=dict(visible=True, range=[0,100], color='#475569',
                                   gridcolor='#1e2535', tickfont=dict(size=8,color='#475569')),
                    angularaxis=dict(color='#94a3b8', gridcolor='#1e2535',
                                    tickfont=dict(size=9,color='#94a3b8'))
                ),
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(family='DM Sans', color='#94a3b8'),
                legend=dict(font=dict(size=10,color='#94a3b8'), bgcolor='transparent'),
                margin=dict(l=30,r=30,t=30,b=30), height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Analise uma partida primeiro para ver os perfis dos times.")

    # ── TAB 3: HISTÓRICO ──────────────────────────────────────────────────────
    with tab3:
        if analisador.historico_analises:
            df = pd.DataFrame(analisador.historico_analises)
            df['Prob Média'] = ((df['prob_btts']+df['prob_over25'])/2).round(1)
            st.dataframe(
                df.sort_values(by='data',ascending=False)
                  .rename(columns={'home':'Casa','away':'Fora','prob_btts':'BTTS %',
                                   'prob_over25':'Ov2.5 %','data':'Data'}),
                use_container_width=True, hide_index=True
            )
            pdf_bytes = analisador.gerar_relatorio_pdf(analisador.historico_analises)
            st.download_button(
                "⬇️ Exportar PDF",
                data=pdf_bytes,
                file_name="relatorio_analises.pdf",
                mime="application/pdf"
            )
        else:
            st.info("Histórico vazio. Analise uma partida para popular.")

if __name__ == "__main__":
    main()
