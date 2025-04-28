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

# async def keep_alive(websocket: WebSocket, interval: int = 20):
#     try:
#         while True:
#             await asyncio.sleep(interval)
#             await websocket.send_text("__ping__")
#     except Exception:
#         pass  # Let outer handler handle disconnection

@router.websocket("/{faction}")
async def websocket_broadcast(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    if faction in __faction_rooms:
        await websocket.accept()
        __faction_rooms[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")

        fh = Factions_Handler(db)
        score = fh.get_value(faction)
        await websocket.send_text(str(score))

        # ping_task = asyncio.create_task(keep_alive(websocket))

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
            # ping_task.cancel()
            __faction_rooms[faction].remove(websocket)
    else:
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")


async def broadcast_to_room(faction: str, message: str):
    if faction in __faction_rooms:
        for connection in __faction_rooms[faction]:
            try:
                await connection.send_text(message)
            except:
                # Log the error and remove the closed connection
                logging.error(f"WebSocket connection closed")
                __faction_rooms[faction].remove(connection)

@router.websocket("/{faction}/timed")
async def websocket_timed(websocket: WebSocket, faction: str, db: Session = Depends(get_db)):
    if faction in __faction_rooms_timed:
        await websocket.accept()
        __faction_rooms_timed[faction].append(websocket)
        logging.info(f"WebSocket connection accepted for faction: {faction}")

        fh = Factions_Handler(db)
        score = fh.get_value(faction)
        await websocket.send_text(str(score))

        # ping_task = asyncio.create_task(keep_alive(websocket))

        try:
            while True:
                await asyncio.sleep(5)
                score = fh.get_value(faction)
                logging.info(f"Sending timed update: {score}")
                await websocket.send_text(str(score))
        except WebSocketDisconnect:
            logging.info(f"WebSocket connection closed for faction: {faction}")
        except Exception as e:
            logging.error(f"Error in updates: {e}")
        finally:
            # ping_task.cancel()
            __faction_rooms_timed[faction].remove(websocket)
    else:
        await websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")
