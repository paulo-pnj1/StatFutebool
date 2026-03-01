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
    page_title="Bet Analyzer",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* RESET E ESTILOS GLOBAIS */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    color: #ffffff;
    min-height: 100vh;
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
    padding: 1rem 1.5rem 2rem !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* SIDEBAR MODERNA */
[data-testid="stSidebar"] {
    background: rgba(20, 20, 35, 0.95) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* TOP BAR */
.top-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.5rem;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 107, 107, 0.3);
    margin: -1rem -1.5rem 1.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.tb-icon {
    font-size: 1.8rem;
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    flex-shrink: 0;
}

.tb-title {
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    flex: 1;
}

.tb-sub {
    font-size: 0.7rem;
    color: #a0a0c0;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(255, 255, 255, 0.05);
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    border: 1px solid rgba(255, 107, 107, 0.2);
}

/* STATUS DOTS */
.status-dots {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.3rem 0.8rem;
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    transition: all 0.3s ease;
}

.dot-g {
    background: #4ecdc4;
    box-shadow: 0 0 15px #4ecdc4;
    animation: pulse 2s infinite;
}

.dot-y {
    background: #ffd93d;
    box-shadow: 0 0 15px #ffd93d;
}

.dot-r {
    background: #ff6b6b;
    box-shadow: 0 0 15px #ff6b6b;
}

@keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
    100% { opacity: 1; transform: scale(1); }
}

/* SIDEBAR MENU */
.sidebar-section {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 15px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #ff6b6b;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sidebar-title i {
    font-size: 1rem;
}

/* MENU ITEMS */
.menu-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.8rem 1rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #a0a0c0;
}

.menu-item:hover {
    background: rgba(255, 107, 107, 0.1);
    border-color: rgba(255, 107, 107, 0.3);
    transform: translateX(5px);
    color: #ffffff;
}

.menu-item.active {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(78, 205, 196, 0.2));
    border-color: #ff6b6b;
    color: #ffffff;
    box-shadow: 0 5px 15px rgba(255, 107, 107, 0.2);
}

.menu-icon {
    font-size: 1.2rem;
}

/* CONTROLS CONTAINER */
.controls-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

/* LABELS */
.sec-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4ecdc4;
    margin-bottom: 0.5rem;
    display: block;
}

/* MATCH BANNER */
.match-banner {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(78, 205, 196, 0.1));
    border: 1px solid rgba(255, 107, 107, 0.3);
    border-radius: 20px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex-wrap: wrap;
    box-shadow: 0 10px 30px rgba(255, 107, 107, 0.1);
}

.match-teams {
    flex: 1;
    min-width: 200px;
}

.match-teams .mh {
    font-size: 1.2rem;
    font-weight: 700;
    color: #ff6b6b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.match-teams .mv {
    font-size: 0.7rem;
    color: #4ecdc4;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0.2rem 0;
}

.match-teams .ma {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4ecdc4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.match-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #a0a0c0;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 30px;
    padding: 0.5rem 1.2rem;
    white-space: nowrap;
    flex-shrink: 0;
}

/* METRIC GRID */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}

.metric-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem 0.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}

