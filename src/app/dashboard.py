import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import subprocess
import os
from src.database import get_connection
from src.ingestion.pipeline import ingest_historical

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="BTC Data Pipeline Dashboard",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Premium (Glassmorphism e Cores Harmoniosas)
st.markdown(
    """
    <style>
    /* Estilo geral */
    .stApp {
        background: #0E1117;
        color: #E2E8F0;
    }
    
    /* Customização dos Headers */
    h1, h2, h3 {
        color: #F59E0B !important;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Cartões Glassmorphic */
    .card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #FFFFFF;
        margin-top: 8px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tags de Status */
    .status-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-weight: 600;
    }
    
    .status-failure {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# CARREGAMENTO DE DADOS (DATABASE FETCH)
# ==============================================================================
@st.cache_data(ttl=10)
def fetch_silver_prices():
    """Busca dados da camada Silver (Normalizados)"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT price_timestamp, btc_usd, btc_brl, usd_brl, source, collected_at
        FROM silver.normalized_prices
        ORDER BY price_timestamp DESC
        LIMIT 1000;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=10)
def fetch_gold_prices(granularity: str):
    """Busca dados agregados da camada Gold"""
    table_name = f"gold.prices_aggregated_{granularity}"
    conn = None
    try:
        conn = get_connection()
        query = f"""
        SELECT interval_timestamp, avg_btc_usd, max_btc_usd, min_btc_usd, avg_btc_brl, avg_usd_brl, records_count
        FROM {table_name}
        ORDER BY interval_timestamp DESC
        LIMIT 500;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=5)
def fetch_pipeline_logs():
    """Busca logs de execução da pipeline de monitoramento"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT id, job_name, started_at, finished_at, status, records_processed, records_failed_quality, error_message
        FROM monitoring.pipeline_logs
        ORDER BY started_at DESC
        LIMIT 50;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()

