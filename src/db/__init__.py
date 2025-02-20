import os
import sys
import logging
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database

if __debug__: 
    load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))
    # Load additional environment variables from dev/docker/.env if not already set
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../dev/docker/.env"), override=False)

Base = declarative_base()

class Env:
    """Load required database environment variables"""
    def __init__(self):
        required_vars = ["DATABASE_PREFIX", "DATABASE_HOSTNAME", "DB_USERNAME", "DB_PASSWORD", "DB_DATABASE"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]

        if missing_vars:
            logging.critical(f"Missing environment variables: {', '.join(missing_vars)}")
            sys.exit(1)

        self.DATABASE_PREFIX = os.getenv("DATABASE_PREFIX")
        self.DATABASE_HOSTNAME = os.getenv("DATABASE_HOSTNAME")
        self.DB_USERNAME = os.getenv("DB_USERNAME")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_DATABASE = os.getenv("DB_DATABASE")

    def get_db_url(self):
        """Generate a safe SQLAlchemy database URL"""
        return f"{self.DATABASE_PREFIX}://{self.DB_USERNAME}:{urllib.parse.quote_plus(self.DB_PASSWORD)}@{self.DATABASE_HOSTNAME}/{self.DB_DATABASE}"

db_vars = Env()
DATABASE_URL = db_vars.get_db_url()
engine = create_engine(DATABASE_URL, echo=True)

if not database_exists(engine.url):
    create_database(engine.url)
    logging.info(f"✅ Database created: {engine.url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """FastAPI Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables & insert initial data"""
    from .models import Faction, insert_initial_factions 

    Base.metadata.create_all(bind=engine)
    logging.info("Tables created successfully")

    insert_initial_factions()
