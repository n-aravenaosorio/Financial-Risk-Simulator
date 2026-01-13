import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from src.database import SessionLocal, Asset, MarketData, SimulationResult
from datetime import datetime

class MonteCarloEngine:
    def __init__(self, db_session: Session):
        self.session = db_session

    def run_simulation(self, ticker: str, days_ahead: int = 252, simulations: int = 1000):
        print(f"\n🎲 Iniciando simulación Monte Carlo para {ticker} ({simulations} escenarios)...")
        
        asset = self.session.query(Asset).filter_by(symbol=ticker).first()
        if not asset:
            print(f"❌ Error: El activo {ticker} no existe en la BD. Ejecuta el ETL primero.")
            return

        query = self.session.query(MarketData.close).filter_by(asset_id=asset.id).order_by(MarketData.date)
        df = pd.read_sql(query.statement, self.session.bind)
        
        if df.empty:
            print("❌ Datos insuficientes para simular.")
            return

        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        
        mu = df['log_ret'].mean()
        sigma = df['log_ret'].std()
        last_price = df['close'].iloc[-1]

        print(f"📊 Estadísticas: Último Precio=${last_price:.2f}, Mu={mu:.6f}, Sigma={sigma:.6f}")

        random_shocks = np.random.normal(loc=mu, scale=sigma, size=(days_ahead, simulations))
        
        simulation_paths = np.zeros((days_ahead + 1, simulations))
        simulation_paths[0] = last_price
        
        prices = last_price * np.exp(np.cumsum(random_shocks, axis=0))
        
        final_prices = prices[-1]
        
        final_prices_sorted = np.sort(final_prices)
        
        percentile_5 = np.percentile(final_prices_sorted, 5)
        var_95 = last_price - percentile_5
        
        percentile_1 = np.percentile(final_prices_sorted, 1)
        var_99 = last_price - percentile_1

        es_95 = last_price - final_prices_sorted[final_prices_sorted <= percentile_5].mean()

        print(f"📉 Resultados de Riesgo (a {days_ahead} días):")
        print(f"   VaR 95%: ${var_95:.2f}")
        print(f"   VaR 99%: ${var_99:.2f}")
        print(f"   ES 95%:  ${es_95:.2f}")

        new_sim = SimulationResult(
            asset_id=asset.id,
            run_date=datetime.utcnow(),
            var_95=float(var_95),
            var_99=float(var_99),
            expected_shortfall=float(es_95)
        )
        self.session.add(new_sim)
        self.session.commit()
        print("✅ Resultados guardados en la base de datos.")

if __name__ == "__main__":
    db = SessionLocal()
    sim = MonteCarloEngine(db)
    
    sim.run_simulation("AAPL", simulations=1000)
    
    db.close()