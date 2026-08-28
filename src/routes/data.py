from fastapi import FastAPI, APIRouter, Depends, Uploadfile
import os
from helpers.config import get_settings, Settings

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: Uploadfile, 
                      app_settings: Settings = Depends(get_settings)):


    