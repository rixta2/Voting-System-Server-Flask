from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from src.db.models import Faction
from src.db import get_db, SessionLocal, Session
from src.utils.constants import FACTIONS
import logging
from src.service.ws.score_ws import broadcast_to_room

router = APIRouter()

@router.get("/{faction}")
async def get_faction_score(faction, db: Session = Depends(get_db)):
    if faction in FACTIONS:
        db_val:Faction = db.query(Faction).filter_by(name=faction).first() 
        
        if not db_val:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(content={"Error finding faction."}, status_code=500)

        else: return ({"score": db_val.score})
    else: return Response(content={"Faction not found"}, status_code=404)

@router.get("/increment/{faction}")
async def increment_faction_score(faction, db: Session = Depends(get_db)):
    if faction in FACTIONS:
        db_val:Faction = db.query(Faction).filter_by(name=faction).first()
        
        if not db_val:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(status_code=500, content="Error finding faction.")

        db_val.score += 1
        score = db_val.score
        db.commit()
        await broadcast_to_room(faction=faction, message=str(score))
        return "success"
    else: return Response(content="Faction not found", status_code=404)

