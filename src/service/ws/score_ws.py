from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, Request, Response
from src.utils.constants import FACTIONS
from src.db.models import Faction
from src.db import get_db, SessionLocal, Session
import logging
from typing import Dict, List


__faction_rooms: Dict[str, List[WebSocket]] = {faction: [] for faction in FACTIONS}


router = APIRouter()

@router.websocket("/{faction}")
async def websocket_endpoint(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    
    """Handles WebSocket connections for different factions (rooms)"""
    if faction in __faction_rooms: 
        await websocket.accept()
        __faction_rooms[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")
        db_val:Faction = db.query(Faction).filter_by(name=faction).first()
        await websocket.send_text(str(db_val.score))
        
        try: 
            while True:
                data = await websocket.receive_text()
                logging.info(f"Received message: {data}")
                if data == "get_score":
                    db = SessionLocal()
                    db_val: Faction = db.query(Faction).filter_by(name=faction).first()
                    if db_val:
                        logging.info(f"Sending score: {db_val.score}")
                        await websocket.send_text(str(db_val.score))
                    else:
                        logging.error("Faction not found in database")
                        await websocket.send_text("Faction not found")
        except WebSocketDisconnect:
            __faction_rooms[faction].remove(websocket)
            logging.info(f"WebSocket connection closed for faction: {faction}")
    else: 
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")

async def broadcast_to_room(faction: str, message: str):
    """Sends a message to all connected clients in a specific room"""
    if faction in __faction_rooms:
        for connection in __faction_rooms[faction]:
            await connection.send_text(message)

