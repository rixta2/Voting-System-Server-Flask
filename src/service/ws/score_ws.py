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

async def keep_alive(websocket: WebSocket, interval: int = 20):
    try:
        while True:
            await asyncio.sleep(interval)
            await websocket.send_text("__ping__")
    except Exception:
        pass  # Let the outer handler catch and handle disconnect

@router.websocket("/{faction}")
async def websocket_broadcast(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    fh = Factions_Handler(db)
    await fh.initialise_cache()

    if faction in __faction_rooms: 
        await websocket.accept()
        __faction_rooms[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")
        await websocket.send_text(str(fh.get_cache().get(faction)))

        ping_task = asyncio.create_task(keep_alive(websocket))

        try:
            while True:
                data = await websocket.receive_text()
                if data == "get_score":
                    score = fh.get_cache().get(faction)
                    await websocket.send_text(str(score))
        except WebSocketDisconnect:
            logging.info(f"WebSocket connection closed for faction: {faction}")
        finally:
            ping_task.cancel()
            __faction_rooms[faction].remove(websocket)
    else: 
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")

@router.websocket("/{faction}/timed")
async def websocket_timed(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    fh = Factions_Handler(db)
    await fh.initialise_cache()

    if faction in __faction_rooms_timed: 
        await websocket.accept()
        __faction_rooms_timed[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")
        await websocket.send_text(str(fh.get_cache().get(faction)))

        ping_task = asyncio.create_task(keep_alive(websocket))

        try:
            while True:
                await asyncio.sleep(5) 
                score = fh.get_cache().get(faction)
                await websocket.send_text(str(score))
        except WebSocketDisconnect:
            logging.info(f"WebSocket connection closed for faction: {faction}")
        except Exception as e:
            logging.error(f"Error in updates: {e}")
        finally:
            ping_task.cancel()
            __faction_rooms_timed[faction].remove(websocket)
    else: 
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")
