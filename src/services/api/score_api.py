from flask import Blueprint, request, jsonify
from src.db.models import Faction
from src.db.database import db  # Add this import

score_blueprint = Blueprint('score', __name__, url_prefix="/score")

@score_blueprint.route('/getScore', methods=['GET'])
def get_score():
    faction_name = request.args.get("name")
    faction = Faction.query.filter_by(name=faction_name).first()
    
    if faction:
        return jsonify({"score": faction.score})
    
    return jsonify({"error": "Faction not found"}), 404

@score_blueprint.route('/updateScore', methods=['POST'])
def update_score():
    data = request.json
    name = data.get('name')
    score = data.get('score')

    if not name or not isinstance(score, int):
        return jsonify({"error": "Invalid input"}), 400

    faction = Faction.query.filter_by(name=name).first()
    if not faction:
        return jsonify({"error": "Faction not found"}), 404 

    faction.score = score
    db.session.commit()

    return jsonify({"message": "Score updated successfully"})

@score_blueprint.route('/incrementScore', methods=['POST'])
def increment_score():
    data = request.json
    name = data.get('name')

    if not name:
        return jsonify({"error": "Missing 'name' parameter"}), 400

    faction = Faction.query.filter_by(name=name.strip()).first()
    if not faction:
        return jsonify({"error": "Faction not found"}), 404 

    faction.score += 1  
    db.session.commit()

    return jsonify({"message": "Score incremented", "name": name, "new_score": faction.score})

@score_blueprint.route('/setScore', methods=['POST'])
def set_score():
    data = request.json
    name = data.get('name')
    score = data.get('score')

    if not name or not isinstance(score, int):
        return jsonify({"error": "Invalid input"}), 400

    faction = Faction.query.filter_by(name=name).first()
    if not faction:
        return jsonify({"error": "Faction not found"}), 404 

    faction.score = score
    db.session.commit()

    return jsonify({"message": "Score set successfully", "name": name, "new_score": faction.score})