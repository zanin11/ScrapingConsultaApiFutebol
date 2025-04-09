
import streamlit as st
import pandas as pd
import requests
import time
import seaborn as sns
import matplotlib.pyplot as plt

# Título do app
st.title("📊 Análise de Dados de Futebol - Premier League")

# API Info
API_KEY = '914df061a15c95578b2ae6f4ae4bff4e'
headers = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

# Função com delay para evitar excesso de requisições
def request_with_limit(url, params):
    time.sleep(6)
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Sidebar com filtros
st.sidebar.header("⚙️ Filtros")
season = st.sidebar.selectbox("Temporada", options=["2021", "2022", "2023"], index=0)
league_id = 39  # Premier League

# URLs
base_url = "https://v3.football.api-sports.io"
endpoints = {
    "Classificação": f"{base_url}/standings",
    "Artilheiros": f"{base_url}/players/topscorers",
    "Cartões Vermelhos": f"{base_url}/players/topredcards",
    "Cartões Amarelos": f"{base_url}/players/topyellowcards"
}

# Seção de visualização
selecao = st.sidebar.radio("📂 Selecione a análise", list(endpoints.keys()))

params = {
    'league': league_id,
    'season': season
}

# Requisição à API
data = request_with_limit(endpoints[selecao], params)

# Exibição baseada na escolha
if selecao == "Classificação":
    try:
        standings = data['response'][0]['league']['standings'][0]
        df = pd.DataFrame(standings)
        df_show = df[['rank', 'team', 'points', 'goalsDiff', 'all']]
        df_show['team'] = df_show['team'].apply(lambda x: x['name'])
        df_show['played'] = df_show['all'].apply(lambda x: x['played'])
        df_show['wins'] = df_show['all'].apply(lambda x: x['win'])
        df_show['draws'] = df_show['all'].apply(lambda x: x['draw'])
        df_show['loses'] = df_show['all'].apply(lambda x: x['lose'])
        df_show = df_show.drop(columns='all')

        st.subheader("🏆 Classificação da Premier League")
        st.dataframe(df_show)

        st.bar_chart(df_show.set_index('team')['points'])

    except Exception as e:
        st.error("Erro ao carregar classificação.")
        st.exception(e)

else:
    try:
        players = data['response']
        df = pd.DataFrame(players)
        df['nome'] = df['player'].apply(lambda x: x['name'])
        df['time'] = df['statistics'].apply(lambda x: x[0]['team']['name'])

        if selecao == "Artilheiros":
            df['gols'] = df['statistics'].apply(lambda x: x[0]['goals']['total'])
            df_show = df[['nome', 'time', 'gols']].sort_values(by='gols', ascending=False)
            st.subheader("⚽ Artilheiros")
        elif selecao == "Cartões Vermelhos":
            df['reds'] = df['statistics'].apply(lambda x: x[0]['cards']['red'])
            df_show = df[['nome', 'time', 'reds']].sort_values(by='reds', ascending=False)
            st.subheader("🔴 Cartões Vermelhos")
        elif selecao == "Cartões Amarelos":
            df['yellows'] = df['statistics'].apply(lambda x: x[0]['cards']['yellow'])
            df_show = df[['nome', 'time', 'yellows']].sort_values(by='yellows', ascending=False)
            st.subheader("🟡 Cartões Amarelos")

        st.dataframe(df_show)

        col = df_show.columns[-1]
        st.bar_chart(df_show.set_index('nome')[col])

    except Exception as e:
        st.error("Erro ao carregar dados dos jogadores.")
        st.exception(e)
