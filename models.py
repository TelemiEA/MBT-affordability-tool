"""
Database models for the affordability benchmarking tool.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Scenario(Base):
    """Model for affordability scenarios."""
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, unique=True, index=True)
    scenario_type = Column(String)  # 'vanilla' or 'self_employed'
    applicant_type = Column(String)  # 'single' or 'joint'
    applicant1_income = Column(Integer)
    applicant2_income = Column(Integer, nullable=True)
    applicant1_employment = Column(String)  # 'employed' or 'self_employed'
    applicant2_employment = Column(String, nullable=True)
    age = Column(Integer, default=30)
    term = Column(Integer, default=35)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AffordabilityResult(Base):
    """Model for affordability results from lenders."""
    __tablename__ = "affordability_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, index=True)
    lender_name = Column(String)
    max_borrowing = Column(Float)
    run_date = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, index=True)  # Groups results from the same run
    created_at = Column(DateTime, default=datetime.utcnow)


class RunSummary(Base):
    """Model for summarizing each complete run."""
    __tablename__ = "run_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    scenario_id = Column(String)
    total_lenders = Column(Integer)
    successful_extractions = Column(Integer)
    average_borrowing = Column(Float)
    gen_h_amount = Column(Float)
    gen_h_difference = Column(Float)
    gen_h_rank = Column(Integer)
    run_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")  # 'running', 'completed', 'failed'


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./affordability.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()