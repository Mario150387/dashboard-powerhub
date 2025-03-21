import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# Configurações do Streamlit
st.set_page_config(page_title="Dashboard PowerHub", layout="wide")

# Carregar as credenciais do Streamlit Secrets
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

# Conectar com a planilha
client = gspread.authorize(creds)

# Função para carregar dados da planilha
@st.cache_data(ttl=60)
def carregar_dados():
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1A0KvaF2koNvQAwaaRTNhqfurLUdXk89kQNO9HnjxTjQ/edit?usp=sharing")
    sheet = spreadsheet.worksheet("Página1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    # Limpando as margens (R$ para número)
    cols_margens = ["Margem Atualizada Produto", "Margem Novo", "Margem RMC", "Margem RCC"]
    for col in cols_margens:
        df[col] = df[col].replace({'R\$': '', ',': '.'}, regex=True).astype(float)
    return df

# Carregar dados
df = carregar_dados()

# Layout da Dashboard
st.image("logo_empresa.png", width=80)
st.title("Dashboard PowerHub")

consultoras = df['Consultora'].unique()
consultora_selecionada = st.sidebar.selectbox("Filtrar por Consultora", options=["Todas"] + list(consultoras))

if consultora_selecionada != "Todas":
    df = df[df['Consultora'] == consultora_selecionada]

# KPIs margens
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Margem Produto", f"R$ {df['Margem Atualizada Produto'].sum():,.2f}")
col2.metric("Total Margem Novo", f"R$ {df['Margem Novo'].sum():,.2f}")
col3.metric("Total Margem RMC", f"R$ {df['Margem RMC'].sum():,.2f}")
col4.metric("Total Margem RCC", f"R$ {df['Margem RCC'].sum():,.2f}")

# Exibir dados
st.subheader("Tabela Completa")
st.dataframe(df)
