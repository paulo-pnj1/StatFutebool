# Analisador Automático de Apostas em Futebol

Sistema de análise estatística para identificação de oportunidades de apostas de valor (value bets) em futebol, baseado em dados reais de competições europeias.

Desenvolvido com **Streamlit** e integrado às APIs da **football-data.org** e (opcionalmente) **The Odds API**.

## Funcionalidades Principais

- Extração e análise automática de partidas futuras das principais ligas europeias
- Cálculo de probabilidades estimadas para os mercados mais relevantes:
  - Ambas as equipas marcam (BTTS)
  - Mais/Menos de 2.5 gols
  - Mais/Menos de 1.5 gols
  - Mais/Menos de 3.5 gols
  - Maior número de gols no segundo tempo
- Construção de perfis quantitativos de equipas (ataque, defesa, estilo de jogo)
- Ajustes contextuais baseados em:
  - Estilo de jogo das equipas envolvidas
  - Histórico de confrontos diretos (H2H)
  - Padrões característicos da competição
- Cálculo de odds justas (fair odds) e Expected Value (EV) para detecção de value bets
- Integração opcional com odds em tempo real (The Odds API)
- Sistema de watchlist com alertas por email
- Exportação de relatórios analíticos em formato PDF
- Interface interativa com visualização de probabilidades (gauges Plotly)

## Mercados Suportados

| Código             | Descrição                          | Probabilidade calculada | Odd justa | Recomendação |
|--------------------|------------------------------------|--------------------------|-----------|--------------|
| btts               | Ambas as equipas marcam            | Sim                      | Sim       | Sim          |
| over25             | Mais de 2.5 gols                   | Sim                      | Sim       | Sim          |
| over15             | Mais de 1.5 gols                   | Sim                      | Sim       | Sim          |
| under35            | Menos de 3.5 gols                  | Sim                      | Sim       | Sim          |
| under25            | Menos de 2.5 gols                  | Sim                      | Sim       | Sim          |
| second_half_more   | Mais gols no segundo tempo         | Sim                      | Sim       | Sim          |

## Requisitos e Instalação

### Pré-requisitos

- Python ≥ 3.9
- Chave de API da [football-data.org](https://www.football-data.org/) (plano gratuito suficiente para uso individual)

### Instalação

1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/futebol-analise-apostas.git
cd futebol-analise-apostas
