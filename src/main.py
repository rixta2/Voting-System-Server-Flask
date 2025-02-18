from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import logging
import uvicorn
from .service import register_routes
from .db import init_db



app = FastAPI()
init_db()
register_routes(app)


if __name__ == '__main__':
    if __debug__: 
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    uvicorn.run("src.main:app", host="0.0.0.0", port=7373, reload=True)