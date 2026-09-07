from .providers.QdrantProvider import QdrantProvider
from .VectorDBEnums import VectorDBEnums

class VectorDBProviderFactory:
    def __init__(self, config: dict):
        self.config = config



    def create(self, provider: str):

        if provider == VectorDBEnums.QDRANT.value:
            return QdrantProvider(
                db_path=self.config.VECTOR_DB_PATH,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )


        return None
        