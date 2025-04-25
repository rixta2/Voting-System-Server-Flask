from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, Request, Response
from src.utils.constants import FACTIONS
from src.utils.constants import FACTIONS_ARR
import logging
from typing import Dict, List
from src.db.handlers.factions_handler import Factions_Handler
from src.db import get_db, Session
import asyncio 

__faction_rooms: Dict[str, List[WebSocket]] = {faction: [] for faction in FACTIONS}
__faction_rooms_timed: Dict[str, List[WebSocket]] = {faction: [] for faction in FACTIONS}
router = APIRouter()

@router.websocket("/{faction}")
async def websocket_broadcast(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    fh = Factions_Handler(db)
    await fh.initialise_cache()
    
    if faction in __faction_rooms: 
        await websocket.accept()
        __faction_rooms[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")
        await websocket.send_text(str(fh.get_cache().get(faction)))
        
        try: 
            while True:
                data = await websocket.receive_text()
                logging.info(f"Received message: {data}")
                if data == "get_score":
                    if faction in FACTIONS_ARR:
                        logging.info(f"Sending score: {fh.get_cache().get(faction)}")
                        await websocket.send_text(str(fh.get_cache().get(faction)))
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
            await connection.send_text(str(message))

@router.websocket("/{faction}/timed")
async def websocket_timed(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    fh = Factions_Handler(db)
    await fh.initialise_cache()

    if faction in __faction_rooms_timed: 
        await websocket.accept()
        __faction_rooms_timed[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")
        await websocket.send_text(str(fh.get_cache().get(faction)))
        try:
            while True:
                await asyncio.sleep(5) 
                score = fh.get_cache().get(faction)
                logging.info(f"Sending timed update: {score}")
                await websocket.send_text(str(fh.get_cache().get(faction)))
        except WebSocketDisconnect:
            __faction_rooms_timed[faction].remove(websocket)
            logging.info(f"WebSocket connection closed for faction: {faction}")
        except Exception as e:
            logging.error(f"Error in updates: {e}")
    else: 
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")