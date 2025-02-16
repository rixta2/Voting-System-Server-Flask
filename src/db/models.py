from sqlalchemy import String, Column, Integer
from .database import db
import logging

class factions(db.Model):
    name = Column(String(80), primary_key=True)
    score = Column(Integer)
    
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

def insert_initial_factions():
    if factions.query.count() == 0:
        initial_factions = [
            factions(name="Overgrowth", score=0),
            factions(name="Artificers", score=0),
            factions(name="Rebel", score=0),
            factions(name="Nocturne", score=0)
        ]
        db.session.bulk_save_objects(initial_factions)
        db.session.commit()
        logging.info("Initial factions data inserted successfully")