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
    page_icon="⚽",
    initial_sidebar_state="collapsed"
)

# Chaves API
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "DEFAULT_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "sua_chave_the_odds_api")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

HEADERS_FOOTBALL = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
HEADERS_ODDS = {"Authorization": f"apikey {ODDS_API_KEY}"}
BASE_URL_FOOTBALL = "https://api.football-data.org/v4"
BASE_URL_ODDS = "https://api.the-odds-api.com/v4"

# --- 2. FUNÇÕES UTILITÁRIAS ---
def calculate_implied_probability(odd):
    return round(100 / odd, 2) if odd and odd > 0 else None

def calculate_value_bet(real_prob, odd):
    return round((odd * (real_prob / 100)) - 1, 3) if odd and odd > 0 and real_prob else None

def get_total_goals(match):
    return (match['score']['fullTime'].get('home', 0) or 0) + (match['score']['fullTime'].get('away', 0) or 0)

# --- 3. FUNÇÕES DE API (CACHE OTIMIZADO) ---
@st.cache_data(ttl=3600)
def fetch_football_data(endpoint):
    if FOOTBALL_DATA_API_KEY == "DEFAULT_KEY":
        return None
    try:
        url = f"{BASE_URL_FOOTBALL}/{endpoint}"
        response = requests.get(url, headers=HEADERS_FOOTBALL, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=3600)
def get_competitions():
    data = fetch_football_data("competitions")
    if data and "competitions" in data:
        return {comp["name"]: comp["id"] for comp in data["competitions"] 
                if comp["name"] in ["Premier League", "Primera Division", "Serie A", "Bundesliga", 
                                   "Ligue 1", "Primeira Liga", "UEFA Champions League"] 
                and comp.get("currentSeason")}
    return {}

@st.cache_data(ttl=600)
def get_matches(competition_id):
    today = datetime.now().strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    data = fetch_football_data(f"competitions/{competition_id}/matches?dateFrom={today}&dateTo={next_week}")
    return data.get("matches", []) if data else []

@st.cache_data(ttl=3600)
def fetch_team_profile(team_id, comp_id):
    profile = {'ataque': 5, 'defesa': 5, 'estilo': 'equilibrado', 'btts': 50, 'over25': 50}
    
    # Standings
    standings = fetch_football_data(f"competitions/{comp_id}/standings")
    if standings and 'standings' in standings:
        for group in standings['standings']:
            for entry in group['table']:
                if entry['team']['id'] == team_id:
                    played = entry['playedGames']
                    if played > 0:
                        profile['ataque'] = min(10, max(1, round((entry['goalsFor']/played/1.4)*7+1)))
                        profile['defesa'] = min(10, max(1, round((1.4/max(entry['goalsAgainst']/played,0.1))*7+1)))
                    break
    
    # Recent matches
    matches = fetch_football_data(f"teams/{team_id}/matches?status=FINISHED&limit=5")
    if matches and 'matches' in matches:
        recent = matches['matches'][:5]
        if recent:
            profile['btts'] = round(sum(1 for m in recent if get_total_goals(m)>2) / len(recent) * 100)
            profile['over25'] = round(sum(1 for m in recent if get_total_goals(m)>2.5) / len(recent) * 100)
    
    # Estilo
    if profile['ataque'] >= 7 and profile['defesa'] <= 6:
        profile['estilo'] = 'ofensivo'
    elif profile['defesa'] >= 7 and profile['ataque'] <= 6:
        profile['estilo'] = 'defensivo'
    
    return profile

