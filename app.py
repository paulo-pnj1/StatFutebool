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
import time

load_dotenv()

st.set_page_config(
    page_title="Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="collapsed"
)

# ── CSS PARA EXPERIÊNCIA INCRÍVEL ────────────────────────────────────────────
st.markdown("""
<style>
/* IMPORTAÇÃO DE FONTES MODERNAS */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* RESET E ESTILOS BASE */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, .stApp {
    font-family: 'Space Grotesk', sans-serif;
    background: #0a0a0f;
    color: #ffffff;
    scroll-behavior: smooth;
}

/* REMOVER ELEMENTOS PADRÃO */
#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"],
[data-testid="stStatusWidget"],
.stActionButton,
div[data-testid="stDecoration"] {
    display: none !important;
}

/* CONTAINER PRINCIPAL - MAXIMIZADO */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* TOP BAR SUPER SLICK */
.top-bar {
    position: sticky;
    top: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 2rem;
    background: rgba(10, 10, 15, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 75, 75, 0.2);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.logo-icon {
    font-size: 2rem;
    background: linear-gradient(135deg, #ff4b4b, #ff8c8c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 20px rgba(255, 75, 75, 0.3));
}

.logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #ff4b4b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
}

.nav-links {
    display: flex;
    gap: 0.5rem;
    background: rgba(255, 255, 255, 0.03);
    padding: 0.3rem;
    border-radius: 40px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-link {
    padding: 0.6rem 1.2rem;
    border-radius: 30px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #a0a0b0;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-link:hover {
    background: rgba(255, 75, 75, 0.1);
    color: #ffffff;
}

.nav-link.active {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: #ffffff;
    box-shadow: 0 5px 20px rgba(255, 75, 75, 0.3);
}

.status-area {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.currency-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.9rem;
    font-weight: 500;
}

.status-dots {
    display: flex;
    gap: 0.4rem;
    padding: 0.4rem 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 30px;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.dot-green { background: #4cd964; box-shadow: 0 0 15px #4cd964; animation: pulse 2s infinite; }
.dot-yellow { background: #ffcc00; box-shadow: 0 0 15px #ffcc00; }
.dot-red { background: #ff3b30; box-shadow: 0 0 15px #ff3b30; }

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.2); }
}

/* QUICK ACTIONS BAR */
.quick-actions {
    display: flex;
    gap: 0.8rem;
    padding: 1rem 2rem;
    background: rgba(20, 20, 30, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    overflow-x: auto;
    scrollbar-width: none;
}

.quick-actions::-webkit-scrollbar {
    display: none;
}

.action-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 30px;
    font-size: 0.85rem;
    color: #a0a0b0;
    white-space: nowrap;
    cursor: pointer;
    transition: all 0.2s ease;
}

.action-chip:hover {
    background: rgba(255, 75, 75, 0.1);
    border-color: rgba(255, 75, 75, 0.3);
    color: #ffffff;
    transform: translateY(-2px);
}

.action-chip.active {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: #ffffff;
    border: none;
}

/* MAIN CONTENT AREA */
.main-content {
    padding: 2rem;
    min-height: calc(100vh - 140px);
    background: radial-gradient(circle at 50% 0%, rgba(255, 75, 75, 0.05), transparent 50%);
}

/* QUICK SELECTOR CARDS */
.selector-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.selector-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.2rem;
    transition: all 0.3s ease;
    cursor: pointer;
}

.selector-card:hover {
    background: rgba(255, 75, 75, 0.05);
    border-color: rgba(255, 75, 75, 0.2);
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.selector-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.selector-icon {
    font-size: 2rem;
    background: linear-gradient(135deg, #ff4b4b, #ff8c8c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.selector-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #ffffff;
}

.selector-value {
    font-size: 0.9rem;
    color: #a0a0b0;
    margin-bottom: 0.5rem;
}

.selector-preview {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* MATCH CARDS */
.match-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.match-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.2rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.match-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ff4b4b, #ff8c8c);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}

.match-card:hover::before {
    transform: translateX(0);
}

.match-card:hover {
    background: rgba(255, 75, 75, 0.05);
    border-color: rgba(255, 75, 75, 0.2);
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.match-card.selected {
    background: rgba(255, 75, 75, 0.1);
    border-color: #ff4b4b;
    box-shadow: 0 0 30px rgba(255, 75, 75, 0.2);
}

.match-teams {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.match-team {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
}

.match-vs {
    font-size: 0.8rem;
    color: #ff4b4b;
    font-weight: 700;
}

.match-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.match-time {
    font-size: 0.8rem;
    color: #a0a0b0;
    font-family: 'JetBrains Mono', monospace;
}

.match-badge {
    padding: 0.3rem 0.8rem;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 20px;
    font-size: 0.7rem;
    color: #ff4b4b;
    font-weight: 600;
}

/* RESULT CARDS */
.result-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

.result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.result-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.result-badge {
    padding: 0.3rem 0.8rem;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 20px;
    font-size: 0.7rem;
    color: #ff4b4b;
}

/* PROBABILITY METERS */
.prob-meter {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.meter-label {
    width: 100px;
    font-size: 0.9rem;
    color: #a0a0b0;
}

.meter-bar {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    overflow: hidden;
}

.meter-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.meter-fill.high { background: linear-gradient(90deg, #4cd964, #34c759); }
.meter-fill.medium { background: linear-gradient(90deg, #ffcc00, #ffb347); }
.meter-fill.low { background: linear-gradient(90deg, #ff3b30, #ff4b4b); }

.meter-value {
    width: 50px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #ffffff;
    text-align: right;
}

/* QUICK BET PANEL */
.quick-bet-panel {
    position: sticky;
    bottom: 2rem;
    left: 2rem;
    right: 2rem;
    background: rgba(20, 20, 30, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 75, 75, 0.2);
    border-radius: 40px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    z-index: 100;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from { transform: translateY(100px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.quick-bet-info {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.quick-bet-match {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
}

.quick-bet-market {
    padding: 0.3rem 0.8rem;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 20px;
    font-size: 0.8rem;
    color: #ff4b4b;
}

.quick-bet-inputs {
    display: flex;
    gap: 0.8rem;
}

.quick-bet-input {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    padding: 0.6rem 1rem;
    color: #ffffff;
    font-size: 0.9rem;
    min-width: 100px;
}

.quick-bet-button {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: #ffffff;
    border: none;
    border-radius: 30px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.quick-bet-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(255, 75, 75, 0.4);
}

/* LOADING ANIMATIONS */
@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.loading {
    background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

/* RESPONSIVIDADE PERFEITA */
@media (max-width: 1024px) {
    .nav-links { display: none; }
    .quick-actions { padding: 0.8rem 1rem; }
    .main-content { padding: 1rem; }
    .match-grid { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
}

@media (max-width: 768px) {
    .top-bar { padding: 0.6rem 1rem; }
    .logo-text { font-size: 1.2rem; }
    .currency-badge { padding: 0.3rem 0.8rem; font-size: 0.8rem; }
    .quick-bet-panel { 
        flex-direction: column;
        border-radius: 20px;
        margin: 1rem;
    }
    .quick-bet-info { width: 100%; }
    .quick-bet-inputs { width: 100%; flex-wrap: wrap; }
    .quick-bet-input { flex: 1; }
}

@media (max-width: 480px) {
    .logo-text { display: none; }
    .status-dots { display: none; }
    .selector-grid { grid-template-columns: 1fr; }
    .match-grid { grid-template-columns: 1fr; }
}

/* SCROLLBAR CUSTOMIZADA */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff4b4b, #ff8c8c);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ff6b6b, #ff9f9f);
}

/* TOOLTIPS */
[data-tooltip] {
    position: relative;
    cursor: help;
}

[data-tooltip]:before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 0.4rem 0.8rem;
    background: rgba(20, 20, 30, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 75, 75, 0.2);
    border-radius: 10px;
    font-size: 0.7rem;
    color: #ffffff;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    pointer-events: none;
    z-index: 1000;
}

[data-tooltip]:hover:before {
    opacity: 1;
    visibility: visible;
    bottom: 150%;
}

/* ANIMAÇÕES DE ENTRADA */
.fade-in {
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.slide-in {
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* HOVER EFFECTS */
.hover-lift {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* GLASS MORPHISM */
.glass {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* NEON EFFECTS */
.neon-text {
    text-shadow: 0 0 10px rgba(255, 75, 75, 0.5);
}

.neon-border {
    box-shadow: 0 0 20px rgba(255, 75, 75, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY, "Accept": "application/json"}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS = "https://api.the-odds-api.com/v4"

MARKET_MAP = {
    'btts': 'BTTS',
    'over25': 'Over 2.5',
    'over15': 'Over 1.5',
    'under35': 'Under 3.5',
    'under25': 'Under 2.5',
    'second_half_more': '2º Tempo +'
}

THRESHOLDS = {'btts': 60, 'over25': 60, 'over15': 80, 'under35': 70, 'under25': 60, 'second_half_more': 60}

CURRENCIES = {
    'AOA': {'symbol': 'Kz', 'flag': '🇦🇴', 'name': 'Kwanza'},
    'EUR': {'symbol': '€', 'flag': '🇪🇺', 'name': 'Euro'},
    'BRL': {'symbol': 'R$', 'flag': '🇧🇷', 'name': 'Real'},
    'USD': {'symbol': '$', 'flag': '🇺🇸', 'name': 'Dólar'},
}

# ── FUNÇÕES UTILITÁRIAS ──────────────────────────────────────────────────────
def fmt_money(value, currency_key):
    c = CURRENCIES.get(currency_key, CURRENCIES['EUR'])
    return f"{c['symbol']}{value:,.2f}"

def calculate_value_bet(real_prob, odd):
    if not odd or odd <= 0 or not real_prob:
        return None
    return round((odd * (real_prob / 100)) - 1, 3)

def get_total_goals(m):
    return (m['score']['fullTime'].get('home', 0) or 0) + (m['score']['fullTime'].get('away', 0) or 0)

def get_home_goals(m):
    return m['score']['fullTime'].get('home', 0) or 0

def get_away_goals(m):
    return m['score']['fullTime'].get('away', 0) or 0

def get_fh_goals(m):
    return (m['score']['halfTime'].get('home', 0) or 0) + (m['score']['halfTime'].get('away', 0) or 0)

def get_sh_goals(m):
    return get_total_goals(m) - get_fh_goals(m)

def mc_cls(p, t):
    return "high" if p >= t else "medium" if p >= t - 10 else "low"

# ── API FUNCTIONS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_fd(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        r = requests.get(f"{BASE_URL_FOOTBALL}/{endpoint}", headers=HEADERS_FOOTBALL, timeout=15)
        if r.status_code == 429:
            st.error("❌ Rate limit atingido.")
            return None
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_fd("competitions")
    if not data or "competitions" not in data:
        return {}
    top = ["Premier League", "Primera Division", "Serie A", "Bundesliga", "Ligue 1",
           "Primeira Liga", "Eredivisie", "Jupiler Pro League", "Scottish Premiership",
           "UEFA Champions League", "UEFA Europa League", "UEFA Conference League"]
    return {c["name"]: c["id"] for c in data["competitions"] if c["name"] in top and c.get("currentSeason")}

@st.cache_data(ttl=600)
def get_matches(comp_id):
    today = datetime.now().strftime("%Y-%m-%d")
    nw = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_fd(f"competitions/{comp_id}/matches?dateFrom={today}&dateTo={nw}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile(team_id, comp_id):
    p = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado', 'over25': 50, 'btts': 50, 
         'over15': 70, 'under35': 70, 'under25': 50, 'second_half_more': 50}
    try:
        sd = fetch_fd(f"competitions/{comp_id}/standings")
        if sd and 'standings' in sd:
            for g in sd['standings']:
                for t in g['table']:
                    if t['team']['id'] == team_id:
                        pg, gf, ga = t['playedGames'], t['goalsFor'], t['goalsAgainst']
                        if pg > 0:
                            p['ataque'] = min(10, max(1, round((gf / pg / 1.4) * 7 + 1)))
                            p['defesa'] = min(10, max(1, round((1.4 / max(ga / pg, 0.1)) * 7 + 1)))
                        break
        md = fetch_fd(f"teams/{team_id}/matches?status=FINISHED&limit=10")
        if md and 'matches' in md:
            rm = md['matches'][:10]
            if rm:
                n = len(rm)
                p['over25'] = round(sum(1 for m in rm if get_total_goals(m) > 2.5) / n * 100)
                p['btts'] = round(sum(1 for m in rm if get_home_goals(m) > 0 and get_away_goals(m) > 0) / n * 100)
                p['over15'] = round(sum(1 for m in rm if get_total_goals(m) > 1.5) / n * 100)
                p['under35'] = round(sum(1 for m in rm if get_total_goals(m) < 3.5) / n * 100)
                p['under25'] = round(sum(1 for m in rm if get_total_goals(m) < 2.5) / n * 100)
                p['second_half_more'] = round(sum(1 for m in rm if get_sh_goals(m) > get_fh_goals(m)) / n * 100)
        a, d = p['ataque'], p['defesa']
        p['estilo'] = 'ofensivo' if a >= 7 and d <= 6 else 'defensivo' if d >= 7 and a <= 6 else 'equilibrado'
        return p
    except Exception:
        return p

# ── ANALISADOR ────────────────────────────────────────────────────────────────
class Analisador:
    def __init__(self):
        for k, v in [('watchlist', []), ('historico', []), ('quick_markets', ['btts', 'over25']), 
                     ('favorite_competition', None), ('quick_stake', 10.0)]:
            if k not in st.session_state:
                st.session_state[k] = v
        self.watchlist = st.session_state.watchlist
        self.historico = st.session_state.historico
        self.quick_markets = st.session_state.quick_markets
        self.favorite_competition = st.session_state.favorite_competition
        self.quick_stake = st.session_state.quick_stake

    @st.cache_data(ttl=3600)
    def fetch_h2h(_self, hid, aid, limit=5):
        try:
            hm = fetch_fd(f"teams/{hid}/matches?status=FINISHED&limit=20")
            h2h = []
            if hm and 'matches' in hm:
                for m in hm['matches']:
                    if m.get('awayTeam', {}).get('id') == aid or m.get('homeTeam', {}).get('id') == aid:
                        h2h.append(m)
                        if len(h2h) >= limit:
                            break
            n = max(len(h2h), 1)
            return {
                'btts_h2h': sum(1 for m in h2h if get_home_goals(m) > 0 and get_away_goals(m) > 0) / n * 100,
                'over25_h2h': sum(1 for m in h2h if get_total_goals(m) > 2.5) / n * 100
            }
        except Exception:
            return {'btts_h2h': 50, 'over25_h2h': 50}

    def fetch_live_odds(self, ht, at):
        try:
            if ODDS_API_KEY == "sua_chave_the_odds_api":
                return []
            r = requests.get(f"{BASE_URL_ODDS}/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h,totals", timeout=10)
            if r.status_code == 200:
                for ev in r.json():
                    if ht.lower() in ev['home_team'].lower() and at.lower() in ev['away_team'].lower():
                        return ev.get('bookmakers', [])
            return []
        except Exception:
            return []

    def ajustes_estilo(self, hp, ap):
        aj = {k: 0 for k in MARKET_MAP}
        hs, as_ = hp['estilo'], ap['estilo']
        if hs == 'ofensivo' and as_ == 'ofensivo':
            aj.update({'btts': 8, 'over25': 12, 'over15': 5, 'under35': -10, 'under25': -8, 'second_half_more': 5})
        elif hs == 'defensivo' and as_ == 'defensivo':
            aj.update({'btts': -10, 'over25': -15, 'over15': -5, 'under35': 12, 'under25': 10, 'second_half_more': -5})
        elif 'ofensivo' in [hs, as_]:
            aj.update({'btts': 3, 'over25': 2, 'over15': 2, 'under35': -3, 'under25': -2, 'second_half_more': 3})
        if hp['ataque'] >= 8 and ap['defesa'] <= 5:
            aj['btts'] += 5
            aj['over25'] += 8
            aj['over15'] += 4
            aj['under35'] -= 6
            aj['under25'] -= 5
            aj['second_half_more'] += 4
        if ap['ataque'] >= 8 and hp['defesa'] <= 5:
            aj['btts'] += 5
            aj['over25'] += 8
            aj['over15'] += 4
            aj['under35'] -= 6
            aj['under25'] -= 5
            aj['second_half_more'] += 4
        return aj

    def ajustes_comp(self, competition):
        aj = {k: 0 for k in MARKET_MAP}
        if 'Premier League' in competition:
            aj.update({'over25': 5, 'over15': 3, 'under35': -2, 'under25': -1, 'second_half_more': 2})
        elif 'Serie A' in competition:
            aj.update({'btts': -3, 'over25': -2, 'over15': -1, 'under35': 4, 'under25': 3, 'second_half_more': -2})
        elif 'Bundesliga' in competition:
            aj.update({'btts': 5, 'over25': 8, 'over15': 5, 'under35': -8, 'under25': -7, 'second_half_more': 5})
        return aj

    def analisar(self, ht, at, competition, hid, aid, comp_id, markets):
        with st.spinner("🔮 Analisando dados em tempo real..."):
            time.sleep(0.5)  # Feedback visual
            hp = fetch_team_profile(hid, comp_id)
            ap = fetch_team_profile(aid, comp_id)
            h2h = self.fetch_h2h(hid, aid)
            aj = self.ajustes_estilo(hp, ap)
            ajc = self.ajustes_comp(competition)

            def calc(b, k, lo, hi, h2=0):
                return min(hi, max(lo, b + aj[k] + ajc[k] + h2))

            probs = {
                'btts': calc((hp['btts'] + ap['btts']) / 2, 'btts', 15, 85, (h2h['btts_h2h'] - 50) / 10),
                'over25': calc((hp['over25'] + ap['over25']) / 2, 'over25', 20, 80, (h2h['over25_h2h'] - 50) / 10),
                'over15': calc((hp['over15'] + ap['over15']) / 2, 'over15', 40, 95),
                'under35': calc((hp['under35'] + ap['under35']) / 2, 'under35', 30, 90),
                'under25': calc((hp['under25'] + ap['under25']) / 2, 'under25', 25, 85),
                'second_half_more': calc((hp['second_half_more'] + ap['second_half_more']) / 2, 'second_half_more', 20, 80)
            }

            res = {f'prob_{k}': round(v, 1) for k, v in probs.items()}
            res.update({f'odd_justa_{k}': round(100 / v, 2) for k, v in probs.items()})
            res['h2h'] = h2h
            res['home_profile'] = hp
            res['away_profile'] = ap
            res['recomendacoes'] = self._recs(probs, markets)

            self.historico.append({
                'home': ht,
                'away': at,
                'mercado_escolhido': markets[0] if markets else '',
                'probs': {k: round(v, 1) for k, v in probs.items()},
                'data': datetime.now().strftime('%d/%m %H:%M'),
                'timestamp': datetime.now()
            })
            st.session_state.historico = self.historico
            return res

    def _recs(self, probs, markets):
        icons = {'btts': '🎯', 'over25': '⚽', 'over15': '⚽', 'under35': '🛡️', 'under25': '🛡️', 'second_half_more': '⏱️'}
        recs = []
        for k, v in probs.items():
            if k not in markets:
                continue
            t = THRESHOLDS[k]
            recs.append({
                'key': k,
                'icon': icons[k],
                'label': MARKET_MAP[k],
                'prob': v,
                'class': 'high' if v >= t else 'medium' if v >= t - 10 else 'low'
            })
        return recs

    def gerar_pdf(self, currency_key='EUR'):
        c = CURRENCIES.get(currency_key, CURRENCIES['EUR'])
        pdf = FPDF()
        pdf.add_page()
        
        def clean_text(text):
            if not isinstance(text, str):
                text = str(text)
            text = text.replace('🏠', 'Home: ').replace('🚩', 'Away: ')
            text = text.replace('⚽', '[F] ').replace('🎯', '[T] ')
            text = ''.join(char for char in text if ord(char) < 256 or char in '€$R$Kz')
            return text.encode('latin-1', errors='ignore').decode('latin-1')
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 9, clean_text(f"Bet Analyzer Report"), ln=1, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=9)
        pdf.cell(200, 6, clean_text(f"Total bets: {len(self.historico)}"), ln=1)
        pdf.ln(3)
        
        MMAP = {"btts": "BTTS", "over25": "Over 2.5", "over15": "Over 1.5",
                "under35": "Under 3.5", "under25": "Under 2.5", "second_half_more": "2o Tempo+"}
        
        for a in list(reversed(self.historico))[-20:]:
            mkey = a.get('mercado_escolhido', '')
            mlabel = MMAP.get(mkey, mkey.upper())
            prob_m = a.get('probs', {}).get(mkey, 0)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(200, 6, clean_text(f"{a['home']} vs {a['away']}"), ln=1)
            pdf.set_font("Arial", size=8)
            pdf.cell(200, 5, clean_text(f"  {a['data']} | {mlabel} | {prob_m:.0f}%"), ln=1)
            pdf.ln(2)
        
        return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ── INTERFACE PRINCIPAL ──────────────────────────────────────────────────────
def main():
    # Inicializar session state
    for k, v in [('last_analise', None), ('last_match', None), ('currency', 'EUR'), 
                 ('current_page', 'analyze'), ('selected_match_id', None)]:
        if k not in st.session_state:
            st.session_state[k] = v

    an = Analisador()
    comps = get_competitions()
    curr = st.session_state['currency']
    c_info = CURRENCIES.get(curr, CURRENCIES['EUR'])

    # Status das APIs
    api_ok = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"
    email_ok = bool(EMAIL_USER and EMAIL_PASS)

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="top-bar">
        <div class="logo-area">
            <span class="logo-icon">⚽</span>
            <span class="logo-text">Bet Analyzer</span>
        </div>
        
        <div class="nav-links">
            <div class="nav-link {'active' if st.session_state.current_page == 'analyze' else ''}" 
                 onclick="document.querySelector('[data-page=\"analyze\"]').click()">
                🔍 Análise
            </div>
            <div class="nav-link {'active' if st.session_state.current_page == 'profiles' else ''}"
                 onclick="document.querySelector('[data-page=\"profiles\"]').click()">
                📊 Perfis
            </div>
            <div class="nav-link {'active' if st.session_state.current_page == 'history' else ''}"
                 onclick="document.querySelector('[data-page=\"history\"]').click()">
                📈 Histórico
            </div>
        </div>
        
        <div class="status-area">
            <div class="currency-badge" data-tooltip="Moeda atual">
                {c_info['flag']} {curr} {c_info['symbol']}
            </div>
            <div class="status-dots">
                <div class="dot {'dot-green' if api_ok else 'dot-red'}" data-tooltip="Football API"></div>
                <div class="dot {'dot-green' if odds_ok else 'dot-yellow'}" data-tooltip="Odds API"></div>
                <div class="dot {'dot-green' if email_ok else 'dot-yellow'}" data-tooltip="Email"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botões invisíveis para navegação
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("analyze", key="nav_analyze", use_container_width=True):
            st.session_state.current_page = 'analyze'
            st.rerun()
    with col2:
        if st.button("profiles", key="nav_profiles", use_container_width=True):
            st.session_state.current_page = 'profiles'
            st.rerun()
    with col3:
        if st.button("history", key="nav_history", use_container_width=True):
            st.session_state.current_page = 'history'
            st.rerun()

    # ── QUICK ACTIONS ─────────────────────────────────────────────────────────
    if comps:
        comp_list = list(comps.keys())
        favorite_idx = comp_list.index(an.favorite_competition) if an.favorite_competition in comp_list else 0
        
        st.markdown("""
        <div class="quick-actions">
            <div class="action-chip active" data-tooltip="Competição favorita">
                ⚽ Premier League
            </div>
            <div class="action-chip" data-tooltip="Mercados rápidos">
                🎯 BTTS
            </div>
            <div class="action-chip" data-tooltip="Mercados rápidos">
                ⚽ Over 2.5
            </div>
            <div class="action-chip" data-tooltip="Watchlist">
                📋 Favoritos
            </div>
            <div class="action-chip" data-tooltip="Exportar">
                📥 PDF
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── MAIN CONTENT ──────────────────────────────────────────────────────────
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Seletor de competição e partida (sempre visível)
    if comps:
        comp_list = list(comps.keys())
        selected_comp = st.selectbox(
            "Competição",
            comp_list,
            index=comp_list.index(an.favorite_competition) if an.favorite_competition in comp_list else 0,
            key="comp_selector",
            label_visibility="collapsed"
        )
        
        if an.favorite_competition != selected_comp:
            an.favorite_competition = selected_comp
            st.session_state.favorite_competition = selected_comp

        comp_id = comps[selected_comp]

        # Buscar partidas com loading otimizado
        with st.spinner("🔍 Buscando partidas..."):
            matches = get_matches(comp_id)

        # Cards de partidas
        st.markdown('<div class="match-grid">', unsafe_allow_html=True)
        
        match_options = []
        for m in matches:
            if m["status"] in ["SCHEDULED", "TIMED"]:
                try:
                    dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    match_data = {
                        "id": m["id"],
                        "home_id": m["homeTeam"]["id"],
                        "away_id": m["awayTeam"]["id"],
                        "home_team": m["homeTeam"]["name"],
                        "away_team": m["awayTeam"]["name"],
                        "date": dt,
                        "time": dt.strftime('%H:%M'),
                        "day": dt.strftime('%d/%m')
                    }
                    match_options.append(match_data)
                    
                    # Renderizar card
                    selected_class = "selected" if st.session_state.selected_match_id == m["id"] else ""
                    st.markdown(f"""
                    <div class="match-card {selected_class}" onclick="document.querySelector('[data-match=\"{m['id']}\"]').click()">
                        <div class="match-teams">
                            <span class="match-team">{m['homeTeam']['name'][:20]}</span>
                            <span class="match-vs">VS</span>
                            <span class="match-team">{m['awayTeam']['name'][:20]}</span>
                        </div>
                        <div class="match-info">
                            <span class="match-time">{dt.strftime('%d/%m %H:%M')}</span>
                            <span class="match-badge">⚽ Ao Vivo</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botão invisível para seleção
                    if st.button("select", key=f"select_{m['id']}"):
                        st.session_state.selected_match_id = m["id"]
                        st.session_state.last_match = match_data
                        st.rerun()
                        
                except:
                    continue
                    
        st.markdown('</div>', unsafe_allow_html=True)

    # ── PAINEL DE APOSTA RÁPIDA ──────────────────────────────────────────────
    if st.session_state.last_match:
        match = st.session_state.last_match
        
        st.markdown(f"""
        <div class="quick-bet-panel">
            <div class="quick-bet-info">
                <span class="quick-bet-match">{match['home_team']} vs {match['away_team']}</span>
                <span class="quick-bet-market">BTTS</span>
            </div>
            <div class="quick-bet-inputs">
                <input type="number" class="quick-bet-input" placeholder="Odd" value="2.00" step="0.01">
                <input type="number" class="quick-bet-input" placeholder="Stake {c_info['symbol']}" value="{an.quick_stake:.2f}" step="1.00">
                <button class="quick-bet-button">⚡ Analisar Rápido</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CONTEÚDO DAS PÁGINAS ─────────────────────────────────────────────────
    if st.session_state.current_page == 'analyze' and st.session_state.last_analise:
        analise = st.session_state.last_analise
        match = st.session_state.last_match
        
        st.markdown(f"""
        <div class="result-card fade-in">
            <div class="result-header">
                <div class="result-title">
                    <span>📊 Resultados da Análise</span>
                    <span class="result-badge">⚡ Tempo Real</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas principais
        cols = st.columns(3)
        markets_to_show = ['btts', 'over25', 'over15']
        for i, market in enumerate(markets_to_show):
            if market in analise:
                prob = analise[f'prob_{market}']
                cls = mc_cls(prob, THRESHOLDS[market])
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="mv" style="color: {'#4cd964' if cls=='high' else '#ffcc00' if cls=='medium' else '#ff3b30'}">
                            {prob:.0f}%
                        </div>
                        <div class="ml">{MARKET_MAP[market]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Barras de probabilidade
        st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
        for market in ['btts', 'over25', 'over15', 'under35', 'under25', 'second_half_more']:
            if market in analise:
                prob = analise[f'prob_{market}']
                cls = mc_cls(prob, THRESHOLDS[market])
                st.markdown(f"""
                <div class="prob-meter">
                    <span class="meter-label">{MARKET_MAP[market]}</span>
                    <div class="meter-bar">
                        <div class="meter-fill {cls}" style="width: {prob}%;"></div>
                    </div>
                    <span class="meter-value">{prob:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_page == 'profiles' and st.session_state.last_match:
        match = st.session_state.last_match
        comp_id = comps[st.session_state.favorite_competition]
        
        with st.spinner("🔍 Carregando perfis detalhados..."):
            hp = fetch_team_profile(match['home_id'], comp_id)
            ap = fetch_team_profile(match['away_id'], comp_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">🏠 {match['home_team']}</div>
                    <span class="result-badge">{hp['estilo'].upper()}</span>
                </div>
            """, unsafe_allow_html=True)
            
            for label, key in [("Ataque", "ataque"), ("Defesa", "defesa")]:
                val = hp[key]
                cls = "high" if val >= 7 else "medium" if val >= 5 else "low"
                st.markdown(f"""
                <div class="prob-meter">
                    <span class="meter-label">{label}</span>
                    <div class="meter-bar">
                        <div class="meter-fill {cls}" style="width: {val*10}%;"></div>
                    </div>
                    <span class="meter-value">{val}/10</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">🚩 {match['away_team']}</div>
                    <span class="result-badge">{ap['estilo'].upper()}</span>
                </div>
            """, unsafe_allow_html=True)
            
            for label, key in [("Ataque", "ataque"), ("Defesa", "defesa")]:
                val = ap[key]
                cls = "high" if val >= 7 else "medium" if val >= 5 else "low"
                st.markdown(f"""
                <div class="prob-meter">
                    <span class="meter-label">{label}</span>
                    <div class="meter-bar">
                        <div class="meter-fill {cls}" style="width: {val*10}%;"></div>
                    </div>
                    <span class="meter-value">{val}/10</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.current_page == 'history':
        if an.historico:
            st.markdown(f"""
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">📈 Últimas Análises</div>
                    <span class="result-badge">{len(an.historico)} total</span>
                </div>
            """, unsafe_allow_html=True)
            
            for entry in reversed(an.historico[-10:]):
                st.markdown(f"""
                <div class="hist-card">
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">{entry['home']} vs {entry['away']}</div>
                        <div style="font-size: 0.8rem; color: #a0a0b0;">{entry['data']}</div>
                    </div>
                    <div style="display: flex; gap: 1rem;">
                        <span style="color: #ff4b4b;">{entry.get('mercado_escolhido', 'N/A')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão de exportação
            if st.button("📥 Exportar Histórico PDF", use_container_width=True):
                pdf_data = an.gerar_pdf(curr)
                st.download_button(
                    "📥 Download PDF",
                    data=pdf_data,
                    file_name="bet_analyzer_history.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="result-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <div style="font-size: 1.2rem; color: #a0a0b0;">Nenhuma análise no histórico</div>
                <div style="margin-top: 1rem; color: #666688;">Faça uma análise para começar</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
