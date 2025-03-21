import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# Autenticação Google
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file('/Users/marioandrade/Documents/script/credentials.json', scopes=scope)
client = gspread.authorize(creds)

# Função para carregar dados
def carregar_dados():
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1A0KvaF2koNvQAwaaRTNhqfurLUdXk89kQNO9HnjxTjQ/edit?usp=sharing")
    ws = spreadsheet.worksheet("Log_consultas")
    df = pd.DataFrame(ws.get_all_records())
    return df

# ====== HEADER COM LOGO ======
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("/Users/marioandrade/Documents/script/logo_empresa.png", width=160)  # <-- pode trocar pela sua logo
with col_title:
    st.markdown("<h2 style='margin-bottom: 0;'>Dashboard de Consultas Automáticas</h2><p style='color: gray;'>Versão Interna - PowerHub</p>", unsafe_allow_html=True)

st.markdown("---")

# Controle de sessão
if "df" not in st.session_state:
    st.session_state.df = None

if st.button("🔄 Carregar / Atualizar Dados"):
    st.session_state.df = carregar_dados()

if st.session_state.df is None:
    st.warning("👆 Clique no botão acima para carregar os dados.")
    st.stop()
else:
    df = st.session_state.df

# Função de limpeza das margens
def limpar_margens(col):
    return pd.to_numeric(
        col.str.replace("R$", "", regex=False).str.replace(" ", "").str.replace(",", "."),
        errors="coerce"
    )

df["Margem novo"] = limpar_margens(df["Margem novo"].astype(str))
df["Margem RMC"] = limpar_margens(df["Margem RMC"].astype(str))
df["Margem RCC"] = limpar_margens(df["Margem RCC"].astype(str))

# ------------------------------
# Filtro por Consultora
# ------------------------------
st.markdown("### 🎯 Filtros")
consultoras = df["Consultora"].dropna().unique().tolist()
consultoras.sort()
consultora_selecionada = st.selectbox("Selecione uma Consultora:", ["Todas"] + consultoras)

if consultora_selecionada != "Todas":
    df = df[df["Consultora"] == consultora_selecionada]

st.markdown("---")

# ------------------------------
# KPIs principais
# ------------------------------
st.markdown("### 📊 Indicadores Gerais")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Registros", len(df))
col2.metric("Higienizados", df[df["Status"] == "Higienizado"].shape[0])
col3.metric("Erros", df[df["Status"].str.startswith("Erro")].shape[0])
sucesso_pct = (df[df["Status"] == "Higienizado"].shape[0] / len(df)) * 100 if len(df) else 0
col4.metric("Sucesso (%)", f"{sucesso_pct:.1f}%")

st.markdown("---")

# ------------------------------
# Clientes com margens acima de R$50
# ------------------------------
st.markdown("### 💼 Análise de Margens")

df_50 = df[
    (df["Margem novo"] > 50) |
    (df["Margem RMC"] > 50) |
    (df["Margem RCC"] > 50)
]
qtd_acima_50 = len(df_50)
st.metric("Clientes com Margem > R$50", qtd_acima_50)

# Gráfico de pizza
labels = ["Acima de R$50", "Abaixo ou Sem Margem"]
sizes = [qtd_acima_50, len(df) - qtd_acima_50]
fig, ax = plt.subplots(figsize=(4, 4))
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

# ------------------------------
# Totais das margens
# ------------------------------
st.markdown("### 💰 Totais das Margens (R$)")
col5, col6, col7 = st.columns(3)
col5.metric("Margem Novo", f"R$ {df['Margem novo'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col6.metric("Margem RMC", f"R$ {df['Margem RMC'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col7.metric("Margem RCC", f"R$ {df['Margem RCC'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

# ------------------------------
# Top consultoras
# ------------------------------
if consultora_selecionada == "Todas":
    st.markdown("### 🏆 Top 5 Consultoras (Higienizados)")
    top_consultoras = df[df["Status"] == "Higienizado"]["Consultora"].value_counts().head(5)
    st.table(top_consultoras)
