import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configurar acesso ao Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Função para carregar dados
@st.cache_data(ttl=300)
def carregar_dados():
    spreadsheet = client.open_by_url(st.secrets["sheet_url"])
    sheet = spreadsheet.worksheet("Log_consultas")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Limpeza dos dados das colunas de margem
    colunas_margem = ["Margem novo", "Margem RMC", "Margem RCC"]
    for coluna in colunas_margem:
        df[coluna] = df[coluna].replace({'R\$': '', ',': '.', '\.': '', '\s': ''}, regex=True).astype(float)
    
    return df

# Interface
st.image("logo_empresa.png", width=120)
st.title("Dashboard de Monitoramento PowerHub 🚀")

# Carregar dados
df = carregar_dados()

# Exibir métricas
st.subheader("Resumo das Margens")
st.metric("Total Margem novo", f"R$ {df['Margem novo'].sum():.2f}")
st.metric("Total Margem RMC", f"R$ {df['Margem RMC'].sum():.2f}")
st.metric("Total Margem RCC", f"R$ {df['Margem RCC'].sum():.2f}")

# Exibir dados da tabela
st.dataframe(df)
