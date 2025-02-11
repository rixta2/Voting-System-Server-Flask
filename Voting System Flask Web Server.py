import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass@localhost/questival'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypass@localhost/questival_db'
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/get_score', methods=['GET'])
def get_score():
    name = request.args.get('name')
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
    
    return jsonify({'message': 'Score updated successfully'})

# **NEW ENDPOINT** to increment score
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

    return jsonify({'message': f'Score incremented for {name}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
