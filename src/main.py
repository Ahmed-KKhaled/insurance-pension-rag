from fastapi import FastAPI
from helpers import get_settings
from routes import base_router, data_router, nlp_router
from motor.motor_asyncio import AsyncIOMotorClient
from helpers import get_settings
from stores import LLMProviderFactory, VectorDBProviderFactory
from stores.llm.templates import TemplateParser

app = FastAPI()

@app.on_event("startup")
async def startup_span():
    settings = get_settings()

    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings)

    # Generation client
    app.generation_client = llm_provider_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    app.generation_client.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID
    )

    # Embedding client
    app.embedding_client = llm_provider_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE
    )

    # VectorDB client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    # template parser
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    )




@app.on_event("shutdown")
async def shutdown_span():
    app.mongo_conn.close()
    app.vectordb_client.disconnect()

app.include_router(base_router)
app.include_router(data_router)
app.include_router(nlp_router)



