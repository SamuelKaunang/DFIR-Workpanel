from sqlalchemy import (create_engine, Column, Integer,
    String, DateTime, Text, JSON)
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id        = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    service   = Column(String(20))
    src_ip    = Column(String(45))
    src_port  = Column(Integer)
    country   = Column(String(60), nullable=True)
    city      = Column(String(60), nullable=True)
    raw_data  = Column(Text, nullable=True)
    extra     = Column(JSON, nullable=True)

engine = create_engine("sqlite:///honeypot.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)