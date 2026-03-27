from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()

class Case(Base):
    __tablename__ = "cases"
    id          = Column(Integer, primary_key=True)
    case_id     = Column(String(20), unique=True)
    title       = Column(String(200))
    description = Column(Text)
    severity    = Column(String(10))
    status      = Column(String(20), default="open")
    assigned_to = Column(String(100), nullable=True)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.datetime.utcnow)
    source      = Column(String(50))
    tags        = Column(JSON, default=list)

class Artifact(Base):
    __tablename__ = "artifacts"
    id            = Column(Integer, primary_key=True)
    case_id       = Column(String(20))
    name          = Column(String(200))
    artifact_type = Column(String(30))
    file_path     = Column(String(500), nullable=True)
    content       = Column(Text, nullable=True)
    collected_at  = Column(DateTime, default=datetime.datetime.utcnow)
    source        = Column(String(100))
    md5           = Column(String(32), nullable=True)
    sha256        = Column(String(64), nullable=True)
    metadata_     = Column(JSON, default=dict)

class Finding(Base):
    __tablename__ = "findings"
    id           = Column(Integer, primary_key=True)
    case_id      = Column(String(20))
    artifact_id  = Column(Integer, nullable=True)
    finding_type = Column(String(50))
    title        = Column(String(200))
    description  = Column(Text)
    severity     = Column(String(10))
    timestamp    = Column(DateTime)
    data         = Column(JSON, default=dict)

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id          = Column(Integer, primary_key=True)
    case_id     = Column(String(20))
    event_time  = Column(DateTime)
    category    = Column(String(30))
    title       = Column(String(200))
    description = Column(Text)
    source      = Column(String(100))
    artifact_id = Column(Integer, nullable=True)

engine = create_engine("sqlite:///dfir.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
