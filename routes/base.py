from fastapi import FastAPI, APIRouter


base_router = APIRouter()

@base_router.get('/')
def home():
    return {
        "message": "hello people"
    }