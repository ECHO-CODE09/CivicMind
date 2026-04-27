from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:7823@localhost:5432/civicmind")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Debate(Base):
    __tablename__ = "debates"
    id              = Column(Integer, primary_key=True, index=True)
    question        = Column(Text, nullable=False)
    advocate_arg    = Column(Text)
    challenger_arg  = Column(Text)
    arbitrator_arg  = Column(Text)
    for_score       = Column(Float, default=0)
    against_score   = Column(Float, default=0)
    neutral_score   = Column(Float, default=0)
    final_verdict   = Column(Text)
    bias_flags      = Column(JSON, default=[])
    created_at      = Column(DateTime, default=datetime.utcnow)


class BiasFlag(Base):
    __tablename__ = "bias_flags"
    id          = Column(Integer, primary_key=True, index=True)
    debate_id   = Column(Integer, nullable=False)
    bias_type   = Column(String(100))
    severity    = Column(String(20))
    description = Column(Text)
    created_at  = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready.")
