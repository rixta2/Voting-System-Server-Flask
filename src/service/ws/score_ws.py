from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from src.utils.constants import FACTIONS
import logging
from typing import Dict, List


__faction_rooms: Dict[str, List[WebSocket]] = {faction: [] for faction in FACTIONS}


router = APIRouter()

@router.websocket("/{faction}")
async def websocket_endpoint(websocket: WebSocket, faction: str):
    """Handles WebSocket connections for different factions (rooms)"""
    if faction in __faction_rooms: 
        await websocket.accept()
        __faction_rooms[faction].append(websocket)
        
        try: 
            while True:
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            __faction_rooms[faction].remove(websocket)
    else: 
        websocket.close(reason="Incorrect faction.")
        logging.info(f"Connection rejected with incorrect faction: {faction}")

async def broadcast_to_room(faction: str, message: str):
    """Sends a message to all connected clients in a specific room"""
    if faction in __faction_rooms:
        for connection in __faction_rooms[faction]:
            await connection.send_text(message)
            
