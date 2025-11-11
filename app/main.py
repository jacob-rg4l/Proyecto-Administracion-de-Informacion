
from fastapi import FastAPI
from app.rutas import api

app = FastAPI()
app.include_router(api)
