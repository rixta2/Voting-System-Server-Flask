from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2  # Required for direct PostgreSQL connections
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import Flask
import sys
from dotenv import load_dotenv
import urllib.parse
import logging


db = SQLAlchemy()

if __debug__: 
    load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))

class Env:
    def __init__(self):
        required_vars = ["DATABASE_PREFIX", "DATABASE_HOSTNAME", "DB_USERNAME", "DB_PASSWORD", "DB_DATABASE"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]

        if missing_vars:
            logging.critical(f"Missing environment variables: {', '.join(missing_vars)}")
            sys.exit(1)
        
        self.DATABASE_PREFIX= os.getenv("DATABASE_PREFIX", None) 
        self.DATABASE_HOSTNAME= os.getenv("DATABASE_HOSTNAME", None)
        self.DB_USERNAME= os.getenv("DB_USERNAME", None)
        self.DB_PASSWORD= os.getenv("DB_PASSWORD", None)
        self.DB_DATABASE= os.getenv("DB_DATABASE", None)

def ensure_postgres_db(db_url:str):
    engine = create_engine(db_url, echo=True)

    if not database_exists(engine.url):
        create_database(engine.url)
        logging.info(f"✅ Database created: {engine.url}")

def init_db(app:Flask):
    db_vars = Env()
    # db_url = f"{db_vars.DATABASE_PREFIX}://{db_vars.DB_USERNAME}:{db_vars.DB_PASSWORD}@{db_vars.DATABASE_HOSTNAME}/{db_vars.DB_DATABASE}"
    db_url = f"{db_vars.DATABASE_PREFIX}://{db_vars.DB_USERNAME}:{urllib.parse.quote_plus(db_vars.DB_PASSWORD)}@{db_vars.DATABASE_HOSTNAME}/{db_vars.DB_DATABASE}"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    ensure_postgres_db(db_url)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        logging.info("Tables created successfully")
        
