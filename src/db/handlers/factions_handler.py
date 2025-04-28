from sqlalchemy.orm import Session
from src.db.models.faction_model import Faction
from src.utils.constants import FACTIONS_ARR
import logging

class Factions_Handler:
    def __init__(self, db: Session):
        self.db = db

    def get_value(self, faction_name: str) -> int | None:
        if faction_name in FACTIONS_ARR:
            db_val = self.db.query(Faction).filter_by(name=faction_name).first()
            if db_val:
                return db_val.score
        logging.error(f"Factions_Handler | get_value | Faction '{faction_name}' not found.")
        return None

    def increment_faction_value(self, faction_name: str) -> int:
        if faction_name in FACTIONS_ARR:
            db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
            if db_val:
                db_val.score += 1
                self.db.commit()
                return db_val.score
        logging.error("Factions_Handler | increment_faction_value | Invalid faction.")
        return -1

    def decrement_faction_value(self, faction_name: str) -> bool:
        if faction_name in FACTIONS_ARR:
            db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
            if db_val:
                db_val.score = db_val.score - 1
                self.db.commit()
                return db_val.score
        logging.error("Factions_Handler | increment_faction_value | Invalid faction.")
        return -1

    def set_score(self, faction_name: str, val: int) -> bool:
        if faction_name in FACTIONS_ARR:
            db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
            if db_val:
                db_val.score = val
                self.db.commit()
                return True
        logging.error("Factions_Handler | set_score | Invalid faction.")
        return False
