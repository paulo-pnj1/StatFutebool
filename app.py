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
from fpdf import FPDF

# ────────────────────────────────────────────────
#  CONFIGURAÇÃO INICIAL + TEMA
# ────────────────────────────────────────────────
load_dotenv()

st.set_page_config(
    page_title="Analisador de Apostas • Football Value",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

# Tema moderno escuro + acentos vibrantes
st.markdown("""
    <style>
    /* Fundo geral + tipografia */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Cabeçalhos */
    h1, h2, h3, h4 {
        color: #00d4ff !important;
        font-weight: 500 !important;
    }
    
    /* Cards */
    .card {
        background-color: #161b22;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        border: 1px solid #30363d;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        margin-bottom: 1.2rem;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2.1rem !important;
        color: #00ff9d !important;
    }
    
    /* Selectbox / Multiselect mais bonito */
    .stSelectbox > div > div > div, .stMultiSelect > div > div > div {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #c9d1d9;
    }
    
    /* Botões primários */
    .stButton > button {
        background-color: #238636 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #2ea043 !important;
    }
    
    /* Expansores */
    .stExpander {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
#  CHAVES e HEADERS
# ────────────────────────────────────────────────
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY         = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER           = os.getenv("EMAIL_USER")
EMAIL_PASS           = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY, "Accept": "application/json"}
HEADERS_ODDS     = {"Authorization": f"apikey {ODDS_API_KEY}"}

BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS     = "https://api.the-odds-api.com/v4"

# ────────────────────────────────────────────────
#  FUNÇÕES AUXILIARES (mantidas iguais ou ligeiramente limpas)
# ────────────────────────────────────────────────
def calculate_implied_probability(odd):
    return round(100 / odd, 2) if odd and odd > 0 else None

def calculate_value_bet(real_prob, odd):
    if not odd or odd <= 0 or not real_prob:
        return None
    return round((odd * (real_prob / 100)) - 1, 3)

def get_total_goals(match):    return (match['score']['fullTime'].get('home', 0) or 0) + (match['score']['fullTime'].get('away', 0) or 0)
def get_home_goals(match):     return match['score']['fullTime'].get('home', 0) or 0
def get_away_goals(match):     return match['score']['fullTime'].get('away', 0) or 0
def get_first_half_goals(match): return (match['score']['halfTime'].get('home', 0) or 0) + (match['score']['halfTime'].get('away', 0) or 0)
def get_second_half_goals(match): return get_total_goals(match) - get_first_half_goals(match)

# ────────────────────────────────────────────────
#  CACHE DE DADOS (mantido)
# ────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_football_data(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        r = requests.get(f"{BASE_URL_FOOTBALL}/{endpoint}", headers=HEADERS_FOOTBALL, timeout=12)
        if r.status_code == 429:
            st.error("Limite da API Football-Data atingido.")
            return None
        return r.json() if r.ok else None
    except:
        return None

# ... (outras funções cacheadas mantidas iguais: get_competitions, get_matches, fetch_team_profile_cached, etc.)

# ────────────────────────────────────────────────
#  INTERFACE PRINCIPAL – UX DESKTOP BONITA
# ────────────────────────────────────────────────
def main():
    if 'last_analise' not in st.session_state:
        st.session_state.last_analise = None
    if 'last_match' not in st.session_state:
        st.session_state.last_match = None
    if 'selected_comp_name' not in st.session_state:
        st.session_state.selected_comp_name = None

    # Cabeçalho principal
    st.title("⚽ Analisador Automático de Value Bets")
    st.caption("Dados reais • H2H • Perfis de times • Odds justas • Alertas inteligentes")

    # ── SIDEBAR ───────────────────────────────────────
    with st.sidebar:
        st.header("⚙️  Controles")

        st.subheader("Mercados Ativos")
        market_options = {
            'btts':             "Ambas Marcam (BTTS)",
            'over25':           "Over 2.5 Gols",
            'over15':           "Over 1.5 Gols",
            'under35':          "Under 3.5 Gols",
            'under25':          "Under 2.5 Gols",
            'second_half_more': "Mais gols 2º tempo"
        }
        selected_markets_disp = st.multiselect(
            "Selecione os mercados",
            options=list(market_options.values()),
            default=["Ambas Marcam (BTTS)", "Over 2.5 Gols", "Over 1.5 Gols"]
        )
        selected_markets = [k for k,v in market_options.items() if v in selected_markets_disp]

        st.divider()

        st.subheader("Filtro de Recomendações")
        risco_filtro = st.radio("", ["Todos", "🔥 Value Bets", "🛡️ Alta Probabilidade (>65%)"])

        st.divider()

        with st.expander("📋 Watchlist", expanded=False):
            # ... (watchlist mantida igual ou simplificada)

        st.divider()
        st.caption("v1.1 • 2025 • Powered by Football-Data & The Odds API")

    # ── CONTEÚDO PRINCIPAL ───────────────────────────────
    tab_analise, tab_perfis, tab_historico = st.tabs(["  Análise Rápida  ", "  Perfis de Times  ", "  Histórico  "])

    with tab_analise:
        col_comp, col_partida = st.columns([1, 2])

        with col_comp:
            comps = get_competitions()
            if not comps:
                st.error("Não foi possível carregar competições. Verifique a API key.")
                st.stop()

            selected_comp = st.selectbox(
                "Competição",
                options=list(comps.keys()),
                index=list(comps.keys()).index(st.session_state.selected_comp_name) if st.session_state.selected_comp_name in comps else 0,
                key="comp_select"
            )
            st.session_state.selected_comp_name = selected_comp

        with col_partida:
            with st.spinner("Carregando próxima rodada..."):
                matches = get_matches(comps[selected_comp])

            match_list = []
            for m in matches:
                if m["status"] not in ["SCHEDULED", "TIMED"]:
                    continue
                try:
                    dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    match_list.append({
                        "display": f"{m['homeTeam']['name']} × {m['awayTeam']['name']}  •  {dt.strftime('%d/%m %H:%M')}",
                        "home": m['homeTeam']['name'],
                        "away": m['awayTeam']['name'],
                        "home_id": m['homeTeam']['id'],
                        "away_id": m['awayTeam']['id'],
                        "date": dt
                    })
                except:
                    pass

            if match_list:
                choice = st.selectbox("Próximas partidas", [m["display"] for m in match_list])
                selected_idx = [m["display"] for m in match_list].index(choice)
                selected_match = match_list[selected_idx]
            else:
                st.info("Nenhuma partida agendada nos próximos dias.")
                selected_match = None

        if selected_match and st.button("🔥 Analisar Partida Agora", type="primary", use_container_width=True):
            with st.spinner("Processando análise completa..."):
                # Aqui você chama sua função de análise completa
                # analise = analisador.analisar_partida_automatica(...)
                # st.session_state.last_analise = analise
                # st.session_state.last_match = selected_match
                st.success("Análise concluída!")

        # Resultado (exemplo de visualização moderna)
        if st.session_state.last_analise:
            st.markdown("---")
            analise = st.session_state.last_analise
            match   = st.session_state.last_match

            # Cabeçalho da partida
            c1, c2, c3 = st.columns([2,1,2])
            c1.markdown(f"### {match['home']}")
            c2.markdown("<h2 style='text-align:center; color:#aaa'>×</h2>", unsafe_allow_html=True)
            c3.markdown(f"### {match['away']}")

            st.caption(f"{match['date'].strftime('%d/%m/%Y %H:%M')} • {selected_comp}")

            # Cards de probabilidades
            cols = st.columns(len(selected_markets) or 1)
            for i, market in enumerate(selected_markets):
                prob = analise.get(f"prob_{market}", 55)
                label = market_options[market]

                with cols[i]:
                    with st.container():
                        st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                        fig = create_gauge_chart(prob, label, 60)
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown(f"**Odd justa**: {analise.get(f'odd_justa_{market}', '–')}", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

    # ── Outras abas (perfis e histórico) podem seguir o mesmo padrão de cards ──

if __name__ == "__main__":
    main()
