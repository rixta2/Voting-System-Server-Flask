from fastapi import FastAPI
from .ws.score_ws import router as score_ws_router
from .api.score_route import router as score_api_router


def register_routes(app: FastAPI):
    app.include_router(score_ws_router, prefix="/score_ws")
    app.include_router(score_api_router, prefix="/score")