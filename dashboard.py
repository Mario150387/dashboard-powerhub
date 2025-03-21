import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configurar a página
st.set_page_config(page_title="Dashboard PowerHub", layout="wide")

# Carregar dados do secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

@st.cache_data(ttl=300)
def carregar_dados():
    # Abre a planilha pelo link
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1A0KvaF2koNvQAwaaRTNhqfurLUdXk89kQNO9HnjxTjQ/edit?usp=sharing")
    # Ajuste do nome da worksheet
    sheet = spreadsheet.worksheet("Log_consultas")
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    
    # Limpeza de coluna de valores
    colunas_valores = ['Margem Novo', 'Margem Atualizada', 'Margem RMC', 'Margem RCC']
    for coluna in colunas_valores:
        df[coluna] = df[coluna].replace({'R\$': '', ',': '.', '\.': '', '\s': ''}, regex=True).astype(float)
    
    return df

# Carregar dados
df = carregar_dados()

# Interface
st.image("logo_empresa.png", width=80)
st.title("📊 Dashboard PowerHub")
consultoras = df["Consultora"].unique()
filtro_consultora = st.sidebar.multiselect("Filtrar por Consultora", options=consultoras, default=consultoras)

df_filtrado = df[df["Consultora"].isin(filtro_consultora)]

# KPIs Totais
st.subheader("🔢 Indicadores Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Consultas Realizadas", len(df_filtrado))
col2.metric("Total Margem Novo (R$)", f"R$ {df_filtrado['Margem Novo'].sum():,.2f}")
col3.metric("Total Margem Atualizada (R$)", f"R$ {df_filtrado['Margem Atualizada'].sum():,.2f}")

# KPIs adicionais
col4, col5 = st.columns(2)
col4.metric("Total Margem RMC (R$)", f"R$ {df_filtrado['Margem RMC'].sum():,.2f}")
col5.metric("Total Margem RCC (R$)", f"R$ {df_filtrado['Margem RCC'].sum():,.2f}")

# Tabela de dados
st.subheader("📄 Tabela de Consultas")
st.dataframe(df_filtrado, use_container_width=True)
