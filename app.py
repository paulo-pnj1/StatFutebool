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

# --- 1. CONFIGURAÇÃO INICIAL E VARIÁVEIS DE AMBIENTE ---
load_dotenv()

st.set_page_config(
    page_title="Analisador de Apostas",
    layout="wide",
    page_icon="soccer"
)

# ── TEMA VISUAL ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow:wght@300;400;500;600&display=swap');

/*
  PALETA:
  Fundo principal  : #0F1923
  Superficie       : #162130
  Card             : #1E2D3E
  Borda            : #2C3E52
  Verde primario   : #00C853
  Dourado          : #FFB300
  Vermelho         : #E53935
  Texto principal  : #FFFFFF
  Texto secundario : #C5D3DE
  Texto terciario  : #8FA3B1
*/

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    color: #FFFFFF;
}

.stApp {
    background-color: #0F1923;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(0,200,83,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(0,132,61,0.03) 0%, transparent 50%);
}

p, li { color: #FFFFFF !important; }
.stMarkdown p, .stMarkdown li { color: #FFFFFF !important; }
label {
    color: #C5D3DE !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.9rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0B1420;
    border-right: 1px solid #1E2D3E;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] span { color: #FFFFFF !important; }
section[data-testid="stSidebar"] label { color: #C5D3DE !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important;
    font-family: 'Rajdhani', sans-serif !important;
}
section[data-testid="stSidebar"] .stExpander {
    background-color: #162130;
    border: 1px solid #2C3E52;
    border-radius: 8px;
}

/* Sidebar inputs — fundo preto */
section[data-testid="stSidebar"] .stMultiSelect > div > div,
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #0A0F16 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] .stMultiSelect > div > div:focus-within,
section[data-testid="stSidebar"] .stSelectbox > div > div:focus-within {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 2px rgba(0,200,83,0.2) !important;
}
/* Dropdown popup — fundo preto, letras brancas */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[data-baseweb="menu"],
[role="listbox"] {
    background-color: #0A0F16 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 6px !important;
}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="listbox"] li,
[role="option"] {
    background-color: #0A0F16 !important;
    color: #FFFFFF !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background-color: #1E2D3E !important;
    color: #FFFFFF !important;
}
/* Tags selecionadas */
span[data-baseweb="tag"] {
    background-color: #1E2D3E !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 4px !important;
}
span[data-baseweb="tag"] span { color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background-color: #162130 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
}

/* ── Titulos ── */
h1 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.4rem !important;
    color: #FFFFFF !important;
    letter-spacing: 0.04em;
    padding-bottom: 0.25rem;
    border-bottom: 3px solid #00C853;
    display: inline-block;
    margin-bottom: 0.5rem !important;
}
h2 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    border-left: 4px solid #00C853;
    padding-left: 0.75rem;
    margin-top: 1.5rem !important;
}
h3 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0B1420;
    border-bottom: 2px solid #1E2D3E;
    gap: 4px;
    padding: 0 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
    color: #C5D3DE !important;
    background-color: transparent !important;
    border: none !important;
    padding: 12px 20px;
    text-transform: uppercase;
}
.stTabs [aria-selected="true"] {
    color: #00C853 !important;
    border-bottom: 3px solid #00C853 !important;
    background-color: rgba(0,200,83,0.06) !important;
    border-radius: 4px 4px 0 0;
}

/* ── Botao Principal ── */
.stButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 1rem;
    background-color: #2E7D52 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(46,125,82,0.3) !important;
}
.stButton > button:hover {
    background-color: #3A9463 !important;
    box-shadow: 0 6px 20px rgba(46,125,82,0.45) !important;
    transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #E53935 !important;
    color: #FFFFFF !important;
    font-size: 0.75rem !important;
    padding: 0.25rem 0.6rem !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #EF5350 !important;
    transform: none !important;
}

/* ── Inputs area principal ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: #162130 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 2px rgba(0,200,83,0.2) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background-color: #162130 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
}
input { color: #FFFFFF !important; }
input::placeholder { color: #8FA3B1 !important; }

/* ── Metricas ── */
[data-testid="stMetric"] {
    background-color: #162130;
    border: 1px solid #2C3E52;
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetric"] label {
    color: #C5D3DE !important;
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.8rem !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-family: 'Barlow', sans-serif !important; }

