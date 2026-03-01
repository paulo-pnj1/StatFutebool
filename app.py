import streamlit as st
import requests
import pandas asd as pd
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
.nav-button {
    background: transparent;
    border: none;
    color: #a0a0b0;
    font-size: 0.95rem;
    font-weight: 500;
    padding: 0.6rem 1.2rem;
    border-radius: 30px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-button:hover {
    background: rgba(255, 75, 75, 0.1);
    color: #ffffff;
}

.nav-button.active {
    background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
    color: #ffffff;
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
    cursor: pointer;
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
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
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

# ── API FUNCTIONS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_fd(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        r = requests.get(f"{BASE_URL_FOOTBALL}/{endpoint}", headers=HEADERS_FOOTBALL, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_fd("competitions")
    if not data:
        return {}
    return {c["name"]: c["id"] for c in data.get("competitions", []) if c.get("currentSeason")}

@st.cache_data(ttl=600)
def get_matches(comp_id):
    today = datetime.now().strftime("%Y-%m-%d")
    nw = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_fd(f"competitions/{comp_id}/matches?dateFrom={today}&dateTo={nw}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile(team_id, comp_id):
    return {'ataque': 7, 'defesa': 6, 'estilo': 'ofensivo', 'over25': 65, 'btts': 60}

# ── ANALISADOR ────────────────────────────────────────────────────────────────
class Analisador:
    def __init__(self):
        if 'historico' not in st.session_state:
            st.session_state.historico = []
        self.historico = st.session_state.historico

    def analisar(self, ht, at, competition, hid, aid, comp_id, markets):
        with st.spinner("🔮 Analisando..."):
            time.sleep(0.5)
            
        # Simulação de análise
        probs = {
            'btts': 68,
            'over25': 72,
            'over15': 85,
            'under35': 45,
            'under25': 38,
            'second_half_more': 62
        }
        
        res = {f'prob_{k}': v for k, v in probs.items()}
        res['h2h'] = {'btts_h2h': 55, 'over25_h2h': 60}
        
        self.historico.append({
            'home': ht,
            'away': at,
            'probs': probs,
            'data': datetime.now().strftime('%d/%m %H:%M')
        })
        
        return res

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

    an = Analisador()
    comps = get_competitions()
    c_info = CURRENCIES[st.session_state.currency]

    # Status das APIs
    api_ok = FOOTBALL_DATA_API_KEY != "DEFAULT_KEY"

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    cols = st.columns([2, 3, 2])
    
    with cols[0]:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 2rem;">⚽</span>
            <span style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #fff, #ff4b4b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Bet Analyzer</span>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("🔍 Análise", use_container_width=True, type="primary" if st.session_state.page == 'analyze' else "secondary"):
                st.session_state.page = 'analyze'
                st.rerun()
        with b2:
            if st.button("📊 Perfis", use_container_width=True, type="primary" if st.session_state.page == 'profiles' else "secondary"):
                st.session_state.page = 'profiles'
                st.rerun()
        with b3:
            if st.button("📈 Histórico", use_container_width=True, type="primary" if st.session_state.page == 'history' else "secondary"):
                st.session_state.page = 'history'
                st.rerun()
    
    with cols[2]:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem; justify-content: flex-end;">
            <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.03); padding: 0.3rem 1rem; border-radius: 30px;">
                <span>{c_info['flag']}</span>
                <span>{st.session_state.currency}</span>
                <span>{c_info['symbol']}</span>
            </div>
            <div style="display: flex; gap: 0.3rem;">
                <div class="dot {'dot-green' if api_ok else 'dot-red'}" title="API Status"></div>
                <div class="dot dot-yellow" title="Odds API"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── QUICK ACTIONS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display: flex; gap: 0.5rem; padding: 1rem 0; overflow-x: auto;">
        <div class="quick-action active">⚽ Premier League</div>
        <div class="quick-action">🎯 BTTS</div>
        <div class="quick-action">⚽ Over 2.5</div>
        <div class="quick-action">📋 Favoritos</div>
        <div class="quick-action">📥 Exportar</div>
    </div>
    """, unsafe_allow_html=True)

    # ── MAIN CONTENT ──────────────────────────────────────────────────────────
    
    # Seletor de competição e partida (sempre visível)
    if comps:
        comp_list = list(comps.keys())
        selected_comp = st.selectbox(
            "Competição",
            comp_list,
            index=0,
            key="comp_selector",
            label_visibility="collapsed"
        )

        comp_id = comps[selected_comp]

        # Buscar partidas
        with st.spinner("🔍 Carregando partidas..."):
            matches = get_matches(comp_id)

        # Grid de partidas
        st.markdown('<div class="match-grid">', unsafe_allow_html=True)
        
        match_options = []
        for m in matches[:6]:  # Limitar para performance
            if m["status"] in ["SCHEDULED", "TIMED"]:
                try:
                    dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    match_data = {
                        "id": m["id"],
                        "home_id": m["homeTeam"]["id"],
                        "away_id": m["awayTeam"]["id"],
                        "home_team": m["homeTeam"]["name"],
                        "away_team": m["awayTeam"]["name"],
                        "date": dt
                    }
                    match_options.append(match_data)
                    
                    selected_class = "selected" if st.session_state.selected_match and st.session_state.selected_match.get('id') == m["id"] else ""
                    
                    # Criar coluna para o card
                    cols = st.columns(1)
                    with cols[0]:
                        if st.button(
                            f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}\n\n{dt.strftime('%d/%m %H:%M')}",
                            key=f"match_{m['id']}",
                            use_container_width=True
                        ):
                            st.session_state.selected_match = match_data
                            st.rerun()
                            
                except:
                    continue
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ── PAINEL DE APOSTA RÁPIDA ──────────────────────────────────────────────
    if st.session_state.selected_match:
        match = st.session_state.selected_match
        
        st.markdown("""
        <div class="quick-bet-panel">
            <div class="quick-bet-info">
                <div class="quick-bet-match">{home} vs {away}</div>
                <div class="quick-bet-market">BTTS · Over 2.5</div>
            </div>
            <div class="quick-bet-inputs">
                <input type="number" class="quick-bet-input" placeholder="Odd" value="2.00" step="0.01">
                <input type="number" class="quick-bet-input" placeholder="Stake" value="10.00" step="1.00">
                <button class="quick-bet-button">⚡ Analisar</button>
            </div>
        </div>
        """.format(home=match['home_team'], away=match['away_team']), unsafe_allow_html=True)
        
        # Botão de análise real (Streamlit)
        if st.button("🚀 Analisar Partida", use_container_width=True):
            with st.spinner("🔮 Processando..."):
                result = an.analisar(
                    match['home_team'], match['away_team'],
                    selected_comp, match['home_id'], match['away_id'],
                    comp_id, ['btts', 'over25']
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
        with cols[0]:
            prob = analise['prob_btts']
            st.metric("BTTS", f"{prob:.0f}%", delta=None)
        with cols[1]:
            prob = analise['prob_over25']
            st.metric("Over 2.5", f"{prob:.0f}%", delta=None)
        with cols[2]:
            prob = analise['prob_over15']
            st.metric("Over 1.5", f"{prob:.0f}%", delta=None)
        
        # Barras de probabilidade
        st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
        
        for market in ['btts', 'over25', 'over15', 'under35', 'under25', 'second_half_more']:
            prob = analise[f'prob_{market}']
            cls = "high" if prob >= 60 else "medium" if prob >= 45 else "low"
            
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

    elif st.session_state.page == 'profiles' and st.session_state.selected_match:
        match = st.session_state.selected_match
        
        st.markdown("""
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">📊 Perfis das Equipas</div>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(2)
        
        with cols[0]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 16px;">
                <h3 style="color: #ff4b4b;">🏠 {match['home_team']}</h3>
                <div style="margin-top: 1rem;">
                    <div class="prob-meter">
                        <span class="meter-label">Ataque</span>
                        <div class="meter-bar"><div class="meter-fill high" style="width: 70%;"></div></div>
                        <span class="meter-value">7/10</span>
                    </div>
                    <div class="prob-meter">
                        <span class="meter-label">Defesa</span>
                        <div class="meter-bar"><div class="meter-fill medium" style="width: 60%;"></div></div>
                        <span class="meter-value">6/10</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 16px;">
                <h3 style="color: #ff4b4b;">🚩 {match['away_team']}</h3>
                <div style="margin-top: 1rem;">
                    <div class="prob-meter">
                        <span class="meter-label">Ataque</span>
                        <div class="meter-bar"><div class="meter-fill high" style="width: 70%;"></div></div>
                        <span class="meter-value">7/10</span>
                    </div>
                    <div class="prob-meter">
                        <span class="meter-label">Defesa</span>
                        <div class="meter-bar"><div class="meter-fill medium" style="width: 60%;"></div></div>
                        <span class="meter-value">6/10</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
            
            for entry in reversed(an.historico[-5:]):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 600;">{entry['home']} vs {entry['away']}</span>
                        <span style="color: #a0a0b0;">{entry['data']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📊 Nenhuma análise no histórico. Faça uma análise para começar!")

if __name__ == "__main__":
    main()
