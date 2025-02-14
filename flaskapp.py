import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

connected_clients = {}

@app.route('/get_score', methods=['POST'])
def get_score():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Name parameter is required'}), 400

    score_entry = db.session.execute(db.text("SELECT score FROM questival WHERE name = :name"), {'name': name}).fetchone()
    if not score_entry:
        return jsonify({'error': 'Name not found'}), 404

    return jsonify({'score': score_entry[0]})

@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.json
    name = data.get('name')
    score = data.get('score')

    if name not in ['Artificers', 'Overgrowth', 'Lost']:
        return jsonify({'error': 'Invalid name'}), 400

    if not isinstance(score, int):
        return jsonify({'error': 'Score must be an integer'}), 400

    result = db.session.execute(db.text("UPDATE questival SET score = :score WHERE name = :name"), {'score': score, 'name': name})
    db.session.commit()

    if result.rowcount == 0:
        return jsonify({'error': 'Name not found'}), 404

    # Notify clients via WebSocket
    socketio.emit('score_update', {'name': name, 'score': score})
    return jsonify({'message': 'Score updated successfully'})

@app.route('/increment_score', methods=['POST'])
def increment_score():
    data = request.json
    name = data.get('name')

    if name not in ['Artificers', 'Overgrowth', 'Lost']:
        return jsonify({'error': 'Invalid name'}), 400

    result = db.session.execute(db.text("UPDATE questival SET score = score + 1 WHERE name = :name"), {'name': name})
    db.session.commit()

    if result.rowcount == 0:
        return jsonify({'error': 'Name not found'}), 404

    # Fetch new score after increment
    score_entry = db.session.execute(db.text("SELECT score FROM questival WHERE name = :name"), {'name': name}).fetchone()
    if score_entry:
        new_score = score_entry[0]
        socketio.emit('score_update', {'name': name, 'score': new_score})

    return jsonify({'message': f'Score incremented for {name}'})

@socketio.on('connect')
def handle_connect():
    print(f"[INFO] Client Connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[INFO] Client Disconnected: {request.sid}")

@socketio.on('message')
def handle_message(data):
    print(f"[INFO] Received WebSocket Message: {data}")
    if isinstance(data, str):
        import json
        data = json.loads(data)

    name = data.get('name')
    if name:
        score_entry = db.session.execute(db.text("SELECT score FROM questival WHERE name = :name"), {'name': name}).fetchone()
        if score_entry:
            emit('score_update', {'name': name, 'score': score_entry[0]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
