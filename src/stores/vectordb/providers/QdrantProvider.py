from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from models.db_schemes import RetrievedDocument
import logging
from typing import List

class QdrantProvider(VectorDBInterface):

    def __init__(self, db_path: str,
                      distance_method: str):


        self.client = None

        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE

        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(
            collection_name=collection_name
        )

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        info = self.client.get_collection(
            collection_name=collection_name
        )

        return {
            "status": info.status,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
        }

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False

    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                records=[
                    models.PointStruct(
                        id = record_id,
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    

    def insert_many(self,collection_name: str,
                        texts: list,
                        vectors: list,
                        metadata: list = None,
                        record_ids: list = None,
                        batch_size: int = 50):

        
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(len(texts)))

        for i in range(0, len(texts), batch_size):

            batch_texts = texts[i:i + batch_size]
            batch_vectors = vectors[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            batch_records = record_ids[i:i + batch_size]

            batch_points = [
                models.PointStruct(
                    id=batch_records[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points,
                )

            except Exception as e:
                self.logger.error(
                    f"Error while inserting batch: {e}"
                )
                return False

        return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):

        if vector and isinstance(vector[0], list):
            vector = vector[0]

        responses = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )

        if not responses.points:
            return None

        return [
            RetrievedDocument(**{
                "score": point.score,
                "text": point.payload.get("text") if point.payload else None
            })
            for point in responses.points
        ]

    
    
        

    
        