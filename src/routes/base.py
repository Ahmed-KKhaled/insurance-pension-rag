from fastapi import FastAPI, APIRouter
import os
from helpers.config import get_settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get('/')
async def home():
    app_settings = get_settings()

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "message": "hello people",
        "app-name" : app_name,
        "app-version" : app_version
    }