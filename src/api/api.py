from src import app
from src.api.rest.score_api import score_blueprint


def init_api():
    app.register_blueprint(score_blueprint)
    
    