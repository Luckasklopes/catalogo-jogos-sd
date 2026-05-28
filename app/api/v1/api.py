from fastapi import APIRouter
from app.api.v1.endpoints import games

api_router = APIRouter()
api_router.include_router(games.router, prefix="/catalog/games", tags=["games"])
