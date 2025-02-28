from src.utils.constants import FACTIONS_ARR
from ..models.faction_model import Faction
from src.db import Session
import logging

class Factions_Handler(): 
    _cache = {}
    def __init__(self, db: Session):
        self.db = db
        Factions_Handler._cache = {faction.name: faction.score for faction in self.db.query(Faction).all()}
    
    def get_cache(self): 
        return self._cache 
    
    def increment_faction_value(self, faction_name:str) -> bool: 
        if faction_name in FACTIONS_ARR:
            db_val:Faction = self.db.query(Faction).filter_by(name=faction_name).first() 
            db_val.score += 1
            Factions_Handler._cache[faction_name] = db_val.score
            self.db.commit()
            return True
        else: 
            logging.error("Factions_Handler | increment_faction_value | Incorrect faction provided.")
            return False
    
    def set_score(self, faction_name:str, val:int) -> bool:
        if faction_name in FACTIONS_ARR:
            db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
            db_val.score = val
            Factions_Handler._cache[faction_name] = db_val.score
            self.db.commit()
            return True
        else: 
            logging.error("Factions_Handler | increment_faction_value | Incorrect faction provided.")
            return False