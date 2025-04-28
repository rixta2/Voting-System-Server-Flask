from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, Request, Response
from src.utils.constants import FACTIONS
from src.utils.constants import FACTIONS_ARR
import logging
from typing import Dict, Set
from src.db.handlers.factions_handler import Factions_Handler
from src.db import get_db, Session
import asyncio

# Use Set instead of List
__faction_rooms: Dict[str, Set[WebSocket]] = {faction: set() for faction in FACTIONS}
__faction_rooms_timed: Dict[str, Set[WebSocket]] = {faction: set() for faction in FACTIONS}

router = APIRouter()

@router.websocket("/{faction}")
async def websocket_broadcast(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    if faction in __faction_rooms:
        await websocket.accept()
        __faction_rooms[faction].add(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")

        fh = Factions_Handler(db)
        score = fh.get_value(faction)
        await websocket.send_text(str(score))

        try:
            while True:
                data = await websocket.receive_text()
                logging.info(f"Received message: {data}")
                if data == "get_score":
                    if faction in FACTIONS_ARR:
                        score = fh.get_value(faction)
                        logging.info(f"Sending score: {score}")
                        await websocket.send_text(str(score))
                    else:
                        logging.error("Faction not found in database")
                        await websocket.send_text("Faction not found")
        except WebSocketDisconnect:
            logging.info(f"WebSocket connection closed for faction: {faction}")
        finally:
            __faction_rooms[faction].discard(websocket)
    else:
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")

@router.websocket("/{faction}/timed")
async def websocket_timed(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    if faction in __faction_rooms_timed:
        await websocket.accept()
        __faction_rooms_timed[faction].add(websocket)
        logging.info(f"WebSocket connection accepted for timed faction: {faction}")

        fh = Factions_Handler(db)
        score = fh.get_value(faction)
        await websocket.send_text(str(score))

        try:
            while True:
                await asyncio.sleep(5)
                score = fh.get_value(faction)
                logging.info(f"Sending timed update: {score}")
                await websocket.send_text(str(score))
        except WebSocketDisconnect:
            logging.info(f"WebSocket connection closed for timed faction: {faction}")
        except Exception as e:
            logging.error(f"Error in timed updates: {e}")
        finally:
            __faction_rooms_timed[faction].discard(websocket)
    else:
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")

async def broadcast_to_room(faction: str, message: str):
    if faction not in __faction_rooms:
        logging.warning(f"Tried to broadcast to unknown faction: {faction}")
        return

    connections = set(__faction_rooms[faction])  
    logging.info(f"[Broadcast] {len(connections)} connections found for faction '{faction}'")

    dead_connections = set()

    for connection in connections:
        try:
            await connection.send_text(str(message))
            logging.info(f"[Broadcast] Sent message to connection {id(connection)}")
        except Exception as e:
            logging.error(f"[Broadcast] Failed to send to connection {id(connection)}: {e}")
            dead_connections.add(connection)
            
    for dead in dead_connections:
        __faction_rooms[faction].discard(dead)
        logging.info(f"[Broadcast] Removed dead connection {id(dead)} from faction '{faction}'")

    logging.info(f"[Broadcast] After cleanup: {len(__faction_rooms[faction])} active connections remain.")
