from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get('/')
def home():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")

    return {
        "message": "hello people",
        "app-name" : app_name,
        "app-version" : app_version
    }