/* ── Alertas ── */
.stSuccess {
    background-color: rgba(0,200,83,0.12) !important;
    border-left: 4px solid #00C853 !important;
    border-radius: 6px !important;
}
.stSuccess p, .stSuccess span { color: #CCFFE0 !important; }
.stWarning {
    background-color: rgba(255,179,0,0.12) !important;
    border-left: 4px solid #FFB300 !important;
    border-radius: 6px !important;
}
.stWarning p, .stWarning span { color: #FFE082 !important; }
.stError {
    background-color: rgba(229,57,53,0.12) !important;
    border-left: 4px solid #E53935 !important;
    border-radius: 6px !important;
}
.stError p, .stError span { color: #FFCDD2 !important; }
.stInfo {
    background-color: rgba(33,150,243,0.10) !important;
    border-left: 4px solid #2196F3 !important;
    border-radius: 6px !important;
}
.stInfo p, .stInfo span { color: #BBDEFB !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #00C853 !important; }

/* ── DataFrame ── */
.stDataFrame {
    border: 1px solid #2C3E52 !important;
    border-radius: 8px !important;
    overflow: hidden;
}
thead tr th {
    background-color: #1E2D3E !important;
    color: #C5D3DE !important;
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.8rem !important;
    border-bottom: 1px solid #2C3E52 !important;
}
tbody tr:nth-child(even) { background-color: #162130 !important; }
tbody tr:nth-child(odd)  { background-color: #1A2636 !important; }
tbody tr:hover           { background-color: #263547 !important; }
tbody td                 { color: #FFFFFF !important; }

/* ── Progress Bar ── */
.stProgress > div > div > div > div {
    background-color: #00C853 !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background-color: #2C3E52 !important;
    border-radius: 4px !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    background-color: #FFB300 !important;
    color: #0F1923 !important;
    border: none !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 15px rgba(255,179,0,0.25) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background-color: #FFC933 !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #162130 !important;
    border: 1px solid #2C3E52 !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #C5D3DE !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background-color: #162130 !important;
    border: 1px solid #2C3E52 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ── Caption ── */
.stCaption { color: #C5D3DE !important; }

hr {
    border-color: #1E2D3E !important;
    margin: 1.5rem 0 !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0B1420; }
::-webkit-scrollbar-thumb { background: #2C3E52; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3A5068; }

/* ── Badges ── */
.badge-gold {
    display: inline-block;
    background: rgba(255,179,0,0.15);
    border: 1px solid #FFB300;
    color: #FFB300;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    padding: 2px 10px;
    border-radius: 20px;
    text-transform: uppercase;
}

/* ── Cards ── */
.match-card {
    background: linear-gradient(135deg, #1E2D3E 0%, #162130 100%);
    border: 1px solid #2C3E52;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.5rem 0;
}
.result-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    text-align: center;
    padding: 0.75rem;
    background: linear-gradient(135deg, #162130 0%, #1E2D3E 100%);
    border-radius: 10px;
    border: 1px solid #2C3E52;
}
.api-status {
    background-color: #162130;
    border: 1px solid #2C3E52;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'Barlow', sans-serif;
    font-size: 0.85rem;
    color: #C5D3DE;
    margin-bottom: 1rem;
}
.api-status strong { color: #00C853; }

/* ── Multiselect tags ── */
span[data-baseweb="tag"] {
    background-color: #e0f2e0 !important;  /* Verde muito claro */
    border: 1px solid #00C853 !important;
    border-radius: 4px !important;
}
span[data-baseweb="tag"] span { color: #000000 !important; }  /* Texto preto */

/* Dropdown options */
li[role="option"] {
    color: #FFFFFF !important;
    background-color: #162130 !important;
}
li[role="option"]:hover { background-color: #1E2D3E !important; }
</style>
""", unsafe_allow_html=True)

# Chaves API e Email
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY, "Accept": "application/json"}
HEADERS_ODDS     = {"Authorization": f"apikey {ODDS_API_KEY}"}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS     = "https://api.the-odds-api.com/v4"

# --- 2. FUNÇÕES DE UTILIDADE ---
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

# --- 3. FUNÇÕES DE API ---
@st.cache_data(ttl=3600)
def fetch_football_data(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        st.error("Chave FOOTBALL_DATA_API_KEY nao configurada.")
        return None
    try:
        url = f"{BASE_URL_FOOTBALL}/{endpoint}"
        response = requests.get(url, headers=HEADERS_FOOTBALL, timeout=15)
        if response.status_code == 429:
            st.error("Limite de requisicoes da API atingido. Tente mais tarde.")
            return None
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_football_data("competitions")
    if data and "competitions" in data:
        top = [
            "Premier League", "Primera Division", "Serie A", "Bundesliga",
            "Ligue 1", "Primeira Liga", "Eredivisie", "Jupiler Pro League",
            "Scottish Premiership", "UEFA Champions League",
            "UEFA Europa League", "UEFA Conference League"
        ]
        return {c["name"]: c["id"] for c in data["competitions"] if c["name"] in top and c.get("currentSeason")}
    return {}

@st.cache_data(ttl=600)
def get_matches(competition_id):
    today     = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_football_data(f"competitions/{competition_id}/matches?dateFrom={today}&dateTo={next_week}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile_cached(team_id, comp_id):
    profile = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado', 'over25': 50,
               'btts': 50, 'over15': 70, 'under35': 70, 'under25': 50, 'second_half_more': 50}
    try:
        sd = fetch_football_data(f"competitions/{comp_id}/standings")
        if sd and 'standings' in sd:
            for group in sd['standings']:
                for t in group['table']:
                    if t['team']['id'] == team_id and t['playedGames'] > 0:
                        ag = t['goalsFor'] / t['playedGames']
                        aa = t['goalsAgainst'] / t['playedGames']
                        profile['ataque'] = min(10, max(1, round((ag / 1.4) * 7 + 1)))
                        profile['defesa'] = min(10, max(1, round((1.4 / max(aa, 0.1)) * 7 + 1)))
                        break

        md = fetch_football_data(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if md and 'matches' in md:
            rm = md['matches'][:10]
            if rm:
                n = len(rm)
                profile['over25']           = round(sum(1 for m in rm if get_total_goals(m) > 2.5) / n * 100)
                profile['btts']             = round(sum(1 for m in rm if get_home_goals(m) > 0 and get_away_goals(m) > 0) / n * 100)
                profile['over15']           = round(sum(1 for m in rm if get_total_goals(m) > 1.5) / n * 100)
                profile['under35']          = round(sum(1 for m in rm if get_total_goals(m) < 3.5) / n * 100)
                profile['under25']          = round(sum(1 for m in rm if get_total_goals(m) < 2.5) / n * 100)
                profile['second_half_more'] = round(sum(1 for m in rm if get_second_half_goals(m) > get_first_half_goals(m)) / n * 100)

        a, d = profile['ataque'], profile['defesa']
        profile['estilo'] = 'ofensivo' if (a >= 7 and d <= 6) else 'defensivo' if (d >= 7 and a <= 6) else 'equilibrado'
        return profile
    except Exception:
        return profile

# --- 4. CLASSE MOTOR DE ANÁLISE ---
class AnalisadorAutomatico:
    def __init__(self):
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        if 'historico_analises' not in st.session_state:
            st.session_state.historico_analises = []
        self.watchlist         = st.session_state.watchlist
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
            hm = fetch_football_data(f"teams/{home_id}/matches?status=FINISHED&limit=20")
            h2h = []
            if hm and 'matches' in hm:
                for m in hm['matches']:
                    if m.get('awayTeam', {}).get('id') == away_id or m.get('homeTeam', {}).get('id') == away_id:
                        h2h.append(m)
                        if len(h2h) >= limit:
                            break
            return {
                'btts_h2h':   sum(1 for m in h2h if get_home_goals(m) > 0 and get_away_goals(m) > 0) / max(len(h2h), 1) * 100,
                'over25_h2h': sum(1 for m in h2h if get_total_goals(m) > 2.5) / max(len(h2h), 1) * 100
            }
        except Exception:
            return {'btts_h2h': 50, 'over25_h2h': 50}

    def fetch_live_odds(self, home_team, away_team):
        try:
            if ODDS_API_KEY == "sua_chave_the_odds_api":
                return []
            url = f"{BASE_URL_ODDS}/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals"
            r = requests.get(url, headers=HEADERS_ODDS, timeout=10)
            if r.status_code == 200:
                for event in r.json():
                    if home_team.lower() in event['home_team'].lower() and away_team.lower() in event['away_team'].lower():
                        return event.get('bookmakers', [])
            return []
        except Exception:
            return []

    def analisar_partida_automatica(self, home_team, away_team, competition, home_id, away_id, comp_id, selected_markets):
        hp  = fetch_team_profile_cached(home_id, comp_id)
        ap  = fetch_team_profile_cached(away_id, comp_id)
        h2h = self.fetch_h2h(home_id, away_id)

        def clamp(v, lo, hi): return min(hi, max(lo, v))
        aj = self.calcular_ajustes_estilo(hp, ap)
        ac = self.calcular_ajustes_competicao(competition)

        pb   = clamp((hp['btts'] + ap['btts']) / 2 + aj['btts'] + ac['btts'] + (h2h['btts_h2h'] - 50) / 10, 15, 85)
        po25 = clamp((hp['over25'] + ap['over25']) / 2 + aj['over25'] + ac['over25'] + (h2h['over25_h2h'] - 50) / 10, 20, 80)
        po15 = clamp((hp['over15'] + ap['over15']) / 2 + aj['over15'] + ac['over15'], 40, 95)
        pu35 = clamp((hp['under35'] + ap['under35']) / 2 + aj['under35'] + ac['under35'], 30, 90)
        pu25 = clamp((hp['under25'] + ap['under25']) / 2 + aj['under25'] + ac['under25'], 25, 85)
        ps   = clamp((hp['second_half_more'] + ap['second_half_more']) / 2 + aj['second_half_more'] + ac['second_half_more'], 20, 80)

        analise = {
            'prob_btts': round(pb, 1), 'prob_over25': round(po25, 1), 'prob_over15': round(po15, 1),
            'prob_under35': round(pu35, 1), 'prob_under25': round(pu25, 1), 'prob_second_half_more': round(ps, 1),
            'odd_justa_btts': round(100 / pb, 2), 'odd_justa_over25': round(100 / po25, 2),
            'odd_justa_over15': round(100 / po15, 2), 'odd_justa_under35': round(100 / pu35, 2),
            'odd_justa_under25': round(100 / pu25, 2), 'odd_justa_second_half_more': round(100 / ps, 2),
            'h2h': h2h,
            'analise_detalhada': self.gerar_analise_detalhada(home_team, away_team, hp, ap, aj, h2h),
            'recomendacao': self.gerar_recomendacao(pb, po25, po15, pu35, pu25, ps, selected_markets)
        }
        self.save_historico(analise, home_team, away_team)
        return analise

    def calcular_ajustes_estilo(self, home, away):
        aj = {'btts': 0, 'over25': 0, 'over15': 0, 'under35': 0, 'under25': 0, 'second_half_more': 0}
        if home['estilo'] == 'ofensivo' and away['estilo'] == 'ofensivo':
            aj['btts']+=8; aj['over25']+=12; aj['over15']+=5; aj['under35']-=10; aj['under25']-=8; aj['second_half_more']+=5
        elif home['estilo'] in ('ofensivo','defensivo') and away['estilo'] in ('ofensivo','defensivo') and home['estilo'] != away['estilo']:
            aj['btts']+=3; aj['over25']+=2; aj['over15']+=2; aj['under35']-=3; aj['under25']-=2; aj['second_half_more']+=3
        elif home['estilo'] == 'defensivo' and away['estilo'] == 'defensivo':
            aj['btts']-=10; aj['over25']-=15; aj['over15']-=5; aj['under35']+=12; aj['under25']+=10; aj['second_half_more']-=5
        if home['ataque'] >= 8 and away['defesa'] <= 5:
            aj['btts']+=5; aj['over25']+=8; aj['over15']+=4; aj['under35']-=6; aj['under25']-=5; aj['second_half_more']+=4
        if away['ataque'] >= 8 and home['defesa'] <= 5:
            aj['btts']+=5; aj['over25']+=8; aj['over15']+=4; aj['under35']-=6; aj['under25']-=5; aj['second_half_more']+=4
        return aj

    def calcular_ajustes_competicao(self, competition):
        aj = {'btts': 0, 'over25': 0, 'over15': 0, 'under35': 0, 'under25': 0, 'second_half_more': 0}
        if 'Premier League' in competition:
            aj['over25']+=5; aj['over15']+=3; aj['under35']-=2; aj['under25']-=1; aj['second_half_more']+=2
        elif 'Serie A' in competition:
            aj['btts']-=3; aj['over25']-=2; aj['over15']-=1; aj['under35']+=4; aj['under25']+=3; aj['second_half_more']-=2
        elif 'Bundesliga' in competition:
            aj['btts']+=5; aj['over25']+=8; aj['over15']+=5; aj['under35']-=8; aj['under25']-=7; aj['second_half_more']+=5
        return aj

    def gerar_analise_detalhada(self, home_team, away_team, hp, ap, ajustes, h2h):
        lines = [
            f"**{home_team}**: Time **{hp['estilo'].upper()}** (Ataque: {hp['ataque']}/10 · Defesa: {hp['defesa']}/10)",
            f"**{away_team}**: Time **{ap['estilo'].upper()}** (Ataque: {ap['ataque']}/10 · Defesa: {ap['defesa']}/10)",
            f"**H2H Recente**: BTTS **{h2h['btts_h2h']:.0f}%** | Over 2.5 **{h2h['over25_h2h']:.0f}%**",
        ]
        if hp['estilo'] == 'ofensivo' and ap['estilo'] == 'ofensivo':
            lines.append("**Confronto**: Dois times ofensivos — Alta probabilidade de gols")
        elif hp['estilo'] == 'defensivo' and ap['estilo'] == 'defensivo':
            lines.append("**Confronto**: Dois times defensivos — Baixa probabilidade de gols")
        else:
            lines.append("**Confronto**: Estilos diferentes — Jogo equilibrado")
        if hp['ataque'] >= 8: lines.append(f"{home_team} tem ataque muito forte")
        if ap['ataque'] >= 8: lines.append(f"{away_team} tem ataque muito forte")
        if hp['defesa'] <= 5: lines.append(f"{home_team} tem defesa vulneravel")
        if ap['defesa'] <= 5: lines.append(f"{away_team} tem defesa vulneravel")
        return lines

    def gerar_recomendacao(self, pb, po25, po15, pu35, pu25, ps, selected_markets):
        recs = []
        if 'btts' in selected_markets:
            if pb >= 60:   recs.append("**BTTS**: FORTE candidato — Probabilidade alta")
            elif pb >= 50: recs.append("**BTTS**: Candidato moderado — Vale a analise")
            else:          recs.append("**BTTS**: Probabilidade baixa — Melhor evitar")
        if 'over25' in selected_markets:
            if po25 >= 60:   recs.append("**Over 2.5**: FORTE candidato — Alta chance de gols")
            elif po25 >= 50: recs.append("**Over 2.5**: Candidato moderado — Boa oportunidade")
            else:            recs.append("**Over 2.5**: Probabilidade baixa")
        if 'over15' in selected_markets:
            if po15 >= 80:   recs.append("**Over 1.5**: FORTE candidato — Muito provavel")
            elif po15 >= 70: recs.append("**Over 1.5**: Candidato moderado")
            else:            recs.append("**Over 1.5**: Probabilidade moderada")
        if 'under35' in selected_markets:
            if pu35 >= 70:   recs.append("**Under 3.5**: FORTE candidato — Jogo controlado esperado")
            elif pu35 >= 60: recs.append("**Under 3.5**: Candidato moderado")
            else:            recs.append("**Under 3.5**: Probabilidade baixa")
        if 'under25' in selected_markets:
            if pu25 >= 60:   recs.append("**Under 2.5**: FORTE candidato")
            elif pu25 >= 50: recs.append("**Under 2.5**: Candidato moderado")
            else:            recs.append("**Under 2.5**: Probabilidade baixa")
        if 'second_half_more' in selected_markets:
            if ps >= 60:   recs.append("**2nd Half More Goals**: FORTE candidato")
            elif ps >= 50: recs.append("**2nd Half More Goals**: Candidato moderado")
            else:          recs.append("**2nd Half More Goals**: Probabilidade baixa")
        return recs

    def send_alert(self, match_info, analise, email_to):
        if not EMAIL_USER or not EMAIL_PASS:
            st.warning("Configure EMAIL_USER e EMAIL_PASS no .env.")
            return
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_USER
            msg['To']   = email_to
            msg['Subject'] = f"Value Bet: {match_info['home_team']} vs {match_info['away_team']}"
            body = f"Partida: {match_info['home_team']} vs {match_info['away_team']} ({match_info['date'].strftime('%d/%m %H:%M')})\n\n"
            for market in ['btts', 'over25', 'over15', 'under35', 'under25', 'second_half_more']:
                prob  = analise.get(f'prob_{market}', 0)
                value = calculate_value_bet(prob, 2.0)
                if value and value > 0.1:
                    body += f"- {market.upper()}: {prob}% | Value: {value:.2f}\n"
            msg.attach(MimeText(body, 'plain'))
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls(); s.login(EMAIL_USER, EMAIL_PASS)
            s.sendmail(EMAIL_USER, email_to, msg.as_string()); s.quit()
            st.success("Alerta enviado com sucesso.")
        except Exception as e:
            st.error(f"Erro no email: {e}")

    def gerar_relatorio_pdf(self, analises):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatorio de Analises", ln=1, align='C')
        pdf.ln(10)
        for a in analises[-10:]:
            pdf.cell(200, 10, txt=f"{a['home']} vs {a['away']}", ln=1)
            pdf.cell(200, 10, txt=f"BTTS: {a['prob_btts']}% | Over 2.5: {a['prob_over25']}%", ln=1)
            pdf.ln(5)
        return pdf.output(dest='S')

# --- 5. VISUALIZAÇÃO ---
def create_gauge_chart(value, title, target_prob, max_value=100):
    if value >= target_prob:
        bar_color = '#00C853'; step_high = 'rgba(0,200,83,0.18)'
    elif value >= target_prob - 10:
        bar_color = '#FFB300'; step_high = 'rgba(255,179,0,0.18)'
    else:
        bar_color = '#E53935'; step_high = 'rgba(229,57,53,0.18)'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': '%', 'font': {'size': 22, 'color': '#FFFFFF', 'family': 'Rajdhani'}},
        title={'text': (
            f"<span style='font-size:14pt;font-family:Rajdhani,sans-serif;"  # Alterado para 14pt
            f"color:#FFFFFF;font-weight:700;letter-spacing:0.05em;text-transform:uppercase'>{title}</span>"
        )},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'shape': "angular",
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "#2C3E52",
                     'tickfont': {'color': '#FFFFFF', 'size': 9}, 
                     'tickmode': 'array',
                     'tickvals': [0, 20, 40, 60, 80, 100]},
            'bar': {'color': bar_color, 'thickness': 0.25},
            'bgcolor': "#1E2D3E",
            'borderwidth': 0,
            'steps': [
                {'range': [0, target_prob - 10], 'color': 'rgba(229,57,53,0.10)'},
                {'range': [target_prob - 10, target_prob], 'color': 'rgba(255,179,0,0.10)'},
                {'range': [target_prob, max_value], 'color': step_high}
            ],
            'threshold': {'line': {'color': bar_color, 'width': 2}, 'thickness': 0.8, 'value': value}
        }
    ))
    fig.update_layout(
        height=170,  # Aumentei um pouco para acomodar o título maior
        margin=dict(l=5, r=5, t=50, b=5),  # Aumentei a margem superior para 50
        paper_bgcolor='#162130', 
        plot_bgcolor='#162130',
        font={'color': '#FFFFFF'},
    )
    return fig
    
# --- 6. INTERFACE PRINCIPAL ---
def main():
    for key, val in [('last_analise', None), ('last_match', None), ('selected_comp_name', None)]:
        if key not in st.session_state:
            st.session_state[key] = val

    analisador   = AnalisadorAutomatico()
    competitions = get_competitions()

    if not competitions:
        if FOOTBALL_DATA_API_KEY != "DEFAULT_KEY":
            st.error("Nao foi possivel carregar as competicoes. Verifique sua FOOTBALL_DATA_API_KEY.")
        return

    if st.session_state['selected_comp_name'] not in competitions:
        st.session_state['selected_comp_name'] = list(competitions.keys())[0]

    # Header
    st.markdown("# Analisador de Apostas")
    st.markdown(
        "<p style='font-family:Barlow,sans-serif;color:#C5D3DE;font-size:0.95rem;"
        "margin-top:-0.5rem;margin-bottom:1rem;'>"
        "Analise automatica · Dados reais · H2H · Odds live · Value Bets</p>",
        unsafe_allow_html=True
    )

    football_ok = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok     = ODDS_API_KEY != "sua_chave_the_odds_api"
    st.markdown(
        f"<div class='api-status'>"
        f"Football API: <strong>{'OK — ' + FOOTBALL_DATA_API_KEY[:8] + '...' if football_ok else 'Nao configurada'}</strong>"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"Odds API: <strong>{'Configurada' if odds_ok else 'Nao configurada'}</strong>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Sidebar
    st.sidebar.markdown("## Configuracoes")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Mercados Ativos")

    market_map = {
        'btts':             'BTTS (Ambas Marcam)',
        'over25':           'Over 2.5 Gols',
        'over15':           'Over 1.5 Gols',
        'under35':          'Under 3.5 Gols',
        'under25':          'Under 2.5 Gols',
        'second_half_more': 'Mais Gols 2 Tempo'
    }
    default_keys    = ['btts', 'over25', 'over15', 'under35', 'second_half_more']
    default_display = [market_map[k] for k in default_keys]

    selected_markets_display = st.sidebar.multiselect(
        "Selecione os mercados:",
        options=list(market_map.values()),
        default=default_display
    )
    reverse_map      = {v: k for k, v in market_map.items()}
    selected_markets = [reverse_map[m] for m in selected_markets_display]

    risco_filter = st.sidebar.selectbox(
        "Filtro de Recomendacoes",
        ["Todos", "Value Bet (Odd Real > Odd Justa)", "Baixo Risco (Prob >70%)"]
    )

    st.sidebar.markdown("---")

    with st.sidebar.expander("Watchlist e Alertas"):
        new_match = st.text_input("Partida (Home vs Away)", key="new_match_input")
        if st.button("Adicionar") and new_match:
            analisador.watchlist.append(new_match)
            st.session_state.watchlist = analisador.watchlist
            st.rerun()

        st.markdown("**Partidas salvas:**")
        for i, match in enumerate(analisador.watchlist):
            c1, c2 = st.columns([3, 1])
            c1.write(f"— {match}")
            if c2.button("X", key=f"rem_{i}"):
                analisador.watchlist.pop(i)
                st.session_state.watchlist = analisador.watchlist
                st.rerun()

        if not analisador.watchlist:
            st.caption("Watchlist vazia.")

        st.markdown("---")
        email_to = st.text_input("Email para Alertas", value="seu@email.com")
        if st.button("Enviar Alertas"):
            for match_str in analisador.watchlist:
                try:
                    home, away = match_str.split(" vs ")
                    analise_ex = {'prob_btts': 65, 'prob_over25': 70, 'prob_over15': 85,
                                  'prob_under35': 75, 'prob_under25': 50, 'prob_second_half_more': 55}
                    analisador.send_alert({'home_team': home, 'away_team': away, 'date': datetime.now()}, analise_ex, email_to)
                except Exception as e:
                    st.error(f"Erro: {e}")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Análise de Partidas", "Perfis dos Times", "Historico e Relatorios"])

    # ── Tab 1 ──
    with tab1:
        st.markdown("## Seleção e Análise")

        comp_col, match_col = st.columns([1, 2])
        with comp_col:
            selected_comp_name = st.selectbox(
                "Competicao:",
                options=list(competitions.keys()),
                key='comp_select',
                index=list(competitions.keys()).index(st.session_state['selected_comp_name'])
            )
            st.session_state['selected_comp_name'] = selected_comp_name

        competition_id = competitions[selected_comp_name]

        with match_col:
            with st.spinner(f"Buscando partidas de {selected_comp_name}..."):
                matches = get_matches(competition_id)

            match_options = []
            for match in matches:
                if match["status"] in ["SCHEDULED", "TIMED"]:
                    try:
                        md = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
                        match_options.append({
                            "id": match["id"],
                            "home_id": match["homeTeam"]["id"],
                            "away_id": match["awayTeam"]["id"],
                            "display": f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} — {md.strftime('%d/%m %H:%M')}",
                            "home_team": match["homeTeam"]["name"],
                            "away_team": match["awayTeam"]["name"],
                            "date": md
                        })
                    except:
                        continue

            if not match_options:
                st.warning("Nenhuma partida futura encontrada.")
                selected_match = None
            else:
                sel_str = st.selectbox("Partida:", options=[m["display"] for m in match_options])
                selected_match = match_options[[m["display"] for m in match_options].index(sel_str)]

        if selected_match:
            if st.button("Iniciar Analise Automatica", use_container_width=True):
                with st.spinner(f"Analisando {selected_match['home_team']} vs {selected_match['away_team']}..."):
                    try:
                        analise = analisador.analisar_partida_automatica(
                            selected_match['home_team'], selected_match['away_team'], selected_comp_name,
                            selected_match['home_id'], selected_match['away_id'], competition_id, selected_markets
                        )
                        st.session_state['last_analise'] = analise
                        st.session_state['last_match']   = selected_match
                        st.success("Analise concluida com sucesso.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

        if st.session_state['last_analise']:
            analise        = st.session_state['last_analise']
            selected_match = st.session_state['last_match']

            st.markdown("---")

            r1, r2, r3 = st.columns([5, 2, 5])
            with r1:
                st.markdown(f"<div class='result-header'>{selected_match['home_team']}</div>", unsafe_allow_html=True)
            with r2:
                st.markdown(
                    f"<div style='text-align:center;padding:0.75rem;background:#1E2D3E;"
                    f"border-radius:10px;border:1px solid #2C3E52;font-family:Rajdhani,sans-serif;'>"
                    f"<div style='color:#C5D3DE;font-size:0.7rem;letter-spacing:0.08em;text-transform:uppercase;'>Data</div>"
                    f"<div style='color:#FFB300;font-size:1.1rem;font-weight:700;'>{selected_match['date'].strftime('%d/%m')}</div>"
                    f"<div style='color:#C5D3DE;font-size:0.85rem;'>{selected_match['date'].strftime('%H:%M')}</div>"
                    f"</div>", unsafe_allow_html=True
                )
            with r3:
                st.markdown(f"<div class='result-header'>{selected_match['away_team']}</div>", unsafe_allow_html=True)

            st.markdown("---")

            if selected_markets:
                st.markdown("### Probabilidades e Odd Justa")
                cols_prob = st.columns(len(selected_markets))
                for i, market in enumerate(selected_markets):
                    label = market_map.get(market, market.replace('_', ' ').title())
                    with cols_prob[i]:
                        if f'prob_{market}' in analise:
                            st.plotly_chart(create_gauge_chart(analise[f'prob_{market}'], label, 60), use_container_width=True)
                            st.markdown(
                                f"<div style='text-align:center;margin-top:-10px;'>"
                                f"<span class='badge-gold'>Odd Justa: {analise[f'odd_justa_{market}']}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

            st.markdown("---")
            detail_col, recomend_col = st.columns([2, 1])

            with detail_col:
                st.markdown("### Analise Detalhada")
                for linha in analise['analise_detalhada']:
                    st.markdown(f"* {linha}")

                st.markdown("---")
                st.markdown("### Calculadora de Value Bet")
                with st.expander("Inserir Odds Reais da Casa de Apostas"):
                    if selected_markets:
                        num_cols   = min(3, len(selected_markets))
                        value_cols = st.columns(num_cols)
                        for j, market in enumerate(selected_markets):
                            with value_cols[j % num_cols]:
                                prob      = analise.get(f'prob_{market}', 0)
                                odd_justa = analise.get(f'odd_justa_{market}', 0)
                                label     = market_map.get(market, market.replace('_', ' ').title())
                                odd_real  = st.number_input(
                                    f"**{label}**:", min_value=1.01, value=odd_justa,
                                    step=0.01, format="%.2f", key=f"odd_real_{market}"
                                )
                                value = calculate_value_bet(prob, odd_real)
                                delta = "SEM VALUE"
                                if value and value > 0.05:  delta = "VALUE BET FORTE"
                                elif value and value > 0:   delta = "Value Pequeno"
                                st.metric("EV", f"{value:.3f}" if value else "—", delta=delta)

            with recomend_col:
                st.markdown("### Recomendacoes")
                if analise['recomendacao']:
                    for rec in analise['recomendacao']:
                        st.success(rec)
                else:
                    st.info("Selecione mercados na sidebar.")

                st.markdown("---")
                st.markdown("### Odds em Tempo Real")
                live_odds = analisador.fetch_live_odds(selected_match['home_team'], selected_match['away_team'])
                if live_odds:
                    for bookie in live_odds[:2]:
                        st.subheader(bookie['title'])
                        mt = next((m for m in bookie.get('markets', []) if m['key'] == 'totals'), None)
                        if mt:
                            o25 = next((o['price'] for o in mt['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Over'), 'N/A')
                            u25 = next((o['price'] for o in mt['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Under'), 'N/A')
                            st.text(f"Over 2.5: @{o25} | Under 2.5: @{u25}")
                else:
                    st.info("Odds API nao configurada.")

    # ── Tab 2 ──
    with tab2:
        st.markdown("## Perfil dos Times")
        if st.session_state['last_match']:
            hid = st.session_state['last_match']['home_id']
            aid = st.session_state['last_match']['away_id']
            cid = competitions[st.session_state['selected_comp_name']]

            with st.spinner("Carregando perfis..."):
                hp = fetch_team_profile_cached(hid, cid)
                ap = fetch_team_profile_cached(aid, cid)

            home_col, away_col = st.columns(2)

            def render_profile(col, name, profile):
                with col:
                    estilo = profile['estilo'].upper()
                    ec = '#00C853' if estilo == 'OFENSIVO' else '#E53935' if estilo == 'DEFENSIVO' else '#FFB300'
                    st.markdown(
                        f"<div class='match-card'>"
                        f"<h3 style='margin:0 0 0.5rem;font-family:Rajdhani,sans-serif;color:#FFFFFF;'>{name}</h3>"
                        f"<span style='background:rgba(0,0,0,0.3);border:1px solid {ec};"
                        f"color:{ec};font-family:Rajdhani;font-size:0.75rem;letter-spacing:0.07em;"
                        f"padding:2px 10px;border-radius:20px;text-transform:uppercase;'>{estilo}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
                    st.markdown(f"**Ataque:** {profile['ataque']}/10")
                    st.progress(profile['ataque'] / 10)
                    st.markdown(f"**Defesa:** {profile['defesa']}/10")
                    st.progress(profile['defesa'] / 10)
                    m1, m2 = st.columns(2)
                    m1.metric("BTTS",     f"{profile['btts']}%")
                    m2.metric("Over 2.5", f"{profile['over25']}%")
                    m3, m4 = st.columns(2)
                    m3.metric("Over 1.5", f"{profile['over15']}%")
                    m4.metric("2 Tempo+", f"{profile['second_half_more']}%")

            render_profile(home_col, st.session_state['last_match']['home_team'], hp)
            render_profile(away_col, st.session_state['last_match']['away_team'], ap)
        else:
            st.info("Analise uma partida primeiro na aba Analise de Partidas.")

    # ── Tab 3 ──
    with tab3:
        st.markdown("## Historico de Analises")
        if analisador.historico_analises:
            df = pd.DataFrame(analisador.historico_analises)
            df['Prob Media'] = ((df['prob_btts'] + df['prob_over25']) / 2).round(1)
            st.dataframe(df.sort_values(by='data', ascending=False), use_container_width=True)

            st.markdown("---")
            st.markdown("### Exportar Relatorio")
            pdf_report = analisador.gerar_relatorio_pdf(analisador.historico_analises)
            st.download_button(
                label="Baixar PDF — Ultimas 10 Analises",
                data=pdf_report,
                file_name="Relatorio_Analises_Futebol.pdf",
                mime="application/pdf"
            )
        else:
            st.info("Historico vazio. Analise uma partida para ver os dados aqui.")

if __name__ == "__main__":
    main()
