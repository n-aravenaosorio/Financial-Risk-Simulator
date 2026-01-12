import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from src.database import SessionLocal, Asset, MarketData 

class DataIngestion:
    def __init__(self, db_session: Session):
        self.session = db_session

    def get_stock_data(self, ticker: str, start_date: str = "2018-01-01"):
        print(f"\n📥 Descargando datos para {ticker} desde {start_date}...")
        try:
            data = yf.download(ticker, start=start_date, progress=False)
            
            if data.empty:
                print(f"⚠️ No se encontraron datos para {ticker}")
                return None
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data.reset_index(inplace=True)
            
            data.columns = [c.capitalize() for c in data.columns]
            
            return data
            
        except Exception as e:
            print(f"❌ Error descargando {ticker}: {e}")
            return None

    def save_market_data(self, ticker: str, data: pd.DataFrame):
        try:
            asset = self.session.query(Asset).filter_by(symbol=ticker).first()
            
            if not asset:
                print(f"🆕 Registrando nuevo activo: {ticker}")
                asset = Asset(symbol=ticker)
                self.session.add(asset)
                self.session.commit()
                self.session.refresh(asset) 
            else:
                print(f"ℹ️ El activo {ticker} ya existe (ID: {asset.id}). Actualizando precios...")

            self.session.query(MarketData).filter_by(asset_id=asset.id).delete()
            
            print(f"💾 Guardando {len(data)} registros en DB...")
            
            records = []
            for _, row in data.iterrows():
                record = MarketData(
                    asset_id=asset.id,
                    date=row['Date'].to_pydatetime(),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                records.append(record)

            self.session.add_all(records)
            self.session.commit()
            print(f"✅ ¡Éxito! Datos de {ticker} guardados correctamente.")

        except Exception as e:
            print(f"❌ Error guardando en DB: {e}")
            self.session.rollback()

if __name__ == "__main__":
    db = SessionLocal()
    etl = DataIngestion(db)
    
    tickers_to_test = ["AAPL", "TSLA"]
    
    for symbol in tickers_to_test:
        raw_data = etl.get_stock_data(symbol)
        if raw_data is not None:
            etl.save_market_data(symbol, raw_data)
            
    db.close()