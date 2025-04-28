from functools import wraps
from fastapi import Request, HTTPException, Depends
from dotenv import load_dotenv
import os

if __debug__: 
    load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))

API_KEY = os.getenv("API_KEY", "default_secret")  

async def require_api_key(request: Request):
    """FastAPI dependency that validates API keys from the Authorization header"""
    api_key = request.headers.get("Authorization")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
