from sqlalchemy.orm import Session
from src.db.models.faction_model import Faction
from src.utils.constants import FACTIONS_ARR
import asyncio
import logging

class Factions_Handler:
    _cache: dict[str, int] = {}
    _initialised = False
    _lock = asyncio.Lock()

    def __init__(self, db: Session):
        self.db = db

    async def initialise_cache(self):
        """One-time cache load"""
        async with Factions_Handler._lock:
            if not Factions_Handler._initialised:
                logging.info("Initialising faction score cache...")
                Factions_Handler._cache = {
                    faction.name: faction.score
                    for faction in self.db.query(Faction).all()
                }
                Factions_Handler._initialised = True

    def get_cache(self):
        return self._cache

    async def increment_faction_value(self, faction_name: str) -> bool:
        if faction_name in FACTIONS_ARR:
            async with Factions_Handler._lock:
                db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
                if db_val:
                    db_val.score += 1
                    self.db.commit()
                    Factions_Handler._cache[faction_name] = db_val.score
                    return True
        logging.error("Factions_Handler | increment_faction_value | Invalid faction.")
        return False

    async def set_score(self, faction_name: str, val: int) -> bool:
        if faction_name in FACTIONS_ARR:
            async with Factions_Handler._lock:
                db_val: Faction = self.db.query(Faction).filter_by(name=faction_name).first()
                if db_val:
                    db_val.score = val
                    self.db.commit()
                    Factions_Handler._cache[faction_name] = db_val.score
                    return True
        logging.error("Factions_Handler | set_score | Invalid faction.")
        return False