@st.cache_data(ttl=5)
def fetch_quarantine_records():
    """Busca registros rejeitados em quarentena"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT id, collected_at, error_message, rejected_payload::text as payload
        FROM bronze.quarantine
        ORDER BY collected_at DESC
        LIMIT 50;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()

# ==============================================================================
# MENU LATERAL (SIDEBAR)
# ==============================================================================
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='color: #F59E0B; margin-bottom: 5px;'>🪙 BTC Pipeline</h2>
        <span style='color: #94A3B8; font-size: 14px;'>Monitoramento Inteligente</span>
    </div>
    """,
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Navegação",
    ["📈 Painel de Cotações", "📊 Granularidades (Gold)", "🛡️ Monitoramento e Qualidade"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Sobre o Protótipo")
st.sidebar.info(
    "Desenvolvido para a disciplina de Engenharia de Dados (Parte 2).\n\n"
    "**Alunos:**\n"
    "- João Bizzo (Matrícula: 22252028)\n"
    "- Pietra Paz (Matrícula: 22401571)"
)

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================
st.title("🪙 BTC Data Pipeline")
st.subheader("Ciclo de Vida de Engenharia de Dados - Monitoramento de Preços do Bitcoin")

# Testar conexão com o Banco
df_silver = fetch_silver_prices()

if df_silver is None or df_silver.empty:
    st.error("⚠️ Não foi possível conectar ao banco de dados ou a tabela 'silver.normalized_prices' está vazia.")
    st.info(
        "**Como inicializar o projeto?**\n"
        "1. Certifique-se de que os containers Docker estão rodando: `docker-compose up -d`\n"
        "2. Certifique-se de que a ingestão rodou pelo menos uma vez. Você pode rodar a DAG `btc_historical_backfill` no Airflow ou usar o botão de Backfill manual na aba **Monitoramento** deste painel."
    )
    
    # Adicionar botão de Backfill emergencial de bootstrap
    st.markdown("### ⚡ Inicialização Emergencial (Bootstrap)")
    if st.button("Executar Ingestão Histórica de 7 dias agora"):
        with st.spinner("Conectando ao CoinGecko e gerando tabelas..."):
            try:
                ingest_historical(days=7)
                # Tenta executar o dbt
                dbt_path = os.getenv("DBT_PROFILES_DIR", "/app/dbt_project")
                result = subprocess.run(
                    ["dbt", "run", "--project-dir", dbt_path, "--profiles-dir", dbt_path],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    st.success("Ingestão e transformação completadas! Recarregue a página (pressione F5 ou R).")
                    st.code(result.stdout)
                else:
                    st.error("Falha no dbt run!")
                    st.code(result.stdout + "\n" + result.stderr)
            except Exception as ex:
                st.exception(ex)
    st.stop()

# ==============================================================================
# ABA 1: PAINEL DE COTAÇÕES
# ==============================================================================
if menu == "📈 Painel de Cotações":
    # Obter dados mais recentes para os KPIs
    latest = df_silver.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="card">
                <div class="metric-label">Cotação Atual (USD)</div>
                <div class="metric-value">$ {latest['btc_usd']:,.2f}</div>
                <div style='color: #10B981; font-size: 14px; margin-top: 5px;'>Último registro UTC: {latest['price_timestamp'].strftime('%H:%M:%S')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            f"""
            <div class="card">
                <div class="metric-label">Cotação Atual (BRL)</div>
                <div class="metric-value">R$ {latest['btc_brl']:,.2f}</div>
                <div style='color: #94A3B8; font-size: 14px; margin-top: 5px;'>Fonte: CoinGecko API</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="card">
                <div class="metric-label">Câmbio Implícito BRL/USD</div>
                <div class="metric-value">R$ {latest['usd_brl']:,.4f}</div>
                <div style='color: #F59E0B; font-size: 14px; margin-top: 5px;'>Cálculo implícito pela paridade BTC</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Gráfico Principal de Preço do BTC
    st.markdown("### 📈 Histórico Recente de Preços do Bitcoin")
    
    # Botão de alternância
    currency_toggle = st.radio("Selecione a Moeda de Visualização", ["USD ($)", "BRL (R$)"], horizontal=True)
    
    fig = go.Figure()
    if currency_toggle == "USD ($)":
        fig.add_trace(go.Scatter(
            x=df_silver['price_timestamp'], 
            y=df_silver['btc_usd'],
            mode='lines', 
            name='BTC/USD',
            line=dict(color='#F59E0B', width=2)
        ))
        fig.update_layout(
            title="Preço do Bitcoin em USD ($)",
            yaxis_title="Preço (USD)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    else:
        fig.add_trace(go.Scatter(
            x=df_silver['price_timestamp'], 
            y=df_silver['btc_brl'],
            mode='lines', 
            name='BTC/BRL',
            line=dict(color='#10B981', width=2)
        ))
        fig.update_layout(
            title="Preço do Bitcoin em BRL (R$)",
            yaxis_title="Preço (BRL)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico do Câmbio Implícito
    st.markdown("### 💱 Histórico da Taxa de Câmbio Implícita (USD -> BRL)")
    fig_cambio = go.Figure()
    fig_cambio.add_trace(go.Scatter(
        x=df_silver['price_timestamp'], 
        y=df_silver['usd_brl'],
        mode='lines', 
        name='Câmbio Implícito',
        line=dict(color='#60A5FA', width=1.5)
    ))
    fig_cambio.update_layout(
        title="Dólar Comercial Implícito (BTC_BRL / BTC_USD)",
        yaxis_title="Câmbio (R$ por $)",
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_cambio, use_container_width=True)

# ==============================================================================
# ABA 2: GRANULARIDADES COMPARADAS (GOLD)
# ==============================================================================
elif menu == "📊 Granularidades (Gold)":
    st.markdown("### 📊 Camada Gold - Agregações e Downsampling")
    st.write(
        "Para otimizar consultas analíticas históricas de longo prazo, a camada Gold agrupa os dados "
        "em janelas de tempo de **2h**, **4h** e **Diário**, reduzindo drasticamente o número de linhas carregadas."
    )
    
    gran = st.selectbox("Selecione a Granularidade de Agrupamento", ["2h", "4h", "daily"])
    df_gold = fetch_gold_prices(gran)
    
    if df_gold is None or df_gold.empty:
        st.warning(f"Nenhum dado encontrado para a granularidade {gran} na camada Gold. Certifique-se de executar o `dbt run`.")
    else:
        # Gráficos da Gold
        fig_gold = go.Figure()
        fig_gold.add_trace(go.Scatter(
            x=df_gold['interval_timestamp'], 
            y=df_gold['avg_btc_usd'],
            mode='lines+markers', 
            name='Preço Médio (USD)',
            line=dict(color='#F59E0B', width=2)
        ))
        # Intervalo Min/Max com área sombreada para detalhar volatilidade
        fig_gold.add_trace(go.Scatter(
            x=pd.concat([df_gold['interval_timestamp'], df_gold['interval_timestamp'][::-1]]),
            y=pd.concat([df_gold['max_btc_usd'], df_gold['min_btc_usd'][::-1]]),
            fill='toself',
            fillcolor='rgba(245, 158, 11, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name="Volatilidade (Máx / Mín)"
        ))
        
        fig_gold.update_layout(
            title=f"Média de Preço e Volatilidade - Granularidade {gran.upper()}",
            yaxis_title="Preço USD ($)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_gold, use_container_width=True)
        
        # Exibição de tabela
        st.markdown("#### Detalhes dos Dados Agregados (Visualização de Amostra)")
        st.dataframe(df_gold, use_container_width=True)

# ==============================================================================
# ABA 3: MONITORAMENTO E QUALIDADE
# ==============================================================================
elif menu == "🛡️ Monitoramento e Qualidade":
    st.markdown("### 🛡️ Monitoramento de Pipeline, Qualidade e Governança")
    
    # Métricas de Qualidade Gerais
    df_logs = fetch_pipeline_logs()
    df_quarantine = fetch_quarantine_records()
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_runs = len(df_logs) if df_logs is not None else 0
    success_runs = len(df_logs[df_logs['status'] == 'SUCCESS']) if df_logs is not None else 0
    failed_runs = len(df_logs[df_logs['status'] == 'FAILURE']) if df_logs is not None else 0
    quarantine_count = len(df_quarantine) if df_quarantine is not None else 0
    
    with col1:
        st.markdown(f"<div class='card'><div class='metric-label'>Execuções Recentes</div><div class='metric-value'>{total_runs}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><div class='metric-label'>Execuções Sucesso</div><div class='metric-value' style='color: #10B981;'>{success_runs}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'><div class='metric-label'>Execuções Falha</div><div class='metric-value' style='color: #EF4444;'>{failed_runs}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card'><div class='metric-label'>Itens na Quarentena</div><div class='metric-value' style='color: #F59E0B;'>{quarantine_count}</div></div>", unsafe_allow_html=True)

    # Disparador manual de Backfill e dbt
    st.markdown("### ⚡ Operação Manual do Pipeline")
    c_bf, c_dbt = st.columns(2)
    with c_bf:
        st.markdown("#### Backfill de Dados Históricos")
        days_input = st.number_input("Dias de histórico para carregar", min_value=1, max_value=60, value=7)
        if st.button("Executar Backfill Histórico"):
            with st.spinner(f"Ingerindo cotações dos últimos {days_input} dias..."):
                try:
                    ingest_historical(days=days_input)
                    st.success("Ingestão concluída no banco!")
                except Exception as ex:
                    st.error(f"Erro na ingestão: {ex}")
                    
    with c_dbt:
        st.markdown("#### Reprocessamento dbt")
        st.write("Executa as transformações SQL e validações de qualidade no dbt.")
        if st.button("Executar dbt run"):
            with st.spinner("Executando modelos dbt..."):
                try:
                    dbt_path = os.getenv("DBT_PROFILES_DIR", "/app/dbt_project")
                    result = subprocess.run(
                        ["dbt", "run", "--project-dir", dbt_path, "--profiles-dir", dbt_path],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        st.success("dbt run executado com SUCESSO!")
                        st.code(result.stdout)
                    else:
                        st.error("Falha no dbt run!")
                        st.code("STDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr)
                except Exception as ex:
                    st.error(f"Erro ao disparar dbt: {ex}")

    # Logs de Execução da Pipeline
    st.markdown("### 📜 Logs de Execução da Pipeline")
    if df_logs is None or df_logs.empty:
        st.info("Nenhum log registrado na tabela `monitoring.pipeline_logs`.")
    else:
        # Formatar status para visualização bonita
        def format_status(val):
            if val == 'SUCCESS':
                return "✅ Sucesso"
            elif val == 'FAILURE':
                return "❌ Falha"
            else:
                return "🔄 Executando"
        
        df_logs_display = df_logs.copy()
        df_logs_display['status'] = df_logs_display['status'].apply(format_status)
        st.dataframe(df_logs_display, use_container_width=True)

    # Dados da Quarentena
    st.markdown("### 🛡️ Quarentena de Qualidade (Auditoria de Registros Rejeitados)")
    st.write(
        "Quando dados brutos obtidos da CoinGecko falham nas regras de qualidade "
        "(ex: preços negativos, chaves duplicadas ou nulos), eles são retidos aqui para governança, "
        "impedindo que afetem o dashboard e permitindo auditoria detalhada."
    )
    if df_quarantine is None or df_quarantine.empty:
        st.success("✅ Excelente! Nenhum registro na quarentena. Todos os dados coletados possuem 100% de qualidade.")
    else:
        st.dataframe(df_quarantine, use_container_width=True)
