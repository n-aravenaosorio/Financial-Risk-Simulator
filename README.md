# 📉 Sistema de Simulación de Riesgo Financiero (Monte Carlo & Power BI)

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

> **Una arquitectura Full-Stack para la gestión de riesgos de mercado.** > Este proyecto automatiza la extracción de datos financieros, calcula métricas de riesgo (VaR, Expected Shortfall) utilizando simulaciones de Monte Carlo y visualiza los resultados en un tablero ejecutivo para la toma de decisiones.

---

## 📸 Vista Previa del Resultado

### 1. El Tablero de Control (Power BI)
*Un dashboard ejecutivo que permite identificar activos de alto riesgo (rojo) frente a activos seguros (verde) en tiempo real.*

![Dashboard Power BI](img/power-bi-dashboard.png) 
*(Asegúrate de poner tu captura aquí: img/dashboard_full.png)*

### 2. La Interfaz de Simulación (Streamlit)
*Aplicación web construida en Python para configurar y ejecutar simulaciones bajo demanda.*

![App Streamlit](img/streamlit_app.png)
*(Pon aquí la captura de tu página web)*

---


## 📂 Arquitectura del Código

El sistema está modularizado en 4 componentes clave. A continuación se explica la lógica general de cada uno:

### 1. Base de Datos (`src/database.py`)
Es la base del sistema. Aquí definimos la estructura de las tablas usando **SQLAlchemy (ORM)**. Creamos un modelo relacional donde cada "Activo" (`Asset`) es padre de sus precios históricos (`MarketData`) y de sus simulaciones de riesgo (`SimulationResult`). Esto garantiza que los datos estén ordenados y listos para ser consumidos por Power BI.

![Código Base de Datos](img/code-database-py.png)

---

### 2. Extracción de Datos (`src/extract.py`)
Este módulo se encarga de la ingesta de datos (ETL). Se conecta a la API de Yahoo Finance, descarga la historia de precios del activo solicitado, limpia la información (eliminando nulos) y la guarda masivamente en nuestra base de datos SQL. Incluye lógica para evitar duplicados si el activo ya existe.

![Código Extracción](img/code-extract-py.png)

---

### 3. Motor de Simulación (`src/simulation.py`)
El "cerebro" matemático del proyecto. En lugar de usar bucles lentos, utiliza **NumPy** para vectorizar operaciones.
* Calcula los retornos logarítmicos del activo.
* Aplica la fórmula del **Movimiento Browniano Geométrico** para proyectar miles de escenarios futuros en milisegundos.
* Calcula estadísticamente el **VaR 95%**, **VaR 99%** y el **Expected Shortfall (ES)** y guarda los resultados para su análisis posterior.

![Código Simulación](img/code-simulation-py.png)

---

### 4. Interfaz Principal (`src/main.py`)
Es el orquestador que une todo. Construido con **Streamlit**, crea una página web interactiva donde el usuario puede:
1.  Ingresar un Ticker (ej: TSLA).
2.  Ver gráficos interactivos con **Plotly**.
3.  Configurar parámetros (Días a proyectar, Cantidad de escenarios).
4.  Ejecutar la simulación con un clic, la cual dispara internamente los procesos de cálculo y guardado en base de datos.

![Código Main](img/code-main-py.png)

---

## 🚀 Características Principales

* **🔄 Pipeline ETL Automatizado:** Descarga precios históricos reales desde Yahoo Finance y los limpia automáticamente.
* **💾 Base de Datos SQL:** Almacenamiento persistente de millones de registros de precios y resultados de simulaciones en SQLite.
* **🎲 Motor Monte Carlo Vectorizado:** Uso de `NumPy` para ejecutar miles de escenarios estocásticos en segundos.
* **📊 Métricas de Riesgo Institucional:** Cálculo automático de:
    * **VaR 95% y 99%** (Value at Risk).
    * **Expected Shortfall (ES)** (Pérdida en escenarios de crisis).
* **📈 Visualización Business Intelligence:** Integración nativa con Power BI para análisis visual y matrices de riesgo.

---



## 🛠️ Arquitectura del Sistema

El proyecto sigue un flujo de datos lineal y robusto:

```mermaid
graph LR
A[Yahoo Finance API] -- JSON --> B(Python ETL)
B -- Clean Data --> C[(SQLite Database)]
C -- Historical Prices --> D{Monte Carlo Engine}
D -- Risk Metrics --> C
C -- ODBC/SQL --> E[Power BI Dashboard]
