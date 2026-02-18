import streamlit as st
import duckdb
import pandas as pd

from utils import measure_query

# Configuração DuckDB
duckdb.sql("INSTALL httpfs;")
duckdb.sql("LOAD httpfs;")

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"

st.set_page_config(page_title="Performance SQL - Táxi NYC", layout="wide")
st.title("🚕 Comparação de Performance e Uso de Recursos em Queries SQL")

st.markdown("""
Este dashboard apresenta cinco pares de consultas SQL que ilustram o impacto de boas práticas  
(projeção de colunas, LIMIT, filtros precoces) no tempo de execução e no consumo de memória.
""")

# Carregamento único do dataset (feito uma vez)
with st.spinner("Carregando dataset completo (~3M linhas) na memória... Pode levar até 1 minuto na primeira execução."):
    duckdb.sql(f"CREATE OR REPLACE TABLE taxi AS SELECT * FROM read_parquet('{url}')")

# Metadados (agora instantâneos)
total_rows = duckdb.sql("SELECT COUNT(*) FROM taxi").fetchone()[0]

st.info(f"📊 Dataset carregado: **{total_rows:,}** linhas (NYC Yellow Taxi – Janeiro/2023)")

# ========================================
# 5 PARES DE QUERIES (agora todas usam a tabela 'taxi' pré-carregada)
# ========================================

queries = {
    "1. Preview básico: carregamento amplo vs controlado": {
        "explicacao": "Carregamento de 20 mil linhas completas versus apenas 1 mil linhas com colunas essenciais.",
        "simples": f"SELECT * FROM taxi LIMIT 20000",
        "desc_simples": "Todas as colunas e 20 mil linhas",
        "otimizada": f"SELECT VendorID, tpep_pickup_datetime, passenger_count, trip_distance, total_amount FROM taxi LIMIT 1000",
        "desc_otimizada": "Colunas selecionadas e limite reduzido"
    },
    "2. Agregação simples: full scan vs filtro precoce": {
        "explicacao": "Cálculo de média e contagem por VendorID em todo o dataset versus apenas na segunda metade do mês.",
        "simples": f"SELECT VendorID, AVG(total_amount) AS media, COUNT(*) AS contagem FROM taxi GROUP BY VendorID",
        "desc_simples": "Agregação sobre todo o dataset",
        "otimizada": f"SELECT VendorID, AVG(total_amount) AS media, COUNT(*) AS contagem FROM taxi WHERE tpep_pickup_datetime >= '2023-01-15' GROUP BY VendorID",
        "desc_otimizada": "Filtro precoce antes da agregação"
    },
    "3. Top valores: ordenação completa vs projeção reduzida": {
        "explicacao": "Busca das 100 viagens mais caras carregando todas as colunas versus apenas as necessárias.",
        "simples": f"SELECT * FROM taxi ORDER BY total_amount DESC LIMIT 100",
        "desc_simples": "Ordenação com todas as colunas",
        "otimizada": f"SELECT tpep_pickup_datetime, passenger_count, trip_distance, total_amount FROM taxi ORDER BY total_amount DESC LIMIT 100",
        "desc_otimizada": "Projeção reduzida antes da ordenação"
    },
    "4. Group by detalhado: alta cardinalidade com/sem filtro": {
        "explicacao": "Agrupamento por zona de embarque (alta cardinalidade) em todo o dataset versus com filtro prévio.",
        "simples": f"SELECT PULocationID, AVG(total_amount), COUNT(*) FROM taxi GROUP BY PULocationID ORDER BY COUNT(*) DESC",
        "desc_simples": "Group by sobre todo o dataset",
        "otimizada": f"SELECT PULocationID, AVG(total_amount), COUNT(*) FROM taxi WHERE passenger_count >= 2 GROUP BY PULocationID ORDER BY COUNT(*) DESC",
        "desc_otimizada": "Filtro aplicado antes do group by"
    },
    "5. Ordenamento completo vs limitado": {
        "explicacao": "Ordenação de todo o dataset por data versus ordenação limitada com projeção mínima.",
        "simples": f"SELECT * FROM taxi ORDER BY tpep_pickup_datetime",
        "desc_simples": "Ordenação completa de todas as colunas",
        "otimizada": f"SELECT tpep_pickup_datetime, total_amount FROM taxi ORDER BY tpep_pickup_datetime LIMIT 5000",
        "desc_otimizada": "Ordenação limitada e colunas reduzidas"
    }
}

# Sidebar com radio buttons
st.sidebar.header("Selecione o par de queries")
opcao = st.sidebar.radio("Escolha um teste:", list(queries.keys()))

par = queries[opcao]

# Exibição do par selecionado
st.markdown("---")
st.subheader(opcao)
st.write(par["explicacao"])

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🔴 Query Simples**")
    st.code(par["simples"], language="sql", height=200)
    st.caption(par["desc_simples"])
    with st.spinner("Executando..."):
        metrics_simples = measure_query(par["simples"])
    if metrics_simples["error"]:
        st.error(f"Falha na execução: {metrics_simples['error']}")
    else:
        st.metric("Tempo (s)", f"{metrics_simples['tempo']:.2f}")
        st.metric("Memória Δ (MB)", f"{metrics_simples['memoria_delta_mb']:.1f}")
        st.dataframe(metrics_simples["result"].head(10))

with col2:
    st.markdown("**🟢 Query Otimizada**")
    st.code(par["otimizada"], language="sql", height=200)
    st.caption(par["desc_otimizada"])
    with st.spinner("Executando..."):
        metrics_otimizada = measure_query(par["otimizada"])
    if metrics_otimizada["error"]:
        st.error(f"Falha na execução: {metrics_otimizada['error']}")
    else:
        st.metric("Tempo (s)", f"{metrics_otimizada['tempo']:.2f}")
        st.metric("Memória Δ (MB)", f"{metrics_otimizada['memoria_delta_mb']:.1f}")
        st.dataframe(metrics_otimizada["result"].head(10))

# Gráfico comparativo (ordem forçada)
if not metrics_simples["error"] and not metrics_otimizada["error"]:
    comparacao = pd.DataFrame({
        "Tipo": ["Simples", "Otimizada"],
        "Tempo (s)": [metrics_simples["tempo"], metrics_otimizada["tempo"]],
        "Memória Δ (MB)": [metrics_simples["memoria_delta_mb"], metrics_otimizada["memoria_delta_mb"]]
    })
    comparacao["Tipo"] = pd.Categorical(comparacao["Tipo"], categories=["Simples", "Otimizada"], ordered=True)
    
    st.bar_chart(comparacao, x="Tipo", y=["Tempo (s)", "Memória Δ (MB)"], use_container_width=True)

st.caption("Projeto de portfólio • DuckDB + Streamlit • Comparação de eficiência de recursos")