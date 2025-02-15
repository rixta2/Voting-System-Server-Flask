from src.api.rest.score_api import score_blueprint
from src.api.ws.score_ws import init_score_ws


def init_api(app, socketio):
    #all blueprints go here 
    app.register_blueprint(score_blueprint)

    
    
    #init the ws
    init_score_ws(socketio)

    
    
    