from flask_socketio import join_room, leave_room, emit
from flask import request

def init_score_ws(socketio):
    """Function to register WebSocket event handlers"""

    @socketio.on('connect')
    def handle_connect():
        print(f"Client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Client disconnected: {request.sid}")

    @socketio.on('subscribe_faction')
    def subscribe_faction(data):
        faction = data.get('faction')
        if faction:
            join_room(faction)

