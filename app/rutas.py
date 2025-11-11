
from fastapi import APIRouter

api = APIRouter()

@api.get("/")
def inicio():
    return {"mensaje": "Bienvenido a StockTrack"}