# --- 4. ANALISADOR PRINCIPAL (VERSÃO OTIMIZADA) ---
class Analisador:
    def __init__(self):
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        if 'historico' not in st.session_state:
            st.session_state.historico = []
        self.watchlist = st.session_state.watchlist
        self.historico = st.session_state.historico

    @st.cache_data(ttl=3600)
    def fetch_h2h(_self, home_id, away_id):
        data = fetch_football_data(f"teams/{home_id}/matches?status=FINISHED&limit=10")
        h2h = []
        if data and 'matches' in data:
            for m in data['matches']:
                if m.get('awayTeam', {}).get('id') == away_id or m.get('homeTeam', {}).get('id') == away_id:
                    h2h.append(m)
                    if len(h2h) >= 3:
                        break
        return {
            'btts': round(sum(1 for m in h2h if get_total_goals(m)>2) / max(len(h2h),1) * 100),
            'over25': round(sum(1 for m in h2h if get_total_goals(m)>2.5) / max(len(h2h),1) * 100)
        } if h2h else {'btts': 50, 'over25': 50}

    def analisar(self, home_team, away_team, home_id, away_id, comp_id, comp_name):
        home = fetch_team_profile(home_id, comp_id)
        away = fetch_team_profile(away_id, comp_id)
        h2h = self.fetch_h2h(home_id, away_id)
        
        # Cálculo simplificado
        prob_btts = min(85, max(15, (home['btts'] + away['btts'])/2 + h2h['btts']/20))
        prob_over25 = min(80, max(20, (home['over25'] + away['over25'])/2 + h2h['over25']/20))
        
        # Ajuste por estilo
        if home['estilo'] == 'ofensivo' and away['estilo'] == 'ofensivo':
            prob_btts += 5
            prob_over25 += 8
        elif home['estilo'] == 'defensivo' and away['estilo'] == 'defensivo':
            prob_btts -= 8
            prob_over25 -= 10
        
        analise = {
            'prob_btts': round(prob_btts, 1),
            'prob_over25': round(prob_over25, 1),
            'odd_btts': round(100/prob_btts, 2),
            'odd_over25': round(100/prob_over25, 2),
            'home_estilo': home['estilo'],
            'away_estilo': away['estilo'],
            'home_ataque': home['ataque'],
            'away_ataque': away['ataque'],
            'h2h_btts': h2h['btts'],
            'h2h_over25': h2h['over25']
        }
        
        self.historico.append({
            'home': home_team, 'away': away_team, 'data': datetime.now().strftime('%d/%m %H:%M'),
            'btts': analise['prob_btts'], 'over25': analise['prob_over25']
        })
        st.session_state.historico = self.historico
        return analise

# --- 5. COMPONENTES VISUAIS OTIMIZADOS ---
def mini_gauge(value, title, size=120):
    color = '#4CAF50' if value >= 60 else '#FFC107' if value >= 50 else '#F44336'
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 20}},
        title={'text': title, 'font': {'size': 12}},
        gauge={'axis': {'range': [0, 100], 'tickwidth': 0}, 
               'bar': {'color': color, 'thickness': 0.3},
               'bgcolor': 'white', 'borderwidth': 0,
               'steps': [{'range': [0, 50], 'color': '#ffebee'},
                        {'range': [50, 70], 'color': '#fff9c4'},
                        {'range': [70, 100], 'color': '#e8f5e8'}]}
    ))
    fig.update_layout(height=size, margin=dict(l=5, r=5, t=25, b=5))
    return fig

def mini_card(title, value, unit="%", color=None):
    return f"""
    <div style="background:#f8f9fa; padding:10px; border-radius:8px; text-align:center; margin:5px;">
        <small style="color:#666;">{title}</small><br>
        <span style="font-size:24px; font-weight:bold; color:{color or '#333'};">{value}{unit}</span>
    </div>
    """

