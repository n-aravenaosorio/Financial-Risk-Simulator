import sys
import os

# CORRECCIÓN
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database import SessionLocal, Asset, MarketData, SimulationResult
from src.extract import DataIngestion
from src.simulation import MonteCarloEngine



st.set_page_config(page_title="Risk Simulator", layout="wide")
st.title("📊 Financial Risk Simulator")
st.markdown("---")

db = SessionLocal()

st.sidebar.header("⚙️ Configuración")

assets = db.query(Asset).all()
asset_options = {a.symbol: a.id for a in assets}

if not asset_options:
    st.sidebar.warning("No hay activos. Usa el botón de abajo.")
    selected_ticker = None
else:
    selected_ticker = st.sidebar.selectbox("Selecciona un Activo", list(asset_options.keys()))

st.sidebar.markdown("### 📥 Ingesta de Datos")
new_ticker = st.sidebar.text_input("Nuevo Ticker (ej: GOOGL)")

if st.sidebar.button("Descargar/Actualizar Data"):
    ticker_to_download = new_ticker if new_ticker else selected_ticker
    
    if ticker_to_download:
        with st.spinner(f"Descargando datos de {ticker_to_download}..."):
            etl = DataIngestion(db)
            data = etl.get_stock_data(ticker_to_download)
            if data is not None:
                etl.save_market_data(ticker_to_download, data)
                st.success(f"Datos de {ticker_to_download} actualizados exitosamente.")
                st.rerun()
            else:
                st.error("Error al descargar. Verifica el ticker.")
    else:
        st.error("Escribe un ticker para descargar.")

if selected_ticker:
    asset_id = asset_options[selected_ticker]
    
    query = db.query(MarketData).filter(MarketData.asset_id == asset_id).order_by(MarketData.date)
    df = pd.read_sql(query.statement, db.bind)

    if not df.empty:
        st.subheader(f"📈 Historia de Precios: {selected_ticker}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Precio Cierre', line=dict(color='#00CC96')))
        fig.update_layout(height=400, xaxis_title="Fecha", yaxis_title="Precio (USD)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🎲 Motor de Simulación Monte Carlo")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_days = st.number_input("Días a proyectar", value=252, min_value=30, step=10)
        with col2:
            n_sims = st.number_input("N° Escenarios", value=500, min_value=100, max_value=2000, step=100)
        with col3:
            st.write("")
            st.write("") 
            run_btn = st.button("🚀 Ejecutar Simulación", type="primary")

        if run_btn:
            with st.spinner("Calculando miles de escenarios futuros..."):
                sim_engine = MonteCarloEngine(db)
                sim_engine.run_simulation(selected_ticker, days_ahead=sim_days, simulations=n_sims)
                
                last_result = db.query(SimulationResult).filter(SimulationResult.asset_id == asset_id).order_by(SimulationResult.run_date.desc()).first()
                
                if last_result:
                    st.success("¡Simulación completada!")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("VaR 95% (Riesgo Normal)", f"${last_result.var_95:.2f}", delta_color="inverse")
                    m2.metric("VaR 99% (Crisis)", f"${last_result.var_99:.2f}", delta_color="inverse")
                    m3.metric("Pérdida Esperada (ES)", f"${last_result.expected_shortfall:.2f}", delta_color="inverse")
                    
                    st.info(f"Interpretación: Con un 95% de confianza, la pérdida máxima esperada en {sim_days} días no superará los ${last_result.var_95:.2f} por acción.")

    else:
        st.warning("El activo existe pero no tiene precios históricos. Usa el botón de la izquierda para descargar data.")

db.close()