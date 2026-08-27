from fastapi import FastAPI, APIRouter


base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)

@base_router.get('/')
def home():
    return {
        "message": "hello people"
    }