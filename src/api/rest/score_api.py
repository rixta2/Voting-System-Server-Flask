from flask import Blueprint, request, jsonify
from src import socketio

score_blueprint = Blueprint('score', __name__, url_prefix="/score")

@score_blueprint.route('/getScore', methods=['GET'])
def get_score():
    print("get_score")
    return "ok"

@score_blueprint.route('/update_score', methods=['POST'])
def update_score():
    socketio.emit()
    print("update_score")