.mc-g::before {
    background: linear-gradient(90deg, #4ecdc4, #45b7b0);
}

.mc-y::before {
    background: linear-gradient(90deg, #ffd93d, #ffb347);
}

.mc-r::before {
    background: linear-gradient(90deg, #ff6b6b, #ff4757);
}

.metric-card .mv {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.mc-g .mv { color: #4ecdc4; }
.mc-y .mv { color: #ffd93d; }
.mc-r .mv { color: #ff6b6b; }

.metric-card .ml {
    font-size: 0.65rem;
    font-weight: 600;
    color: #a0a0c0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-card .mo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #666688;
    margin-top: 0.3rem;
}

/* PROB BARS */
.pbar-wrap {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(5px);
}

.pbar-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}

.pbar-row:last-child { margin-bottom: 0; }

.pbar-lbl {
    font-size: 0.75rem;
    color: #a0a0c0;
    width: 85px;
    flex-shrink: 0;
    font-weight: 500;
}

.pbar-track {
    flex: 1;
    height: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    overflow: hidden;
}

.pbar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

.pb-g { background: linear-gradient(90deg, #4ecdc4, #45b7b0); }
.pb-y { background: linear-gradient(90deg, #ffd93d, #ffb347); }
.pb-r { background: linear-gradient(90deg, #ff6b6b, #ff4757); }

.pbar-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #ffffff;
    width: 40px;
    text-align: right;
    flex-shrink: 0;
}

/* ANALYSIS CARD */
.analysis-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(5px);
}

.aline {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.8rem;
    color: #a0a0c0;
    line-height: 1.5;
}

.aline:last-child { border-bottom: none; }

.aline .ai {
    flex-shrink: 0;
    font-size: 1rem;
}

/* H2H */
.h2h-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
    margin-bottom: 1.2rem;
}

.h2h-tile {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem;
    text-align: center;
    backdrop-filter: blur(5px);
}

.h2h-tile .hv {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ff6b6b;
}

.h2h-tile .hl {
    font-size: 0.65rem;
    color: #a0a0c0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.3rem;
}

/* PILLS */
.pill-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.2rem;
}

.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 1rem;
    border-radius: 30px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
    backdrop-filter: blur(5px);
}

.pill-g {
    background: rgba(78, 205, 196, 0.2);
    color: #4ecdc4;
    border: 1px solid rgba(78, 205, 196, 0.3);
}

.pill-y {
    background: rgba(255, 217, 61, 0.2);
    color: #ffd93d;
    border: 1px solid rgba(255, 217, 61, 0.3);
}

.pill-s {
    background: rgba(255, 255, 255, 0.05);
    color: #a0a0c0;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* TEAM CARD */
.team-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(5px);
}

.tc-hdr {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.tc-name {
    font-size: 1rem;
    font-weight: 700;
    color: #ffffff;
}

.tc-badge {
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.3rem 1rem;
    border-radius: 30px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tb-of {
    background: rgba(255, 107, 107, 0.2);
    color: #ff6b6b;
    border: 1px solid rgba(255, 107, 107, 0.3);
}

.tb-df {
    background: rgba(78, 205, 196, 0.2);
    color: #4ecdc4;
    border: 1px solid rgba(78, 205, 196, 0.3);
}

.tb-eq {
    background: rgba(255, 217, 61, 0.2);
    color: #ffd93d;
    border: 1px solid rgba(255, 217, 61, 0.3);
}

/* EV BOX */
.ev-box {
    text-align: center;
    padding: 0.8rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.ev-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
}

.ev-lbl {
    font-size: 0.65rem;
    margin-top: 0.2rem;
    color: #a0a0c0;
}

/* HIST CARDS */
.hist-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 0.8rem;
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.hist-card:hover {
    transform: translateX(5px);
    border-color: rgba(255, 107, 107, 0.3);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.hist-card-left { flex: 1; min-width: 200px; }

.hist-match {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
}

.hist-date {
    font-size: 0.7rem;
    color: #a0a0c0;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.2rem;
}

.hist-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.3rem;
    flex-shrink: 0;
}

.hist-market {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.3rem 1rem;
    border-radius: 30px;
}

.hm-g {
    background: rgba(78, 205, 196, 0.2);
    color: #4ecdc4;
    border: 1px solid rgba(78, 205, 196, 0.3);
}

.hm-y {
    background: rgba(255, 217, 61, 0.2);
    color: #ffd93d;
    border: 1px solid rgba(255, 217, 61, 0.3);
}

.hm-r {
    background: rgba(255, 255, 255, 0.05);
    color: #a0a0c0;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* DIVIDER */
.divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255, 107, 107, 0.3), rgba(78, 205, 196, 0.3), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* STREAMLIT OVERRIDES */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 40px;
    padding: 4px;
    gap: 2px;
    margin-bottom: 1.5rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #a0a0c0 !important;
    border-radius: 40px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4) !important;
    color: #ffffff !important;
    box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3) !important;
}

.stSelectbox, .stMultiSelect, .stNumberInput, .stTextInput {
    margin-bottom: 0.5rem !important;
}

.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: #4ecdc4 !important;
}

[data-baseweb="select"] > div:first-child, [data-baseweb="base-input"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}

[data-baseweb="select"] > div:first-child:hover, [data-baseweb="base-input"]:hover {
    border-color: #ff6b6b !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ff4757) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 40px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 5px 20px rgba(255, 107, 107, 0.3) !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #4ecdc4, #45b7b0) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 40px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
}

div[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 15px !important;
    margin-bottom: 1rem !important;
}

div[data-testid="stExpander"] summary {
    color: #ffffff !important;
    font-weight: 600 !important;
    padding: 0.8rem 1.2rem !important;
}

/* RESPONSIVIDADE */
@media (max-width: 768px) {
    .block-container {
        padding: 0.5rem 1rem !important;
    }
    
    .top-bar {
        padding: 0.6rem 1rem;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .tb-title {
        font-size: 1.1rem;
    }
    
    .tb-sub {
        font-size: 0.6rem;
        padding: 0.2rem 0.6rem;
    }
    
    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .match-banner {
        padding: 1rem;
        gap: 0.8rem;
    }
    
    .match-teams .mh,
    .match-teams .ma {
        font-size: 1rem;
    }
    
    .h2h-grid {
        grid-template-columns: 1fr;
    }
    
    .hist-card {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .hist-right {
        align-items: flex-start;
        width: 100%;
    }
    
    .controls-container {
        padding: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.4rem 1rem !important;
        font-size: 0.7rem !important;
    }
}

@media (max-width: 480px) {
    .tb-title {
        font-size: 1rem;
    }
    
    .tb-sub {
        display: none;
    }
    
    .status-dots {
        padding: 0.2rem 0.5rem;
    }
    
    .metric-grid {
        grid-template-columns: 1fr;
    }
    
    .match-banner {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .match-date {
        width: 100%;
        text-align: center;
    }
    
    .pbar-row {
        flex-wrap: wrap;
    }
    
    .pbar-lbl {
        width: 100%;
        margin-bottom: 0.2rem;
    }
    
    .tc-hdr {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}

/* SCROLLBAR */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ff4757, #45b7b0);
}

/* ANIMAÇÕES */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.5s ease;
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
        """Gera relatório PDF com tratamento de caracteres Unicode"""
        c = CURRENCIES.get(currency_key, CURRENCIES['EUR'])
        pdf = FPDF()
        pdf.add_page()
        
        # Função para limpar texto (remover emojis e caracteres especiais)
        def clean_text(text):
            if not isinstance(text, str):
                text = str(text)
            # Substituir emojis comuns
            text = text.replace('🏠', 'Home: ')
            text = text.replace('🚩', 'Away: ')
            text = text.replace('⚽', '[F] ')
            text = text.replace('🎯', '[T] ')
            text = text.replace('🛡️', '[S] ')
            text = text.replace('⏱️', '[T] ')
            text = text.replace('⚡', '[A] ')
            text = text.replace('⚖️', '[B] ')
            text = text.replace('🤝', '[H] ')
            text = text.replace('✅', '[OK] ')
            text = text.replace('⚠️', '[!] ')
            text = text.replace('🔒', '[L] ')
            text = text.replace('📊', '[G] ')
            text = text.replace('·', '-')
            text = text.replace('→', '->')
            # Remover outros caracteres problemáticos
            text = ''.join(char for char in text if ord(char) < 256 or char in '€$R$Kz')
            return text.encode('latin-1', errors='ignore').decode('latin-1')
        
        # Título
        pdf.set_font("Arial", "B", size=12)
        titulo = clean_text(f"Relatorio Bet Analyzer ({c['name']})")
        pdf.cell(200, 9, titulo, ln=1, align='C')
        pdf.ln(5)
        
        # Total de apostas
        pdf.set_font("Arial", size=9)
        total_apostas = clean_text(f"Total de apostas: {len(self.historico)}")
        pdf.cell(200, 6, total_apostas, ln=1)
        pdf.ln(3)
        
        # Mapeamento de mercados
        MMAP = {"btts":"BTTS","over25":"Over 2.5","over15":"Over 1.5",
                "under35":"Under 3.5","under25":"Under 2.5","second_half_more":"2o Tempo+"}
        
        # Últimas 20 apostas
        for a in list(reversed(self.historico))[-20:]:
            mkey = a.get('mercado_escolhido', '')
            mlabel = MMAP.get(mkey, mkey.upper())
            odd_ap = a.get('odd_apostada', 0)
            ev = a.get('ev', 0)
            stake = a.get('stake', 0)
            prob_m = a.get('probs', {}).get(mkey, a.get('prob_btts', 0))
            
            # Times (limpos)
            home_clean = clean_text(a['home'])
            away_clean = clean_text(a['away'])
            
            pdf.set_font("Arial", "B", size=9)
            match_line = clean_text(f"{home_clean} vs {away_clean}")
            pdf.cell(200, 6, match_line, ln=1)
            
            pdf.set_font("Arial", size=8)
            stake_str = f"{c['symbol']}{stake:.2f}" if stake else "-"
            data_clean = clean_text(a['data'])
            
            # Linha de detalhes
            line = f"  {data_clean}  |  {mlabel}  |  Prob: {prob_m:.0f}%  |  Odd: {odd_ap:.2f}  |  Stake: {stake_str}  |  EV: {ev:+.3f}"
            line_clean = clean_text(line)
            pdf.cell(200, 5, line_clean, ln=1)
            pdf.ln(2)
        
        # Retornar PDF como bytes
        return pdf.output(dest='S').encode('latin-1', errors='ignore')

# ── RENDER HELPERS ────────────────────────────────────────────────────────────
def render_metric_grid(analise, markets):
    tiles = ""
    for m in markets:
        prob = analise.get(f'prob_{m}',0)
        odd  = analise.get(f'odd_justa_{m}',0)
        c    = mc_cls(prob, THRESHOLDS.get(m,60))
        lbl  = MARKET_MAP.get(m,m)
        tiles += f'<div class="metric-card {c}"><div class="mv">{prob:.0f}<span style="font-size:0.6em;color:#666688">%</span></div><div class="ml">{lbl}</div><div class="mo">@ {odd}</div></div>'
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
        c = "#4ecdc4" if v>=60 else "#ffd93d" if v>=45 else "#ff6b6b"
        stats += f'<span class="tc-stat" style="color:{c}">{lbl} {v}%</span>'
    st.markdown(f'<div class="team-card"><div class="tc-hdr"><span class="tc-name">{side} {name}</span><span class="tc-badge {sc}">{p["estilo"]}</span></div>{bars}<div class="tc-stats">{stats}</div></div>', unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    for k,v in [('last_analise',None),('last_match',None),('selected_comp',None),('currency','EUR'),('menu','analise')]:
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
        <div class="tb-title">Bet Analyzer</div>
        <div class="tb-sub">H2H · Value Bet · Alertas</div>
        <div class="status-dots">
            <div class="dot {d1}" title="Football API"></div>
            <div class="dot {d2}" title="Odds API"></div>
            <div class="dot {d3}" title="Email"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not comps:
        st.error("❌ Configure FOOTBALL_DATA_API_KEY no .env")
        return

    if st.session_state['selected_comp'] not in comps:
        st.session_state['selected_comp'] = list(comps.keys())[0]

    # ── SIDEBAR MENU ─────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title"><i>📊</i> MENU PRINCIPAL</div>', unsafe_allow_html=True)
        
        menu_items = {
            'analise': {'icon': '🔍', 'label': 'Análise'},
            'perfis': {'icon': '📊', 'label': 'Perfis'},
            'historico': {'icon': '📈', 'label': 'Histórico'}
        }
        
        for key, item in menu_items.items():
            active_class = "active" if st.session_state['menu'] == key else ""
            if st.button(f"{item['icon']} {item['label']}", key=f"menu_{key}"):
                st.session_state['menu'] = key
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ── CONFIGURAÇÕES ───────────────────────────────────────────────────
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title"><i>⚙️</i> CONFIGURAÇÕES</div>', unsafe_allow_html=True)
        
        # Moeda
        st.markdown('<span class="sec-label">Moeda</span>', unsafe_allow_html=True)
        currency_opts = [f"{v['flag']} {k}" for k, v in CURRENCIES.items()]
        curr_keys = list(CURRENCIES.keys())
        curr_idx = curr_keys.index(curr) if curr in curr_keys else 0
        sel_currency = st.selectbox("Moeda", currency_opts, index=curr_idx, key="currency_sel", label_visibility="collapsed")
        new_curr = curr_keys[currency_opts.index(sel_currency)]
        if new_curr != st.session_state['currency']:
            st.session_state['currency'] = new_curr
            st.rerun()
        
        # Competição
        st.markdown('<span class="sec-label">Competição</span>', unsafe_allow_html=True)
        sel_comp = st.selectbox("Competição", list(comps.keys()),
                                index=list(comps.keys()).index(st.session_state['selected_comp']),
                                key='comp_sel', label_visibility="collapsed")
        st.session_state['selected_comp'] = sel_comp
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ── MERCADOS ────────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title"><i>🎯</i> MERCADOS</div>', unsafe_allow_html=True)
        
        default_d = ['BTTS', 'Over 2.5', 'Over 1.5', 'Under 3.5', '2º Tempo +']
        rev_map = {v: k for k, v in MARKET_MAP.items()}
        sel_disp = st.multiselect("Selecione os mercados", list(MARKET_MAP.values()),
                                  default=[m for m in default_d if m in MARKET_MAP.values()],
                                  key="market_sel", label_visibility="collapsed")
        selected_markets = [rev_map[m] for m in sel_disp]
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ── WATCHLIST ───────────────────────────────────────────────────────
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title"><i>📋</i> WATCHLIST</div>', unsafe_allow_html=True)
        
        new_m = st.text_input("Adicionar partida", placeholder="ex: Arsenal vs Chelsea", key="nmi", label_visibility="collapsed")
        if st.button("➕ Adicionar à Watchlist", use_container_width=True) and new_m:
            an.watchlist.append(new_m)
            st.session_state.watchlist = an.watchlist
            st.rerun()
        
        for i, mw in enumerate(an.watchlist):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f'<div style="padding:0.3rem 0;color:#a0a0c0">⚽ {mw}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"remove_{i}"):
                    an.watchlist.pop(i)
                    st.session_state.watchlist = an.watchlist
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    comp_id = comps[sel_comp]

    # ── CONTEÚDO PRINCIPAL ───────────────────────────────────────────────────
    
    # Seleção de Partida (sempre visível)
    with st.container():
        st.markdown('<div class="controls-container fade-in">', unsafe_allow_html=True)
        st.markdown('<span class="sec-label">⚽ SELECIONAR PARTIDA</span>', unsafe_allow_html=True)
        
        with st.spinner("Buscando partidas..."):
            matches = get_matches(comp_id)
        
        opts = []
        for m in matches:
            if m["status"] in ["SCHEDULED", "TIMED"]:
                try:
                    dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
                    opts.append({
                        "id": m["id"],
                        "home_id": m["homeTeam"]["id"],
                        "away_id": m["awayTeam"]["id"],
                        "disp": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']} · {dt.strftime('%d/%m %H:%M')}",
                        "home_team": m["homeTeam"]["name"],
                        "away_team": m["awayTeam"]["name"],
                        "date": dt
                    })
                except:
                    continue
        
        if not opts:
            st.warning("⚠️ Nenhuma partida encontrada para esta competição.")
            sel_match = None
        else:
            sel_str = st.selectbox("Partida", [o["disp"] for o in opts], key='match_sel', label_visibility="collapsed")
            sel_match = opts[[o["disp"] for o in opts].index(sel_str)]
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Configuração da Aposta (se partida selecionada)
    if sel_match:
        with st.container():
            st.markdown('<div class="controls-container fade-in">', unsafe_allow_html=True)
            st.markdown('<span class="sec-label">💰 CONFIGURAR APOSTA</span>', unsafe_allow_html=True)
            
            mc1, mc2, mc3 = st.columns([2, 1, 1])
            
            with mc1:
                mercado_jogo_disp = st.selectbox("Mercado principal", options=list(MARKET_MAP.values()),
                                                 key='mercado_jogo_sel', label_visibility="collapsed")
                mercado_jogo = {v: k for k, v in MARKET_MAP.items()}[mercado_jogo_disp]
            
            with mc2:
                odd_apostada = st.number_input("Odd", min_value=1.01, value=2.00, step=0.05, format="%.2f", key="odd_input")
            
            with mc3:
                stake = st.number_input(f"Stake ({c_info['symbol']})", min_value=0.0, value=10.0, step=1.0, format="%.2f", key="stake_input")
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Preview EV
        if st.session_state.get('last_analise'):
            prob_prev = st.session_state['last_analise'].get(f'prob_{mercado_jogo}', 0)
            ev_prev = calculate_value_bet(prob_prev, odd_apostada) or 0
            retorno = stake * odd_apostada
            lucro = retorno - stake
            ev_c = "#4ecdc4" if ev_prev > 0.05 else "#ffd93d" if ev_prev > 0 else "#ff6b6b"
            
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:0.8rem;margin:1rem 0">
                <div class="ev-box"><div class="ev-val" style="color:{ev_c}">{ev_prev:+.3f}</div><div class="ev-lbl">Expected Value</div></div>
                <div class="ev-box"><div class="ev-val" style="color:#4ecdc4">{prob_prev:.0f}%</div><div class="ev-lbl">Prob. Modelo</div></div>
                <div class="ev-box"><div class="ev-val" style="color:#c084fc">{fmt_money(retorno, curr)}</div><div class="ev-lbl">Retorno</div></div>
                <div class="ev-box"><div class="ev-val" style="color:{'#4ecdc4' if lucro>=0 else '#ff6b6b'}">{fmt_money(lucro, curr)}</div><div class="ev-lbl">Lucro</div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        if st.button("🚀 ANALISAR PARTIDA", use_container_width=True):
            with st.spinner(f"Analisando {sel_match['home_team']} vs {sel_match['away_team']}…"):
                try:
                    markets_to_use = list(set(selected_markets + [mercado_jogo]))
                    res = an.analisar(sel_match['home_team'], sel_match['away_team'], sel_comp,
                                       sel_match['home_id'], sel_match['away_id'], comp_id, markets_to_use)
                    res['mercado_escolhido'] = mercado_jogo
                    res['odd_apostada'] = odd_apostada
                    res['stake'] = stake
                    res['currency'] = curr
                    
                    if an.historico:
                        an.historico[-1]['mercado_escolhido'] = mercado_jogo
                        an.historico[-1]['odd_apostada'] = odd_apostada
                        an.historico[-1]['stake'] = stake
                        an.historico[-1]['currency'] = curr
                        an.historico[-1]['ev'] = round(calculate_value_bet(
                            an.historico[-1]['probs'].get(mercado_jogo, 50), odd_apostada) or 0, 3)
                        st.session_state.historico = an.historico
                    
                    st.session_state['last_analise'] = res
                    st.session_state['last_match'] = sel_match
                    
                except Exception as e:
                    st.error(f"Erro: {e}")

    # ── CONTEÚDO DAS TABS (baseado no menu) ───────────────────────────────────
    
    # ══════════════════════════════════════════════════════════
    # ANÁLISE
    # ══════════════════════════════════════════════════════════
    if st.session_state['menu'] == 'analise':
        if st.session_state['last_analise'] and st.session_state['last_match']:
            analise = st.session_state['last_analise']
            match = st.session_state['last_match']

            st.markdown(f"""
            <div class="match-banner fade-in">
                <div class="match-teams">
                    <div class="mh">🏠 {match['home_team']}</div>
                    <div class="mv">vs</div>
                    <div class="ma">🚩 {match['away_team']}</div>
                </div>
                <span class="match-date">📅 {match['date'].strftime('%d/%m · %H:%M')}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown('<span class="sec-label">📊 PROBABILIDADES</span>', unsafe_allow_html=True)
            render_metric_grid(analise, selected_markets)

            col_l, col_r = st.columns([3, 2])

            with col_l:
                st.markdown('<span class="sec-label">📈 DISTRIBUIÇÃO</span>', unsafe_allow_html=True)
                render_prob_bars(analise, selected_markets)

                h2h = analise['h2h']
                st.markdown(f"""
                <span class="sec-label">🤝 HEAD TO HEAD</span>
                <div class="h2h-grid">
                    <div class="h2h-tile"><div class="hv">{h2h['btts_h2h']:.0f}%</div><div class="hl">BTTS H2H</div></div>
                    <div class="h2h-tile"><div class="hv">{h2h['over25_h2h']:.0f}%</div><div class="hl">Over 2.5 H2H</div></div>
                </div>""", unsafe_allow_html=True)

            with col_r:
                st.markdown('<span class="sec-label">🔍 ANÁLISE</span>', unsafe_allow_html=True)
                render_detail_card(analise['detail_lines'])
                
                st.markdown('<span class="sec-label">🎯 RECOMENDAÇÕES</span>', unsafe_allow_html=True)
                if analise['recomendacoes']:
                    render_pills(analise['recomendacoes'])
                else:
                    st.info("Selecione mercados na sidebar.")

            with st.expander("💰 CALCULADORA DE VALUE BET"):
                if selected_markets:
                    n_cols = min(3, len(selected_markets))
                    vcols = st.columns(n_cols)
                    for j, mkt in enumerate(selected_markets):
                        with vcols[j % n_cols]:
                            prob = analise.get(f'prob_{mkt}', 0)
                            oj = analise.get(f'odd_justa_{mkt}', 1.5)
                            lbl = MARKET_MAP.get(mkt, mkt)
                            or_ = st.number_input(lbl, min_value=1.01, value=float(oj), step=0.01, format="%.2f", key=f"vi_{mkt}")
                            ev = calculate_value_bet(prob, or_) or 0
                            el = "✅ VALUE" if ev > 0.05 else "✓ Pequeno" if ev > 0 else "✗ Sem Value"
                            ec = "#4ecdc4" if ev > 0.05 else "#ffd93d" if ev > 0 else "#a0a0c0"
                            st.markdown(f'<div class="ev-box"><div class="ev-val" style="color:{ec}">{ev:+.3f}</div><div class="ev-lbl">{el}</div></div>', unsafe_allow_html=True)
                else:
                    st.info("Selecione mercados na sidebar.")

            lo = an.fetch_live_odds(match['home_team'], match['away_team'])
            if lo:
                with st.expander("📡 ODDS AO VIVO"):
                    for bk in lo[:2]:
                        st.markdown(f'<span class="sec-label">{bk["title"]}</span>', unsafe_allow_html=True)
                        mt = next((m for m in bk.get('markets', []) if m['key'] == 'totals'), None)
                        if mt:
                            ov = next((o['price'] for o in mt['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Over'), 'N/A')
                            un = next((o['price'] for o in mt['outcomes'] if o.get('point') == 2.5 and o.get('name') == 'Under'), 'N/A')
                            st.markdown(f'<div class="analysis-card" style="padding:0.8rem"><span>Over 2.5 <b style="color:#4ecdc4">@{ov}</b> &nbsp; Under 2.5 <b style="color:#4ecdc4">@{un}</b></span></div>', unsafe_allow_html=True)
        else:
            st.info("⚠️ Selecione uma partida e clique em 'ANALISAR PARTIDA' para ver os resultados.")

    # ══════════════════════════════════════════════════════════
    # PERFIS
    # ══════════════════════════════════════════════════════════
    elif st.session_state['menu'] == 'perfis':
        if st.session_state['last_match']:
            m_ = st.session_state['last_match']
            cid = comps[st.session_state['selected_comp']]
            with st.spinner("Carregando perfis…"):
                hp = fetch_team_profile(m_['home_id'], cid)
                ap = fetch_team_profile(m_['away_id'], cid)
            
            st.markdown('<span class="sec-label">📊 PERFIS DAS EQUIPAS</span>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                render_team_card(m_['home_team'], hp, "🏠")
            with c2:
                render_team_card(m_['away_team'], ap, "🚩")

            cats = ['Ataque', 'Defesa', 'BTTS', 'Over 2.5', 'Over 1.5']
            hv = [hp['ataque'] * 10, hp['defesa'] * 10, hp['btts'], hp['over25'], hp['over15']]
            av = [ap['ataque'] * 10, ap['defesa'] * 10, ap['btts'], ap['over25'], ap['over15']]

            fig = go.Figure()
            for name, vals, color, fill in [
                (m_['home_team'], hv, '#ff6b6b', 'rgba(255,107,107,0.1)'),
                (m_['away_team'], av, '#4ecdc4', 'rgba(78,205,196,0.1)')
            ]:
                fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]], fill='toself', name=name,
                                               line=dict(color=color, width=2), fillcolor=fill))
            
            fig.update_layout(
                polar=dict(bgcolor="rgba(255,255,255,0.02)",
                           radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)", 
                                         tickfont=dict(size=10, color="#a0a0c0")),
                           angularaxis=dict(gridcolor="rgba(255,255,255,0.1)", 
                                          tickfont=dict(size=11, color="#ffffff"))),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#a0a0c0"),
                legend=dict(font=dict(size=12, color="#ffffff"), 
                           bgcolor="rgba(0,0,0,0)", 
                           orientation="h", 
                           x=0.5, 
                           xanchor="center", 
                           y=-0.15),
                margin=dict(l=30, r=30, t=30, b=60),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Analise uma partida primeiro para ver os perfis.")

    # ══════════════════════════════════════════════════════════
    # HISTÓRICO
    # ══════════════════════════════════════════════════════════
    elif st.session_state['menu'] == 'historico':
        if an.historico:
            hist_sorted = list(reversed(an.historico))

            st.markdown('<span class="sec-label">📈 HISTÓRICO DE APOSTAS</span>', unsafe_allow_html=True)

            # Filtros
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                filtro_mercado = st.selectbox("Filtrar mercado", ["Todos"] + list(MARKET_MAP.values()),
                                               key="hist_fm")
            with col2:
                filtro_ev = st.selectbox("Filtrar EV",
                    ["Todos", "✅ Com Value (EV > 0)", "🔥 EV Forte (> 0.05)", "✗ Sem Value"],
                    key="hist_fev")
            with col3:
                if st.button("🗑 LIMPAR", use_container_width=True):
                    st.session_state.historico = []
                    an.historico.clear()
                    st.rerun()

            icons_m = {'btts': '🎯', 'over25': '⚽', 'over15': '⚽', 'under35': '🛡️', 'under25': '🛡️', 'second_half_more': '⏱️'}
            rev_map_h = {v: k for k, v in MARKET_MAP.items()}

            filtered = []
            for entry in hist_sorted:
                mkey = entry.get('mercado_escolhido', '')
                ev = entry.get('ev', 0)
                if filtro_mercado != "Todos" and mkey != rev_map_h.get(filtro_mercado, mkey):
                    continue
                if filtro_ev == "✅ Com Value (EV > 0)" and ev <= 0:
                    continue
                if filtro_ev == "🔥 EV Forte (> 0.05)" and ev <= 0.05:
                    continue
                if filtro_ev == "✗ Sem Value" and ev > 0:
                    continue
                filtered.append(entry)

            if not filtered:
                st.info("Nenhuma aposta encontrada com esses filtros.")
            else:
                total = len(filtered)
                com_value = sum(1 for e in filtered if e.get('ev', 0) > 0)
                ev_medio = round(sum(e.get('ev', 0) for e in filtered) / total, 3) if total else 0
                stake_tot = sum(e.get('stake', 0) for e in filtered)

                cols = st.columns(4)
                for col, lbl, val, c in [
                    (cols[0], "APOSTAS", str(total), "#ff6b6b"),
                    (cols[1], "COM VALUE", f"{com_value}/{total}", "#4ecdc4"),
                    (cols[2], "EV MÉDIO", f"{ev_medio:+.3f}", "#ffd93d" if ev_medio > 0 else "#ff6b6b"),
                    (cols[3], "STAKE TOTAL", fmt_money(stake_tot, curr), "#c084fc"),
                ]:
                    col.markdown(f"""
                    <div class="metric-card" style="margin-bottom:1rem">
                        <div class="mv" style="color:{c};font-size:1.3rem">{val}</div>
                        <div class="ml">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

                for entry in filtered:
                    mkey = entry.get('mercado_escolhido', 'btts')
                    mlabel = MARKET_MAP.get(mkey, mkey)
                    micon = icons_m.get(mkey, '🎯')
                    ev = entry.get('ev', 0)
                    odd_ap = entry.get('odd_apostada', 0)
                    stake_e = entry.get('stake', 0)
                    entry_curr = entry.get('currency', curr)
                    retorno = stake_e * odd_ap if odd_ap else 0
                    lucro = retorno - stake_e
                    probs = entry.get('probs', {})
                    prob_m = probs.get(mkey, entry.get('prob_btts', 0))

                    if ev > 0.05:
                        ev_cls, ev_c = "hm-g", "#4ecdc4"
                    elif ev > 0:
                        ev_cls, ev_c = "hm-y", "#ffd93d"
                    else:
                        ev_cls, ev_c = "hm-r", "#a0a0c0"

                    mini_pills = ""
                    for k, v in probs.items():
                        if k == mkey:
                            continue
                        t = THRESHOLDS.get(k, 60)
                        pc = "pill-g" if v >= t else "pill-y" if v >= t - 10 else "pill-s"
                        mini_pills += f'<span class="hist-mini-pill {pc}">{MARKET_MAP.get(k, k)} {v:.0f}%</span>'

                    stake_html = f'<span style="color:#c084fc">{fmt_money(stake_e, entry_curr)}</span>' if stake_e else ''
                    odd_html = f'<span style="color:#4ecdc4">@ {odd_ap:.2f}</span>' if odd_ap else ''
                    lucro_c = "#4ecdc4" if lucro >= 0 else "#ff6b6b"
                    lucro_html = f'<span style="color:{lucro_c}">{fmt_money(lucro, entry_curr)}</span>' if odd_ap else ''

                    st.markdown(f"""
                    <div class="hist-card fade-in">
                        <div class="hist-card-left">
                            <div class="hist-match">🏠 {entry['home']} <span style="color:#a0a0c0">vs</span> 🚩 {entry['away']}</div>
                            <div style="display:flex;gap:1rem;margin-top:0.3rem;flex-wrap:wrap">
                                <span class="hist-date">{entry['data']}</span>
                                {odd_html} {stake_html} {lucro_html}
                            </div>
                            <div class="hist-pills">{mini_pills}</div>
                        </div>
                        <div class="hist-right">
                            <span class="hist-market {ev_cls}">{micon} {mlabel}</span>
                            <span class="hist-prob">{prob_m:.0f}%</span>
                            <span style="color:{ev_c};font-weight:700">EV {ev:+.3f}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                pdf_b = an.gerar_pdf(curr)
                st.download_button(
                    "📥 EXPORTAR PDF",
                    data=pdf_b,
                    file_name="relatorio_bets.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("📊 Histórico vazio. Analise uma partida para popular.")

if __name__ == "__main__":
    main()
