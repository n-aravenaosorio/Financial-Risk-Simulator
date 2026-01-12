import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///financial_risk.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    
    market_data = relationship("MarketData", back_populates="asset", cascade="all, delete-orphan")
    simulations = relationship("SimulationResult", back_populates="asset")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)

    asset = relationship("Asset", back_populates="market_data")

class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    run_date = Column(DateTime, default=datetime.utcnow)
    
    var_95 = Column(Float)
    var_99 = Column(Float)
    expected_shortfall = Column(Float) 

    asset = relationship("Asset", back_populates="simulations")

def init_db():
    print("Creando base de datos y tablas...")
    Base.metadata.create_all(bind=engine)
    print("¡Base de datos inicializada con éxito!")

if __name__ == "__main__":
    init_db()