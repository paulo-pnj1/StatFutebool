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
    page_title="⚽ Analisador de Apostas",
    layout="wide",
    page_icon="⚽"
)

# ── TEMA VISUAL: Verde-campo / Carvão / Dourado ──────────────────────────────
st.markdown("""
<style>
/* ── Importação de Fontes ── */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Barlow:wght@300;400;500;600&display=swap');

/* ── Paleta de Cores ──
   Fundo principal  : #0F1923  (carvão profundo)
   Superfície       : #162130  (carvão médio)
   Card             : #1E2D3E  (azul-carvão)
   Borda sutil      : #263547
   Verde primário   : #00C853  (verde campo vibrante)
   Verde escuro     : #00843D
   Dourado          : #FFB300
   Vermelho         : #E53935
   Texto principal  : #E8EDF2
   Texto secundário : #8FA3B1
*/

/* Reset geral */
html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    color: #E8EDF2;
}

/* Fundo principal */
.stApp {
    background-color: #0F1923;
    background-image:
        radial-gradient(ellipse at 20% 0%, rgba(0,200,83,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 100%, rgba(0,132,61,0.04) 0%, transparent 50%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #0B1420;
    border-right: 1px solid #1E2D3E;
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] label {
    color: #8FA3B1 !important;
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-size: 0.8rem;
}
section[data-testid="stSidebar"] .stExpander {
    background-color: #162130;
    border: 1px solid #263547;
    border-radius: 8px;
}

/* ── Títulos ── */
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
    color: #E8EDF2 !important;
    letter-spacing: 0.03em;
    border-left: 4px solid #00C853;
    padding-left: 0.75rem;
    margin-top: 1.5rem !important;
}
h3 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: #B8C8D4 !important;
    letter-spacing: 0.02em;
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
    color: #8FA3B1 !important;
    background-color: transparent !important;
    border: none !important;
    padding: 12px 20px;
    text-transform: uppercase;
    transition: color 0.2s;
}
.stTabs [aria-selected="true"] {
    color: #00C853 !important;
    border-bottom: 3px solid #00C853 !important;
    background-color: rgba(0,200,83,0.06) !important;
    border-radius: 4px 4px 0 0;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}

/* ── Botão Principal ── */
.stButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 1rem;
    background-color: #00C853 !important;
    color: #0F1923 !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.5rem !important;
    transition: background-color 0.2s, transform 0.1s, box-shadow 0.2s !important;
    box-shadow: 0 4px 15px rgba(0,200,83,0.25) !important;
}
.stButton > button:hover {
    background-color: #00E676 !important;
    box-shadow: 0 6px 20px rgba(0,200,83,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Botão pequeno (X na watchlist) */
section[data-testid="stSidebar"] .stButton > button {
    background-color: #E53935 !important;
    color: #FFFFFF !important;
    font-size: 0.75rem !important;
    padding: 0.25rem 0.6rem !important;
    box-shadow: none !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #EF5350 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Selectbox / Inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: #162130 !important;
    border: 1px solid #263547 !important;
    border-radius: 6px !important;
    color: #E8EDF2 !important;
    font-family: 'Barlow', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 2px rgba(0,200,83,0.2) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background-color: #162130 !important;
    border: 1px solid #263547 !important;
    border-radius: 6px !important;
    color: #E8EDF2 !important;
    font-family: 'Barlow', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00C853 !important;
    box-shadow: 0 0 0 2px rgba(0,200,83,0.2) !important;
}

/* ── Métricas ── */
[data-testid="stMetric"] {
    background-color: #162130;
    border: 1px solid #263547;
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetric"] label {
    color: #8FA3B1 !important;
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.8rem !important;
}
[data-testid="stMetricValue"] {
    color: #E8EDF2 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Alertas / Info / Warning / Success ── */
.stSuccess {
    background-color: rgba(0,200,83,0.12) !important;
    border-left: 4px solid #00C853 !important;
    border-radius: 6px !important;
    color: #B8F5D0 !important;
}
.stWarning {
    background-color: rgba(255,179,0,0.12) !important;
    border-left: 4px solid #FFB300 !important;
    border-radius: 6px !important;
    color: #FFE082 !important;
}
.stError {
    background-color: rgba(229,57,53,0.12) !important;
    border-left: 4px solid #E53935 !important;
    border-radius: 6px !important;
    color: #FFCDD2 !important;
}
.stInfo {
    background-color: rgba(33,150,243,0.10) !important;
    border-left: 4px solid #2196F3 !important;
    border-radius: 6px !important;
    color: #BBDEFB !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #00C853 !important;
}

/* ── DataFrames ── */
.stDataFrame {
    border: 1px solid #263547 !important;
    border-radius: 8px !important;
    overflow: hidden;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background-color: #162130 !important;
}
thead tr th {
    background-color: #1E2D3E !important;
    color: #8FA3B1 !important;
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.8rem !important;
    border-bottom: 1px solid #263547 !important;
}
tbody tr:nth-child(even) {
    background-color: #162130 !important;
}
tbody tr:nth-child(odd) {
    background-color: #1A2636 !important;
}
tbody tr:hover {
    background-color: #263547 !important;
}

/* ── Progress Bar ── */
.stProgress > div > div > div > div {
    background-color: #00C853 !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background-color: #263547 !important;
    border-radius: 4px !important;
}

/* ── Download Button ── */
.stDownloadButton > button {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    background-color: #FFB300 !important;
    color: #0F1923 !important;
    border: none !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 15px rgba(255,179,0,0.25) !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background-color: #FFC933 !important;
    box-shadow: 0 6px 20px rgba(255,179,0,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #162130 !important;
    border: 1px solid #263547 !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: #8FA3B1 !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em;
}
.streamlit-expanderContent {
    background-color: #162130 !important;
    border: 1px solid #263547 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ── Caption / Code ── */
.stCaption {
    color: #8FA3B1 !important;
    font-size: 0.82rem !important;
    font-family: 'Barlow', sans-serif !important;
}

/* ── Divisor ── */
hr {
    border-color: #1E2D3E !important;
    margin: 1.5rem 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0B1420; }
::-webkit-scrollbar-thumb { background: #263547; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2E4060; }

/* ── Status Badge (custom) ── */
.badge-green {
    display: inline-block;
    background: rgba(0,200,83,0.15);
    border: 1px solid #00C853;
    color: #00C853;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    padding: 2px 10px;
    border-radius: 20px;
    text-transform: uppercase;
}
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

/* ── Match card ── */
.match-card {
    background: linear-gradient(135deg, #1E2D3E 0%, #162130 100%);
    border: 1px solid #263547;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.5rem 0;
}

/* ── API status bar ── */
.api-status {
    background-color: #162130;
    border: 1px solid #263547;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'Barlow', sans-serif;
    font-size: 0.85rem;
    color: #8FA3B1;
    margin-bottom: 1rem;
}
.api-status strong { color: #00C853; }

/* ── Column headers no resultado ── */
.result-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    text-align: center;
    padding: 0.75rem;
    background: linear-gradient(135deg, #162130 0%, #1E2D3E 100%);
    border-radius: 10px;
    border: 1px solid #263547;
}

/* ── Multiselect tags ── */
span[data-baseweb="tag"] {
    background-color: rgba(0,200,83,0.18) !important;
    border: 1px solid #00C853 !important;
    color: #00E676 !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# Chaves API e Email
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
HEADERS_FOOTBALL = {
    "X-Auth-Token": FOOTBALL_DATA_API_KEY,
    "Accept": "application/json"
}
HEADERS_ODDS = {
    "Authorization": f"apikey {ODDS_API_KEY}"
}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS = "https://api.the-odds-api.com/v4"

# --- 2. FUNÇÕES DE UTILIDADE E CÁLCULO ---
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
        st.error("❌ A chave FOOTBALL_DATA_API_KEY não está configurada no seu ambiente.")
        return None
    try:
        url = f"{BASE_URL_FOOTBALL}/{endpoint}"
        response = requests.get(url, headers=HEADERS_FOOTBALL, timeout=15)
        if response.status_code == 429:
            st.error("❌ Limite de requisições da API Football-Data atingido. Tente novamente mais tarde.")
            return None
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_football_data("competitions")
    if data and "competitions" in data:
        comp_dict = {}
        top_competitions_names = [
            "Premier League", "Primera Division", "Serie A", "Bundesliga",
            "Ligue 1", "Primeira Liga", "Eredivisie", "Jupiler Pro League",
            "Scottish Premiership",
            "UEFA Champions League", "UEFA Europa League", "UEFA Conference League"
        ]
        for comp in data["competitions"]:
            if comp["name"] in top_competitions_names and comp.get("currentSeason"):
                comp_dict[comp["name"]] = comp["id"]
        return comp_dict
    return {}

@st.cache_data(ttl=600)
def get_matches(competition_id):
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_football_data(f"competitions/{competition_id}/matches?dateFrom={today}&dateTo={next_week}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile_cached(team_id, comp_id):
    profile = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado', 'over25': 50, 'btts': 50, 'over15': 70, 'under35': 70, 'under25': 50, 'second_half_more': 50}
    try:
        standings_data = fetch_football_data(f"competitions/{comp_id}/standings")
        if standings_data and 'standings' in standings_data:
            for group in standings_data['standings']:
                for team_entry in group['table']:
                    if team_entry['team']['id'] == team_id:
                        played = team_entry['playedGames']
                        gf = team_entry['goalsFor']
                        ga = team_entry['goalsAgainst']
                        if played > 0:
                            avg_scored = gf / played
                            avg_conceded = ga / played
                            profile['ataque'] = min(10, max(1, round((avg_scored / 1.4) * 7 + 1)))
                            profile['defesa'] = min(10, max(1, round((1.4 / max(avg_conceded, 0.1)) * 7 + 1)))
                        break
        matches_data = fetch_football_data(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if matches_data and 'matches' in matches_data:
            recent_matches = matches_data['matches'][:10]
            if recent_matches:
                total_over25 = sum(1 for m in recent_matches if get_total_goals(m) > 2.5)
                total_btts = sum(1 for m in recent_matches if get_home_goals(m) > 0 and get_away_goals(m) > 0)
                total_over15 = sum(1 for m in recent_matches if get_total_goals(m) > 1.5)
                total_under35 = sum(1 for m in recent_matches if get_total_goals(m) < 3.5)
                total_under25 = sum(1 for m in recent_matches if get_total_goals(m) < 2.5)
                total_second_half_more = sum(1 for m in recent_matches if get_second_half_goals(m) > get_first_half_goals(m))
                profile['over25'] = round((total_over25 / len(recent_matches)) * 100)
                profile['btts'] = round((total_btts / len(recent_matches)) * 100)
                profile['over15'] = round((total_over15 / len(recent_matches)) * 100)
                profile['under35'] = round((total_under35 / len(recent_matches)) * 100)
                profile['under25'] = round((total_under25 / len(recent_matches)) * 100)
                profile['second_half_more'] = round((total_second_half_more / len(recent_matches)) * 100)
        attack, defense = profile['ataque'], profile['defesa']
        if attack >= 7 and defense <= 6:
            profile['estilo'] = 'ofensivo'
        elif defense >= 7 and attack <= 6:
            profile['estilo'] = 'defensivo'
        else:
            profile['estilo'] = 'equilibrado'
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
        self.watchlist = st.session_state.watchlist
        self.historico_analises = st.session_state.historico_analises

    def save_historico(self, analise, home_team, away_team):
        self.historico_analises.append({
            'home': home_team,
            'away': away_team,
            'prob_btts': analise['prob_btts'],
            'prob_over25': analise['prob_over25'],
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
                    if m.get('awayTeam', {}).get('id') == away_id or m.get('homeTeam', {}).get('id') == away_id:
                        h2h.append(m)
                        if len(h2h) >= limit:
                            break
            h2h_stats = {
                'btts_h2h': sum(1 for m in h2h if get_home_goals(m) > 0 and get_away_goals(m) > 0) / max(len(h2h), 1) * 100,
                'over25_h2h': sum(1 for m in h2h if get_total_goals(m) > 2.5) / max(len(h2h), 1) * 100
            }
            return h2h_stats
        except Exception:
            return {'btts_h2h': 50, 'over25_h2h': 50}

    def fetch_live_odds(self, home_team, away_team):
        try:
            if ODDS_API_KEY == "sua_chave_the_odds_api":
                return []
            regions = 'eu'
            url = f"{BASE_URL_ODDS}/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions={regions}&markets=h2h,totals"
            response = requests.get(url, headers=HEADERS_ODDS, timeout=10)
            if response.status_code == 200:
                odds_data = response.json()
                for event in odds_data:
                    if home_team.lower() in event['home_team'].lower() and away_team.lower() in event['away_team'].lower():
                        return event.get('bookmakers', [])
            return []
        except Exception:
            return []

    def analisar_partida_automatica(self, home_team, away_team, competition, home_id, away_id, comp_id, selected_markets):
        home_profile = fetch_team_profile_cached(home_id, comp_id)
        away_profile = fetch_team_profile_cached(away_id, comp_id)
        h2h_adjust = self.fetch_h2h(home_id, away_id)

        prob_btts_base = (home_profile['btts'] + away_profile['btts']) / 2
        prob_over25_base = (home_profile['over25'] + away_profile['over25']) / 2
        prob_over15_base = (home_profile['over15'] + away_profile['over15']) / 2
        prob_under35_base = (home_profile['under35'] + away_profile['under35']) / 2
        prob_under25_base = (home_profile['under25'] + away_profile['under25']) / 2
        prob_second_half_more_base = (home_profile['second_half_more'] + away_profile['second_half_more']) / 2

        ajustes = self.calcular_ajustes_estilo(home_profile, away_profile)
        ajustes_competicao = self.calcular_ajustes_competicao(competition)

        prob_btts_final = min(85, max(15, prob_btts_base + ajustes['btts'] + ajustes_competicao['btts'] + (h2h_adjust['btts_h2h'] - 50)/10))
        prob_over25_final = min(80, max(20, prob_over25_base + ajustes['over25'] + ajustes_competicao['over25'] + (h2h_adjust['over25_h2h'] - 50)/10))
        prob_over15_final = min(95, max(40, prob_over15_base + ajustes['over15'] + ajustes_competicao['over15']))
        prob_under35_final = min(90, max(30, prob_under35_base + ajustes['under35'] + ajustes_competicao['under35']))
        prob_under25_final = min(85, max(25, prob_under25_base + ajustes['under25'] + ajustes_competicao['under25']))
        prob_second_half_more_final = min(80, max(20, prob_second_half_more_base + ajustes['second_half_more'] + ajustes_competicao['second_half_more']))

        odd_justa_btts = round(100 / prob_btts_final, 2)
        odd_justa_over25 = round(100 / prob_over25_final, 2)
        odd_justa_over15 = round(100 / prob_over15_final, 2)
        odd_justa_under35 = round(100 / prob_under35_final, 2)
        odd_justa_under25 = round(100 / prob_under25_final, 2)
        odd_justa_second_half_more = round(100 / prob_second_half_more_final, 2)

        analise = {
            'prob_btts': round(prob_btts_final, 1),
            'prob_over25': round(prob_over25_final, 1),
            'prob_over15': round(prob_over15_final, 1),
            'prob_under35': round(prob_under35_final, 1),
            'prob_under25': round(prob_under25_final, 1),
            'prob_second_half_more': round(prob_second_half_more_final, 1),
            'odd_justa_btts': odd_justa_btts,
            'odd_justa_over25': odd_justa_over25,
            'odd_justa_over15': odd_justa_over15,
            'odd_justa_under35': odd_justa_under35,
            'odd_justa_under25': odd_justa_under25,
            'odd_justa_second_half_more': odd_justa_second_half_more,
            'h2h': h2h_adjust,
            'analise_detalhada': self.gerar_analise_detalhada(home_team, away_team, home_profile, away_profile, ajustes, h2h_adjust),
            'recomendacao': self.gerar_recomendacao(prob_btts_final, prob_over25_final, prob_over15_final, prob_under35_final, prob_under25_final, prob_second_half_more_final, selected_markets)
        }

        self.save_historico(analise, home_team, away_team)
        return analise

    def calcular_ajustes_estilo(self, home, away):
        ajustes = {'btts': 0, 'over25': 0, 'over15': 0, 'under35': 0, 'under25': 0, 'second_half_more': 0}
        if home['estilo'] == 'ofensivo' and away['estilo'] == 'ofensivo':
            ajustes['btts'] += 8; ajustes['over25'] += 12; ajustes['over15'] += 5
            ajustes['under35'] -= 10; ajustes['under25'] -= 8; ajustes['second_half_more'] += 5
        elif home['estilo'] == 'ofensivo' and away['estilo'] == 'defensivo':
            ajustes['btts'] += 3; ajustes['over25'] += 2; ajustes['over15'] += 2
            ajustes['under35'] -= 3; ajustes['under25'] -= 2; ajustes['second_half_more'] += 3
        elif home['estilo'] == 'defensivo' and away['estilo'] == 'ofensivo':
            ajustes['btts'] += 3; ajustes['over25'] += 2; ajustes['over15'] += 2
            ajustes['under35'] -= 3; ajustes['under25'] -= 2; ajustes['second_half_more'] += 3
        elif home['estilo'] == 'defensivo' and away['estilo'] == 'defensivo':
            ajustes['btts'] -= 10; ajustes['over25'] -= 15; ajustes['over15'] -= 5
            ajustes['under35'] += 12; ajustes['under25'] += 10; ajustes['second_half_more'] -= 5
        if home['ataque'] >= 8 and away['defesa'] <= 5:
            ajustes['btts'] += 5; ajustes['over25'] += 8; ajustes['over15'] += 4
            ajustes['under35'] -= 6; ajustes['under25'] -= 5; ajustes['second_half_more'] += 4
        if away['ataque'] >= 8 and home['defesa'] <= 5:
            ajustes['btts'] += 5; ajustes['over25'] += 8; ajustes['over15'] += 4
            ajustes['under35'] -= 6; ajustes['under25'] -= 5; ajustes['second_half_more'] += 4
        return ajustes

    def calcular_ajustes_competicao(self, competition):
        ajustes = {'btts': 0, 'over25': 0, 'over15': 0, 'under35': 0, 'under25': 0, 'second_half_more': 0}
        if 'Premier League' in competition:
            ajustes['over25'] += 5; ajustes['over15'] += 3; ajustes['under35'] -= 2
            ajustes['under25'] -= 1; ajustes['second_half_more'] += 2
        elif 'Serie A' in competition:
            ajustes['btts'] -= 3; ajustes['over25'] -= 2; ajustes['over15'] -= 1
            ajustes['under35'] += 4; ajustes['under25'] += 3; ajustes['second_half_more'] -= 2
        elif 'Bundesliga' in competition:
            ajustes['btts'] += 5; ajustes['over25'] += 8; ajustes['over15'] += 5
            ajustes['under35'] -= 8; ajustes['under25'] -= 7; ajustes['second_half_more'] += 5
        return ajustes

    def gerar_analise_detalhada(self, home_team, away_team, home_profile, away_profile, ajustes, h2h):
        analise = []
        analise.append(f"**🏠 {home_team}**: Time **{home_profile['estilo'].upper()}** (Ataque: {home_profile['ataque']}/10 · Defesa: {home_profile['defesa']}/10)")
        analise.append(f"**🚩 {away_team}**: Time **{away_profile['estilo'].upper()}** (Ataque: {away_profile['ataque']}/10 · Defesa: {away_profile['defesa']}/10)")
        analise.append(f"**🤝 H2H Recente**: BTTS **{h2h['btts_h2h']:.0f}%** | Over 2.5 **{h2h['over25_h2h']:.0f}%**")
        if home_profile['estilo'] == 'ofensivo' and away_profile['estilo'] == 'ofensivo':
            analise.append("**⚔️ CONFRONTO**: Dois times ofensivos → Alta probabilidade de gols")
        elif home_profile['estilo'] == 'defensivo' and away_profile['estilo'] == 'defensivo':
            analise.append("**⚔️ CONFRONTO**: Dois times defensivos → Baixa probabilidade de gols")
        else:
            analise.append("**⚔️ CONFRONTO**: Estilos diferentes → Jogo equilibrado")
        if home_profile['ataque'] >= 8:
            analise.append(f"✅ {home_team} tem ataque muito forte")
        if away_profile['ataque'] >= 8:
            analise.append(f"✅ {away_team} tem ataque muito forte")
        if home_profile['defesa'] <= 5:
            analise.append(f"⚠️ {home_team} tem defesa vulnerável")
        if away_profile['defesa'] <= 5:
            analise.append(f"⚠️ {away_team} tem defesa vulnerável")
        return analise

    def gerar_recomendacao(self, prob_btts, prob_over25, prob_over15, prob_under35, prob_under25, prob_second_half_more, selected_markets):
        recomendacoes = []
        if 'btts' in selected_markets:
            if prob_btts >= 60:
                recomendacoes.append("🎯 **BTTS**: FORTE candidato — Probabilidade alta")
            elif prob_btts >= 50:
                recomendacoes.append("🎯 **BTTS**: Candidato moderado — Vale a análise")
            else:
                recomendacoes.append("🎯 **BTTS**: Probabilidade baixa — Melhor evitar")
        if 'over25' in selected_markets:
            if prob_over25 >= 60:
                recomendacoes.append("⚽ **Over 2.5**: FORTE candidato — Alta chance de gols")
            elif prob_over25 >= 50:
                recomendacoes.append("⚽ **Over 2.5**: Candidato moderado — Boa oportunidade")
            else:
                recomendacoes.append("⚽ **Over 2.5**: Probabilidade baixa — Poucos gols esperados")
        if 'over15' in selected_markets:
            if prob_over15 >= 80:
                recomendacoes.append("⚽ **Over 1.5**: FORTE candidato — Muito provável")
            elif prob_over15 >= 70:
                recomendacoes.append("⚽ **Over 1.5**: Candidato moderado — Boa segurança")
            else:
                recomendacoes.append("⚽ **Over 1.5**: Probabilidade moderada — Analisar mais")
        if 'under35' in selected_markets:
            if prob_under35 >= 70:
                recomendacoes.append("🛡️ **Under 3.5**: FORTE candidato — Jogo controlado esperado")
            elif prob_under35 >= 60:
                recomendacoes.append("🛡️ **Under 3.5**: Candidato moderado — Baixo risco")
            else:
                recomendacoes.append("🛡️ **Under 3.5**: Probabilidade baixa — Possível jogo aberto")
        if 'under25' in selected_markets:
            if prob_under25 >= 60:
                recomendacoes.append("🛡️ **Under 2.5**: FORTE candidato — Poucos gols esperados")
            elif prob_under25 >= 50:
                recomendacoes.append("🛡️ **Under 2.5**: Candidato moderado")
            else:
                recomendacoes.append("🛡️ **Under 2.5**: Probabilidade baixa")
        if 'second_half_more' in selected_markets:
            if prob_second_half_more >= 60:
                recomendacoes.append("⏱️ **2nd Half More Goals**: FORTE candidato — Mais gols na 2ª parte")
            elif prob_second_half_more >= 50:
                recomendacoes.append("⏱️ **2nd Half More Goals**: Candidato moderado")
            else:
                recomendacoes.append("⏱️ **2nd Half More Goals**: Probabilidade baixa")
        return recomendacoes

    def send_alert(self, match_info, analise, email_to):
        if not EMAIL_USER or not EMAIL_PASS:
            st.warning("Configure EMAIL_USER e EMAIL_PASS no .env.")
            return
        try:
            msg = MimeMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = email_to
            msg['Subject'] = f"⚽ Value Bet: {match_info['home_team']} vs {match_info['away_team']}"
            body = f"Partida: {match_info['home_team']} vs {match_info['away_team']} ({match_info['date'].strftime('%d/%m %H:%M')})\nValue Bets:\n"
            for market in ['btts', 'over25', 'over15', 'under35', 'under25', 'second_half_more']:
                if market in analise:
                    prob = analise.get(f'prob_{market}', 0)
                    value = calculate_value_bet(prob, 2.0)
                    if value and value > 0.1:
                        body += f"- {market.upper()}: {prob}% prob | Value: {value:.2f}\n"
            msg.attach(MimeText(body, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email_to, msg.as_string())
            server.quit()
            st.success("📧 Alerta enviado com sucesso!")
        except Exception as e:
            st.error(f"Erro no email: {e}")

    def gerar_relatorio_pdf(self, analises):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatório de Análises", ln=1, align='C')
        pdf.ln(10)
        for analise in analises[-10:]:
            pdf.cell(200, 10, txt=f"{analise['home']} vs {analise['away']}", ln=1)
            pdf.cell(200, 10, txt=f"BTTS: {analise['prob_btts']}% | Over 2.5: {analise['prob_over25']}%", ln=1)
            pdf.ln(5)
        pdf_bytes = pdf.output(dest='S')
        return pdf_bytes

# --- 5. FUNÇÕES DE VISUALIZAÇÃO ---
def create_gauge_chart(value, title, target_prob, max_value=100):
    """Gauge com paleta harmoniosa: verde/amarelo/vermelho sobre fundo escuro."""
    if value >= target_prob:
        bar_color = '#00C853'
        step_high = 'rgba(0,200,83,0.18)'
    elif value >= target_prob - 10:
        bar_color = '#FFB300'
        step_high = 'rgba(255,179,0,0.18)'
    else:
        bar_color = '#E53935'
        step_high = 'rgba(229,57,53,0.18)'

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'suffix': '%', 'font': {'size': 28, 'color': '#E8EDF2', 'family': 'Rajdhani'}},
        title={'text': f"<span style='font-size:0.85em;font-family:Rajdhani,sans-serif;color:#8FA3B1;letter-spacing:0.05em;text-transform:uppercase'>{title}</span>"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'shape': "angular",
            'axis': {
                'range': [None, max_value],
                'tickwidth': 1,
                'tickcolor': "#263547",
                'tickfont': {'color': '#8FA3B1', 'size': 10},
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': "#1E2D3E",
            'borderwidth': 0,
            'steps': [
                {'range': [0, target_prob - 10], 'color': 'rgba(229,57,53,0.12)'},
                {'range': [target_prob - 10, target_prob], 'color': 'rgba(255,179,0,0.12)'},
                {'range': [target_prob, max_value], 'color': step_high}
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 3},
                'thickness': 0.85,
                'value': value
            }
        }
    ))

    fig.update_layout(
        height=210,
        margin=dict(l=15, r=15, t=55, b=10),
        paper_bgcolor='#162130',
        plot_bgcolor='#162130',
        font={'color': '#E8EDF2'},
    )
    return fig

# --- 6. INTERFACE PRINCIPAL ---
def main():
    if 'last_analise' not in st.session_state:
        st.session_state['last_analise'] = None
    if 'last_match' not in st.session_state:
        st.session_state['last_match'] = None
    if 'selected_comp_name' not in st.session_state:
        st.session_state['selected_comp_name'] = None

    analisador = AnalisadorAutomatico()
    competitions = get_competitions()

    if not competitions:
        if FOOTBALL_DATA_API_KEY != "DEFAULT_KEY":
            st.error("❌ Não foi possível carregar as competições. Verifique sua **FOOTBALL_DATA_API_KEY** ou o limite de requisições.")
        return

    if st.session_state['selected_comp_name'] not in competitions:
        st.session_state['selected_comp_name'] = list(competitions.keys())[0]

    # ── HEADER ──
    st.markdown("# ⚽ Analisador de Apostas")
    st.markdown(
        "<p style='font-family:Barlow,sans-serif;color:#8FA3B1;font-size:0.95rem;margin-top:-0.5rem;margin-bottom:1rem;'>"
        "Análise automática · Dados reais · H2H · Odds live · Value Bets</p>",
        unsafe_allow_html=True
    )

    # Status API
    football_ok = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"
    st.markdown(
        f"<div class='api-status'>"
        f"🔑 Football API: <strong>{'✅ ' + FOOTBALL_DATA_API_KEY[:8] + '...' if football_ok else '⚠️ Não configurada'}</strong>"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"📈 Odds API: <strong>{'✅ Configurada' if odds_ok else '⚠️ Não configurada'}</strong>"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── SIDEBAR ──
    st.sidebar.markdown("## ⚙️ Configurações")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Mercados Ativos")

    market_map = {
        'btts': 'BTTS (Ambas Marcam)',
        'over25': 'Over 2.5 Gols',
        'over15': 'Over 1.5 Gols',
        'under35': 'Under 3.5 Gols',
        'under25': 'Under 2.5 Gols',
        'second_half_more': 'Mais Gols 2º Tempo'
    }

    default_markets_keys = ['btts', 'over25', 'over15', 'under35', 'second_half_more']
    default_markets_display = [market_map[k] for k in default_markets_keys]

    selected_markets_display = st.sidebar.multiselect(
        "Selecione os mercados:",
        options=list(market_map.values()),
        default=default_markets_display
    )

    reverse_market_map = {v: k for k, v in market_map.items()}
    selected_markets = [reverse_market_map[m] for m in selected_markets_display]

    risco_filter = st.sidebar.selectbox(
        "Filtro de Recomendações",
        ["Todos", "🔥 Value Bet (Odd Real > Odd Justa)", "🛡️ Baixo Risco (Prob >70%)"]
    )

    st.sidebar.markdown("---")

    with st.sidebar.expander("📋 Watchlist & Alertas"):
        new_match = st.text_input("Partida (Home vs Away)", key="new_match_input")
        if st.button("➕ Adicionar") and new_match:
            analisador.watchlist.append(new_match)
            st.session_state.watchlist = analisador.watchlist
            st.rerun()

        st.markdown("**Partidas salvas:**")
        for i, match in enumerate(analisador.watchlist):
            c1, c2 = st.columns([3, 1])
            c1.write(f"— {match}")
            if c2.button("✕", key=f"rem_{i}"):
                analisador.watchlist.pop(i)
                st.session_state.watchlist = analisador.watchlist
                st.rerun()

        if not analisador.watchlist:
            st.caption("Watchlist vazia.")

        st.markdown("---")
        email_to = st.text_input("Email para Alertas", value="seu@email.com")
        if st.button("📧 Enviar Alertas"):
            for match_str in analisador.watchlist:
                try:
                    home, away = match_str.split(" vs ")
                    analise_exemplo = {'prob_btts': 65, 'prob_over25': 70, 'prob_over15': 85, 'prob_under35': 75, 'prob_under25': 50, 'prob_second_half_more': 55}
                    analisador.send_alert({'home_team': home, 'away_team': away, 'date': datetime.now()}, analise_exemplo, email_to)
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs(["🔍 Análise de Partidas", "📊 Perfis dos Times", "📈 Histórico & Relatórios"])

    # ════════════════════════════════════════
    with tab1:
        st.markdown("## ⚽ Seleção e Análise")

        comp_col, match_col = st.columns([1, 2])
        with comp_col:
            selected_comp_name = st.selectbox(
                "Competição:",
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
                        match_date = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
                        match_options.append({
                            "id": match["id"],
                            "home_id": match["homeTeam"]["id"],
                            "away_id": match["awayTeam"]["id"],
                            "display": f"🏠 {match['homeTeam']['name']} vs 🚩 {match['awayTeam']['name']} — {match_date.strftime('%d/%m %H:%M')}",
                            "home_team": match["homeTeam"]["name"],
                            "away_team": match["awayTeam"]["name"],
                            "date": match_date
                        })
                    except:
                        continue

            if not match_options:
                st.warning("⚠️ Nenhuma partida futura encontrada.")
                selected_match = None
            else:
                selected_match_str = st.selectbox("Partida:", options=[m["display"] for m in match_options])
                match_index = [m["display"] for m in match_options].index(selected_match_str)
                selected_match = match_options[match_index]

        if selected_match:
            if st.button("🚀 Iniciar Análise Automática", use_container_width=True):
                with st.spinner(f"Analisando {selected_match['home_team']} vs {selected_match['away_team']}..."):
                    try:
                        analise = analisador.analisar_partida_automatica(
                            selected_match['home_team'], selected_match['away_team'],
                            selected_comp_name,
                            selected_match['home_id'], selected_match['away_id'],
                            competition_id, selected_markets
                        )
                        st.session_state['last_analise'] = analise
                        st.session_state['last_match'] = selected_match
                        st.success("✅ Análise concluída com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao executar a análise: {e}")

        if st.session_state['last_analise']:
            analise = st.session_state['last_analise']
            selected_match = st.session_state['last_match']

            st.markdown("---")

            # Header do resultado
            r1, r2, r3 = st.columns([5, 2, 5])
            with r1:
                st.markdown(f"<div class='result-header'>🏠 {selected_match['home_team']}</div>", unsafe_allow_html=True)
            with r2:
                st.markdown(
                    f"<div style='text-align:center;padding:0.75rem;background:#1E2D3E;border-radius:10px;"
                    f"border:1px solid #263547;font-family:Rajdhani,sans-serif;'>"
                    f"<div style='color:#8FA3B1;font-size:0.7rem;letter-spacing:0.08em;text-transform:uppercase;'>Data</div>"
                    f"<div style='color:#FFB300;font-size:1.1rem;font-weight:700;'>{selected_match['date'].strftime('%d/%m')}</div>"
                    f"<div style='color:#8FA3B1;font-size:0.85rem;'>{selected_match['date'].strftime('%H:%M')}</div>"
                    f"</div>", unsafe_allow_html=True
                )
            with r3:
                st.markdown(f"<div class='result-header'>🚩 {selected_match['away_team']}</div>", unsafe_allow_html=True)

            st.markdown("---")

            # Probabilidades
            if len(selected_markets) > 0:
                st.markdown("### 📊 Probabilidades & Odd Justa")
                cols_prob = st.columns(len(selected_markets))
                for i, market in enumerate(selected_markets):
                    prob_key = f'prob_{market}'
                    odd_key = f'odd_justa_{market}'
                    label = market_map.get(market, market.replace('_', ' ').title())
                    with cols_prob[i]:
                        if prob_key in analise:
                            fig = create_gauge_chart(analise[prob_key], label, 60)
                            st.plotly_chart(fig, use_container_width=True)
                            odd_val = analise[odd_key]
                            st.markdown(
                                f"<div style='text-align:center;margin-top:-10px;'>"
                                f"<span class='badge-gold'>Odd Justa: {odd_val}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

            st.markdown("---")

            detail_col, recomend_col = st.columns([2, 1])

            with detail_col:
                st.markdown("### 🔍 Análise Detalhada")
                for linha in analise['analise_detalhada']:
                    st.markdown(f"* {linha}")

                st.markdown("---")
                st.markdown("### 💰 Calculadora de Value Bet")
                with st.expander("Insira as Odds Reais da Casa de Apostas"):
                    if len(selected_markets) > 0:
                        num_cols = min(3, len(selected_markets))
                        value_cols = st.columns(num_cols)
                        for j, market in enumerate(selected_markets):
                            with value_cols[j % num_cols]:
                                prob = analise.get(f'prob_{market}', 0)
                                odd_justa = analise.get(f'odd_justa_{market}', 0)
                                label = market_map.get(market, market.replace('_', ' ').title())
                                odd_real = st.number_input(
                                    f"**{label}**:", min_value=1.01, value=odd_justa,
                                    step=0.01, format="%.2f", key=f"odd_real_{market}"
                                )
                                value = calculate_value_bet(prob, odd_real)
                                delta_text = "❌ SEM VALUE"
                                if value and value > 0.05:
                                    delta_text = "✅ VALUE BET FORTE!"
                                elif value and value > 0:
                                    delta_text = "✅ Value Pequeno"
                                st.metric("EV", f"{value:.3f}" if value else "—", delta=delta_text)

            with recomend_col:
                st.markdown("### 🎯 Recomendações")
                if analise['recomendacao']:
                    for rec in analise['recomendacao']:
                        st.success(rec)
                else:
                    st.info("Selecione mercados na sidebar.")

                st.markdown("---")
                st.markdown("### 💸 Odds em Tempo Real")
                live_odds = analisador.fetch_live_odds(selected_match['home_team'], selected_match['away_team'])
                if live_odds:
                    for bookie in live_odds[:2]:
                        st.subheader(f"{bookie['title']}")
                        market_totals = next((m for m in bookie.get('markets', []) if m['key'] == 'totals'), None)
                        if market_totals:
                            over_25 = next((o['price'] for o in market_totals['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Over'), 'N/A')
                            under_25 = next((o['price'] for o in market_totals['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Under'), 'N/A')
                            st.text(f"Over 2.5: @{over_25} | Under 2.5: @{under_25}")
                else:
                    st.info("Odds API não configurada.")

    # ════════════════════════════════════════
    with tab2:
        st.markdown("## 📊 Perfil dos Times")

        if st.session_state['last_match']:
            home_id = st.session_state['last_match']['home_id']
            away_id = st.session_state['last_match']['away_id']
            comp_id = competitions[st.session_state['selected_comp_name']]

            with st.spinner("Carregando perfis..."):
                home_profile = fetch_team_profile_cached(home_id, comp_id)
                away_profile = fetch_team_profile_cached(away_id, comp_id)

            home_col, away_col = st.columns(2)

            def render_profile(col, name, icon, profile):
                with col:
                    estilo = profile['estilo'].upper()
                    estilo_color = '#00C853' if estilo == 'OFENSIVO' else ('#E53935' if estilo == 'DEFENSIVO' else '#FFB300')
                    st.markdown(
                        f"<div class='match-card'>"
                        f"<h3 style='margin:0 0 0.5rem;font-family:Rajdhani,sans-serif;color:#E8EDF2;'>{icon} {name}</h3>"
                        f"<span style='background:rgba(0,0,0,0.3);border:1px solid {estilo_color};"
                        f"color:{estilo_color};font-family:Rajdhani;font-size:0.75rem;letter-spacing:0.07em;"
                        f"padding:2px 10px;border-radius:20px;text-transform:uppercase;'>{estilo}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**Ataque:** {profile['ataque']}/10")
                    st.progress(profile['ataque'] / 10)
                    st.markdown(f"**Defesa:** {profile['defesa']}/10")
                    st.progress(profile['defesa'] / 10)

                    # Mini-stats
                    m1, m2 = st.columns(2)
                    m1.metric("BTTS", f"{profile['btts']}%")
                    m2.metric("Over 2.5", f"{profile['over25']}%")
                    m3, m4 = st.columns(2)
                    m3.metric("Over 1.5", f"{profile['over15']}%")
                    m4.metric("2º Tempo +", f"{profile['second_half_more']}%")

            render_profile(home_col, st.session_state['last_match']['home_team'], "🏠", home_profile)
            render_profile(away_col, st.session_state['last_match']['away_team'], "🚩", away_profile)
        else:
            st.info("⚠️ Analise uma partida primeiro na aba **Análise de Partidas**.")

    # ════════════════════════════════════════
    with tab3:
        st.markdown("## 📈 Histórico de Análises")

        if analisador.historico_analises:
            df = pd.DataFrame(analisador.historico_analises)
            df['Prob Média'] = ((df['prob_btts'] + df['prob_over25']) / 2).round(1)
            st.dataframe(df.sort_values(by='data', ascending=False), use_container_width=True)

            st.markdown("---")
            st.markdown("### 📄 Exportar Relatório")
            pdf_report = analisador.gerar_relatorio_pdf(analisador.historico_analises)
            st.download_button(
                label="⬇️ Baixar PDF — Últimas 10 Análises",
                data=pdf_report,
                file_name="Relatorio_Analises_Futebol.pdf",
                mime="application/pdf"
            )
        else:
            st.info("O histórico está vazio. Analise uma partida para ver os dados aqui.")

if __name__ == "__main__":
    main()
