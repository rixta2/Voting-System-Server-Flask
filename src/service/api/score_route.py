from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from src.db import get_db, Session
from src.utils.constants import FACTIONS
import logging
from src.service.ws.score_ws import broadcast_to_room
from src.utils.authentication import require_api_key
from src.db.handlers.factions_handler import Factions_Handler

router = APIRouter()

@router.get("/{faction}")
async def get_faction_score(faction: str, db: Session = Depends(get_db), auth = Depends(require_api_key)):
    if faction in [f.value for f in FACTIONS]:
        fh = Factions_Handler(db)
        score = fh.get_value(faction)
        if score is not None:
            return {"score": score}
        else:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(content="Server Error.", status_code=500)
    else:
        return Response(content="Faction not found", status_code=404)

@router.get("/increment/{faction}")
async def increment_faction_score(faction: str, db: Session = Depends(get_db), auth = Depends(require_api_key)):
    if faction in [f.value for f in FACTIONS]:
        fh = Factions_Handler(db)
        success = fh.increment_faction_value(faction)
        if success:
            score = fh.get_value(faction)
            await broadcast_to_room(faction, score)
            return {"score": score}
        else:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(content="Server Error.", status_code=500)
    else:
        return Response(content="Faction not found", status_code=404)

@router.get("/decrement/{faction}")
async def increment_faction_score(faction: str, db: Session = Depends(get_db), auth = Depends(require_api_key)):
    if faction in [f.value for f in FACTIONS]:
        fh = Factions_Handler(db)
        success = fh.decrement_faction_value(faction)
        if success:
            score = fh.get_value(faction)
            await broadcast_to_room(faction, score)
            return {"score": score}
        else:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(content="Server Error.", status_code=500)
    else:
        return Response(content="Faction not found", status_code=404)

@router.post("/setScore/{faction}")
async def set_faction_score(faction: str, request: Request, db: Session = Depends(get_db), auth = Depends(require_api_key)):
    if faction in [f.value for f in FACTIONS]:
        data = await request.json()
        score = data.get('score')

        if not isinstance(score, int):
            return JSONResponse(content={"error": "Invalid input"}, status_code=400)

        fh = Factions_Handler(db)
        success = fh.set_score(faction, score)
        if success:
            await broadcast_to_room(faction=faction, message=score)
            return JSONResponse(content={
                "message": "Score set successfully",
                "name": faction,
                "new_score": fh.get_value(faction)
            })
        else:
            logging.error("Faction not found in db post preliminary validation.")
            return Response(status_code=500, content="Error finding faction.")
    else:
        return Response(content="Faction not found", status_code=404)