# --- 6. INTERFACE PRINCIPAL OTIMIZADA ---
def main():
    # Inicialização
    if 'last' not in st.session_state:
        st.session_state.last = None
    
    analisador = Analisador()
    competitions = get_competitions()
    
    if not competitions:
        if FOOTBALL_DATA_API_KEY != "DEFAULT_KEY":
            st.error("Erro ao carregar competições")
        return

    # Header compacto
    st.markdown("""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'>
        <h1 style='margin:0;'>⚽ Analisador de Apostas</h1>
        <span style='background:#4CAF50; color:white; padding:4px 12px; border-radius:20px; font-size:14px;'>BETA</span>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar compacta
    with st.sidebar:
        st.markdown("### ⚙️ Config")
        
        # Mercados
        markets = {
            'btts': 'BTTS', 'over25': 'O2.5', 'over15': 'O1.5',
            'under35': 'U3.5', 'under25': 'U2.5'
        }
        selected = []
        cols = st.columns(3)
        for i, (key, label) in enumerate(markets.items()):
            with cols[i%3]:
                if st.checkbox(label, value=key in ['btts','over25','over15'], key=f"mkt_{key}"):
                    selected.append(key)
        
        st.divider()
        
        # Watchlist compacta
        st.markdown("### 📋 Watchlist")
        new = st.text_input("", placeholder="Time A vs Time B", label_visibility="collapsed")
        if new and st.button("➕", use_container_width=True):
            analisador.watchlist.append(new)
            st.rerun()
        
        for i, m in enumerate(analisador.watchlist[-3:]):
            cols = st.columns([4,1])
            cols[0].caption(m)
            if cols[1].button("✕", key=f"rm_{i}"):
                analisador.walklist.pop(i)

    # Abas principais
    tab1, tab2, tab3 = st.tabs(["🔍 Análise", "📊 Times", "📈 Histórico"])
    
    with tab1:
        # Seleção compacta
        col1, col2 = st.columns(2)
        with col1:
            comp = st.selectbox("Liga", options=list(competitions.keys()), index=0)
        with col2:
            matches = get_matches(competitions[comp])
            match_options = []
            for m in matches:
                if m["status"] in ["SCHEDULED", "TIMED"]:
                    try:
                        date = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                        match_options.append({
                            "display": f"{m['homeTeam']['name']} x {m['awayTeam']['name']} ({date.strftime('%d/%m')})",
                            "home": m['homeTeam']['name'], "away": m['awayTeam']['name'],
                            "home_id": m['homeTeam']['id'], "away_id": m['awayTeam']['id']
                        })
                    except: continue
            
            if match_options:
                match = st.selectbox("Jogo", options=[m["display"] for m in match_options])
                idx = [m["display"] for m in match_options].index(match)
                match_data = match_options[idx]
            else:
                st.warning("Sem jogos")
                match_data = None
        
        # Botão análise
        if match_data and st.button("🚀 Analisar", use_container_width=True, type="primary"):
            with st.spinner("Analisando..."):
                analise = analisador.analisar(
                    match_data['home'], match_data['away'],
                    match_data['home_id'], match_data['away_id'],
                    competitions[comp], comp
                )
                st.session_state.last = {'match': match_data, 'analise': analise}
        
        # Resultados
        if st.session_state.last:
            m = st.session_state.last['match']
            a = st.session_state.last['analise']
            
            st.markdown(f"### {m['home']} 🆚 {m['away']}")
            
            # Métricas principais
            c1, c2, c3 = st.columns(3)
            with c1:
                st.plotly_chart(mini_gauge(a['prob_btts'], 'BTTS %'), use_container_width=True)
                st.caption(f"Odd justa: {a['odd_btts']}")
            with c2:
                st.plotly_chart(mini_gauge(a['prob_over25'], 'O2.5 %'), use_container_width=True)
                st.caption(f"Odd justa: {a['odd_over25']}")
            with c3:
                st.markdown("##### Perfis")
                st.markdown(f"🏠 {a['home_estilo'].title()} ({a['home_ataque']}/10)")
                st.markdown(f"🚩 {a['away_estilo'].title()} ({a['away_ataque']}/10)")
                st.markdown(f"🤝 H2H: {a['h2h_btts']:.0f}% BTTS")
            
            # Calculadora value
            with st.expander("💰 Calculadora Value Bet"):
                cols = st.columns(2)
                for i, market in enumerate(['btts', 'over25']):
                    with cols[i]:
                        prob = a[f'prob_{market}']
                        odd = st.number_input(f"Odd {market.upper()}", min_value=1.01, 
                                             value=round(100/prob,2), step=0.1, format="%.2f")
                        value = calculate_value_bet(prob, odd)
                        st.metric("Value", f"{value:.3f}", 
                                 delta="✅" if value and value>0.05 else "❌")
    
    with tab2:
        if st.session_state.last:
            m = st.session_state.last['match']
            comp_id = competitions[comp]
            
            col1, col2 = st.columns(2)
            for col, team_id, team_name in [(col1, m['home_id'], m['home']), 
                                           (col2, m['away_id'], m['away'])]:
                with col:
                    perfil = fetch_team_profile(team_id, comp_id)
                    st.markdown(f"### {team_name}")
                    st.markdown(f"**{perfil['estilo'].title()}**")
                    st.progress(perfil['ataque']/10, f"Ataque: {perfil['ataque']}/10")
                    st.progress(perfil['defesa']/10, f"Defesa: {perfil['defesa']}/10")
                    st.caption(f"BTTS: {perfil['btts']}% | O2.5: {perfil['over25']}%")
    
    with tab3:
        if analisador.historico:
            df = pd.DataFrame(analisador.historico[-10:])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # PDF simples
            if st.button("📄 Gerar PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                pdf.cell(0, 10, "Relatório de Análises", ln=1)
                for a in analisador.historico[-5:]:
                    pdf.cell(0, 8, f"{a['home']} x {a['away']} - BTTS: {a['btts']}% O2.5: {a['over25']}%", ln=1)
                st.download_button("Download PDF", pdf.output(dest='S').encode('latin1'), 
                                  "relatorio.pdf", "application/pdf")
        else:
            st.info("Nenhuma análise no histórico")

if __name__ == "__main__":
    main()
