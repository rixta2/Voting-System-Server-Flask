from sqlalchemy.orm import Session
from src.db.models.faction_model import Faction
from src.utils.constants import FACTIONS_ARR
import asyncio
import logging

class Factions_Handler:
    _cache = {}
    _lock = asyncio.Lock()
    _initialised = False

    @classmethod
    async def initialise_cache(cls, db: Session):
        async with cls._lock:
            if not cls._initialised:
                cls._cache = {
                    f.name: f.score for f in db.query(Faction).all()
                }
                cls._initialised = True

    @classmethod
    def get_score(cls, name: str) -> int:
        return cls._cache.get(name)

    @classmethod
    async def increment_score(cls, db: Session, name: str) -> bool:
        if name in FACTIONS_ARR:
            async with cls._lock:
                db_val = db.query(Faction).filter_by(name=name).first()
                if db_val:
                    db_val.score += 1
                    db.commit()
                    cls._cache[name] = db_val.score
                    return True
        return False
