from sqlalchemy import String, Column, Integer
from . import Base, SessionLocal
import logging
from src.utils.constants import FACTIONS

class Faction(Base):
    __tablename__ = "factions"
    name = Column(String(80), primary_key=True)
    score = Column(Integer)
    
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

def insert_initial_factions():
    db = SessionLocal()
    
    if db.query(Faction).count() == 0:
        initial_factions = []
        for faction in FACTIONS:
            initial_factions.append(Faction(name=faction, score=0))
            
        db.add_all(initial_factions)
        db.commit()
        logging.info("Initial factions data inserted successfully")
        
        
            #     factions(name="Overgrowth", score=0),
            #     factions(name="Artificers", score=0),
            #     factions(name="Rebel", score=0),
            #     factions(name="Nocturne", score=0)
            # ]