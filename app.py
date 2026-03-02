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
}

/* REMOVER ELEMENTOS PADRÃO */
#MainMenu, footer, header, .stDeployButton,
[data-testid="collapsedControl"],
[data-testid="stStatusWidget"],
.stActionButton,
div[data-testid="stDecoration"] {
    display: none !important;
}

/* CONTAINER PRINCIPAL */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* TOP BAR */
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
}

.logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #ff4b4b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* BOTÕES DE NAVEGAÇÃO */
.stButton button {
    border-radius: 30px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b) !important;
    color: white !important;
    border: none !important;
}

.stButton button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.03) !important;
    color: #a0a0b0 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 75, 75, 0.3);
}

/* STATUS AREA */
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
}

.dot-green { background: #4cd964; box-shadow: 0 0 10px #4cd964; }
.dot-yellow { background: #ffcc00; box-shadow: 0 0 10px #ffcc00; }
.dot-red { background: #ff3b30; box-shadow: 0 0 10px #ff3b30; }

/* QUICK ACTIONS */
.quick-actions {
    display: flex;
    gap: 0.8rem;
    padding: 1rem 2rem;
    background: rgba(20, 20, 30, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    overflow-x: auto;
}

.quick-action {
    padding: 0.6rem 1.2rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 30px;
    color: #a0a0b0;
    font-size: 0.85rem;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.quick-action:hover {
    background: rgba(255, 75, 75, 0.1);
    border-color: rgba(255, 75, 75, 0.3);
    color: #ffffff;
}

.quick-action.active {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: #ffffff;
    border: none;
}

/* MAIN CONTENT */
.main-content {
    padding: 2rem;
    min-height: calc(100vh - 140px);
}

/* SELECTOR CARD */
.selector-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

/* MATCH GRID */
.match-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.match-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.2rem;
    transition: all 0.2s ease;
}

.match-card:hover {
    background: rgba(255, 75, 75, 0.05);
    border-color: rgba(255, 75, 75, 0.2);
    transform: translateY(-2px);
}

.match-card.selected {
    background: rgba(255, 75, 75, 0.1);
    border-color: #ff4b4b;
    box-shadow: 0 0 20px rgba(255, 75, 75, 0.2);
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
    color: #ff4b4b;
    font-weight: 700;
    font-size: 0.9rem;
}

.match-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.match-time {
    font-size: 0.8rem;
    color: #a0a0b0;
    font-family: 'JetBrains Mono', monospace;
}

.match-badge {
    padding: 0.2rem 0.8rem;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 20px;
    font-size: 0.7rem;
    color: #ff4b4b;
}

/* RESULT CARD */
.result-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.result-title {
    font-size: 1.2rem;
    font-weight: 600;
    color: #ffffff;
}

.result-badge {
    padding: 0.3rem 1rem;
    background: rgba(255, 75, 75, 0.1);
    border-radius: 30px;
    font-size: 0.8rem;
    color: #ff4b4b;
}

/* METRIC GRID */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1rem;
    text-align: center;
}

.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.3rem;
}

.metric-card .label {
    font-size: 0.8rem;
    color: #a0a0b0;
}

/* PROBABILITY METER */
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
    transition: width 0.3s ease;
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
    position: fixed;
    bottom: 2rem;
    left: 2rem;
    right: 2rem;
    background: rgba(20, 20, 30, 0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 75, 75, 0.2);
    border-radius: 40px;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    z-index: 100;
    animation: slideUp 0.3s ease;
}

@keyframes slideUp {
    from { transform: translateY(100px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.quick-bet-info {
    flex: 1;
}

.quick-bet-match {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.2rem;
}

.quick-bet-market {
    font-size: 0.8rem;
    color: #ff4b4b;
}

.quick-bet-inputs {
    display: flex;
    gap: 1rem;
    align-items: center;
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
    color: white;
    border: none;
    border-radius: 30px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

.quick-bet-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
}

/* RESPONSIVIDADE */
@media (max-width: 768px) {
    .top-bar { padding: 0.6rem 1rem; }
    .logo-text { font-size: 1.2rem; }
    .quick-actions { padding: 0.8rem 1rem; }
    .main-content { padding: 1rem; }
    .match-grid { grid-template-columns: 1fr; }
    .metric-grid { grid-template-columns: 1fr; }
    .quick-bet-panel { 
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
    }
    .quick-bet-inputs { width: 100%; }
}

/* ANIMAÇÕES */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.3s ease;
}

/* STREAMLIT OVERRIDES */
.stSelectbox, .stMultiSelect, .stNumberInput {
    margin-bottom: 1rem;
}

.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: white !important;
}

.stAlert {
    background: rgba(255, 75, 75, 0.1) !important;
    border: 1px solid rgba(255, 75, 75, 0.2) !important;
    color: white !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── CONFIGURAÇÕES ────────────────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
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
    'EUR': {'symbol': '€', 'flag': '🇪🇺', 'name': 'Euro'},
    'BRL': {'symbol': 'R$', 'flag': '🇧🇷', 'name': 'Real'},
    'USD': {'symbol': '$', 'flag': '🇺🇸', 'name': 'Dólar'},
    'AOA': {'symbol': 'Kz', 'flag': '🇦🇴', 'name': 'Kwanza'},
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

# ── API FUNCTIONS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_fd(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        r = requests.get(f"{BASE_URL_FOOTBALL}/{endpoint}", headers=HEADERS_FOOTBALL, timeout=10)
        if r.status_code == 429:
            st.error("❌ Rate limit atingido.")
            return None
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_fd("competitions")
    if not data or "competitions" not in data:
        return {}
    top = ["Premier League", "Primera Division", "Serie A", "Bundesliga", "Ligue 1",
           "Primeira Liga", "Eredivisie", "UEFA Champions League"]
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
        if 'historico' not in st.session_state:
            st.session_state.historico = []
        self.historico = st.session_state.historico

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
            time.sleep(0.5)
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
                'probs': {k: round(v, 1) for k, v in probs.items()},
                'data': datetime.now().strftime('%d/%m %H:%M')
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
            pdf.set_font("Arial", "B", 9)
            pdf.cell(200, 6, clean_text(f"{a['home']} vs {a['away']}"), ln=1)
            pdf.set_font("Arial", size=8)
            pdf.cell(200, 5, clean_text(f"  {a['data']}"), ln=1)
            pdf.ln(2)
        
        return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ── INTERFACE PRINCIPAL ──────────────────────────────────────────────────────
def main():
    # Inicializar session state
    if 'page' not in st.session_state:
        st.session_state.page = 'analyze'
    if 'selected_match' not in st.session_state:
        st.session_state.selected_match = None
    if 'currency' not in st.session_state:
        st.session_state.currency = 'EUR'
    if 'analysis' not in st.session_state:
        st.session_state.analysis = None
    if 'selected_markets' not in st.session_state:
        st.session_state.selected_markets = ['btts', 'over25', 'over15']

    an = Analisador()
    comps = get_competitions()
    c_info = CURRENCIES[st.session_state.currency]

    # Status das APIs
    api_ok = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"
    odds_ok = ODDS_API_KEY != "sua_chave_the_odds_api"

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 2rem;">⚽</span>
            <span style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #fff, #ff4b4b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Bet Analyzer</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🔍 Análise", key="nav_analyze", use_container_width=True, 
                        type="primary" if st.session_state.page == 'analyze' else "secondary"):
                st.session_state.page = 'analyze'
                st.rerun()
        with b2:
            if st.button("📊 Perfis", key="nav_profiles", use_container_width=True,
                        type="primary" if st.session_state.page == 'profiles' else "secondary"):
                st.session_state.page = 'profiles'
                st.rerun()
        with b3:
            if st.button("📈 Histórico", key="nav_history", use_container_width=True,
                        type="primary" if st.session_state.page == 'history' else "secondary"):
                st.session_state.page = 'history'
                st.rerun()
    
    with col3:
        col_curr, col_dots = st.columns([1, 1])
        with col_curr:
            currency_opts = [f"{v['flag']} {k}" for k, v in CURRENCIES.items()]
            curr_idx = list(CURRENCIES.keys()).index(st.session_state.currency)
            selected = st.selectbox("Moeda", currency_opts, index=curr_idx, label_visibility="collapsed", key="currency_sel")
            new_curr = list(CURRENCIES.keys())[currency_opts.index(selected)]
            if new_curr != st.session_state.currency:
                st.session_state.currency = new_curr
                st.rerun()
        
        with col_dots:
            st.markdown(f"""
            <div style="display: flex; gap: 0.3rem; justify-content: flex-end;">
                <div class="dot {'dot-green' if api_ok else 'dot-red'}" title="Football API"></div>
                <div class="dot {'dot-green' if odds_ok else 'dot-yellow'}" title="Odds API"></div>
            </div>
            """, unsafe_allow_html=True)

    # ── QUICK ACTIONS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display: flex; gap: 0.5rem; padding: 1rem 0; overflow-x: auto; margin-bottom: 1rem;">
        <div class="quick-action active">⚽ Premier League</div>
        <div class="quick-action">🎯 BTTS</div>
        <div class="quick-action">⚽ Over 2.5</div>
        <div class="quick-action">📋 Favoritos</div>
        <div class="quick-action">📥 Exportar PDF</div>
    </div>
    """, unsafe_allow_html=True)

    # ── MAIN CONTENT ──────────────────────────────────────────────────────────
    
    # Seletor de mercados
    with st.expander("⚙️ Configurar Mercados", expanded=False):
        market_options = list(MARKET_MAP.values())
        selected_markets_display = st.multiselect(
            "Selecione os mercados para análise",
            market_options,
            default=[MARKET_MAP[m] for m in st.session_state.selected_markets if m in MARKET_MAP]
        )
        rev_map = {v: k for k, v in MARKET_MAP.items()}
        st.session_state.selected_markets = [rev_map[m] for m in selected_markets_display if m in rev_map]

    # Seletor de competição e partida
    if comps:
        comp_list = list(comps.keys())
        selected_comp = st.selectbox(
            "Competição",
            comp_list,
            index=0,
            key="comp_selector"
        )

        comp_id = comps[selected_comp]

        # Buscar partidas
        with st.spinner("🔍 Carregando partidas..."):
            matches = get_matches(comp_id)

        # Grid de partidas
        st.markdown('<div class="match-grid">', unsafe_allow_html=True)
        
        match_found = False
        for m in matches[:12]:  # Limitar para performance
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
                    match_found = True
                    
                    # Criar card para cada partida
                    with st.container():
                        selected_class = "selected" if st.session_state.selected_match and st.session_state.selected_match.get('id') == m["id"] else ""
                        
                        if st.button(
                            f"**{match_data['home_team']}** vs **{match_data['away_team']}**\n\n{match_data['day']} {match_data['time']}",
                            key=f"match_{m['id']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_match = match_data
                            st.rerun()
                            
                except Exception as e:
                    continue
        
        if not match_found:
            st.info("Nenhuma partida encontrada para esta competição.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ── PAINEL DE APOSTA RÁPIDA ──────────────────────────────────────────────
    if st.session_state.selected_match:
        match = st.session_state.selected_match
        
        st.markdown("---")
        col_odd, col_stake, col_btn = st.columns([2, 2, 3])
        
        with col_odd:
            odd = st.number_input("Odd", min_value=1.01, value=2.00, step=0.05, format="%.2f")
        
        with col_stake:
            stake = st.number_input(f"Stake ({c_info['symbol']})", min_value=0.0, value=10.0, step=1.0, format="%.2f")
        
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 ANALISAR PARTIDA", use_container_width=True):
                with st.spinner("🔮 Processando análise..."):
                    result = an.analisar(
                        match['home_team'], match['away_team'],
                        selected_comp, match['home_id'], match['away_id'],
                        comp_id, st.session_state.selected_markets
                    )
                    st.session_state.analysis = result
                    st.rerun()

    # ── CONTEÚDO DAS PÁGINAS ─────────────────────────────────────────────────
    
    if st.session_state.page == 'analyze' and st.session_state.analysis:
        analise = st.session_state.analysis
        
        st.markdown("""
        <div class="result-card fade-in">
            <div class="result-header">
                <div class="result-title">📊 Resultados da Análise</div>
                <span class="result-badge">⚡ Tempo Real</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Métricas principais
        cols = st.columns(3)
        markets_show = ['btts', 'over25', 'over15']
        for i, market in enumerate(markets_show):
            if market in analise:
                prob = analise[f'prob_{market}']
                with cols[i]:
                    st.metric(MARKET_MAP[market], f"{prob:.0f}%")
        
        # Barras de probabilidade
        st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
        
        for market in st.session_state.selected_markets:
            if market in analise:
                prob = analise[f'prob_{market}']
                cls = "high" if prob >= THRESHOLDS[market] else "medium" if prob >= THRESHOLDS[market] - 10 else "low"
                
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
        
        # H2H
        if 'h2h' in analise:
            h2h = analise['h2h']
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                st.metric("BTTS H2H", f"{h2h['btts_h2h']:.0f}%")
            with col_h2:
                st.metric("Over 2.5 H2H", f"{h2h['over25_h2h']:.0f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == 'profiles' and st.session_state.selected_match:
        match = st.session_state.selected_match
        comp_id = comps[selected_comp]
        
        with st.spinner("🔍 Carregando perfis..."):
            hp = fetch_team_profile(match['home_id'], comp_id)
            ap = fetch_team_profile(match['away_id'], comp_id)
        
        st.markdown("""
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">📊 Perfis das Equipas</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🏠 {match['home_team']}")
            st.markdown(f"**Estilo:** {hp['estilo'].upper()}")
            st.progress(hp['ataque']/10, text=f"Ataque: {hp['ataque']}/10")
            st.progress(hp['defesa']/10, text=f"Defesa: {hp['defesa']}/10")
            
        with col2:
            st.markdown(f"### 🚩 {match['away_team']}")
            st.markdown(f"**Estilo:** {ap['estilo'].upper()}")
            st.progress(ap['ataque']/10, text=f"Ataque: {ap['ataque']}/10")
            st.progress(ap['defesa']/10, text=f"Defesa: {ap['defesa']}/10")
        
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.page == 'history':
        if an.historico:
            st.markdown("""
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">📈 Histórico de Análises</div>
                    <span class="result-badge">{len(an.historico)} total</span>
                </div>
            """.replace("{len(an.historico)}", str(len(an.historico))), unsafe_allow_html=True)
            
            for entry in reversed(an.historico[-10:]):
                with st.container():
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 600;">{entry['home']} vs {entry['away']}</span>
                            <span style="color: #a0a0b0;">{entry['data']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("📥 Exportar Histórico PDF", use_container_width=True):
                pdf_data = an.gerar_pdf(st.session_state.currency)
                st.download_button(
                    "📥 Download PDF",
                    data=pdf_data,
                    file_name="bet_analyzer_history.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("📊 Nenhuma análise no histórico. Faça uma análise para começar!")

if __name__ == "__main__":
    main()
