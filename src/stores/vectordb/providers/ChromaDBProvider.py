from ..VectorDBInterface import VectorDBInterface
from stores.vectordb.VectorDBEnums import DistanceMethodEnums
from chromadb import PersistentClient
from models.db_schemes.data_chunk import RetrievedDocument
import logging
from typing import List
import uuid

class ChromaDBProvider(VectorDBInterface):

     def __init__(self, db_client: str, default_vector_size: int=786, 
                     distance_method : str = None, index_threshold: int=100):

        self.client = None
        self.db_client = db_client
        self.distance_method = distance_method
        self.default_vector_size = default_vector_size

        self.logger = logging.getLogger("uvicorn")


        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = DistanceMethodEnums.COSINE.value

        if distance_method == DistanceMethodEnums.IP.value:
            self.distance_method = DistanceMethodEnums.IP.value

     def connect(self):
        self.client = PersistentClient(path=self.db_client)

     def disconnect(self):
        self.client = None

     def is_collection_existed(self, collection_name: str) -> bool:

        try:
            self.client.get_collection(name=collection_name)
            return True
        except Exception as e:
            self.logger.error(f"The collection name does not exist in Chromadb {e}")
            return False

     def list_all_collections(self) -> List:
         return self.client.list_collections()

    
     def get_collection_info(self, collection_name: str) -> dict:

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error("The collection name does not exist in Chromadb")
            return False

        collection = self.client.get_collection(name=collection_name)

        return {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata,
        }
    
     def delete_collection(self, collection_name: str) -> bool:

        if self.is_collection_existed(collection_name=collection_name):
            self.logger.info(f"Deleting collection : {collection_name}")
            self.client.delete_collection(name=collection_name)
            return True

        return False

     def create_collection(self, collection_name: str,
                                        embedding_size: int = None,
                                        do_reset: bool = False):

        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):

            self.client.create_collection(
               name=collection_name,
               metadata = {
                   "hnsw:space": self.distance_method
               }
            )

            return True

        return False

     
     def insert_one(self, collection_name: str,
                                    text: str,
                                    vector: list,
                                    metadata: dict = None,
                                    record_id: str = None):
        

        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"Cannot insert record into non-existent collection "
                f"{collection_name}"
            )

            return False

        try:
            collection = self.client.get_collection(name=collection_name)


            collection.add(
                ids =[record_id if record_id is not None else str(hash(text))],
                embeddings=[vector],
                documents=[text],
                metadatas=[metadata if metadata is not None else {}],

            )

            return True

        except Exception as e:

            self.logger.error(
                f"Error while inserting record: {e}"
            )

            return False


     def insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        metadata: list = None,
        record_ids: list = None,
        batch_size: int = 50
    ):

        if not self.is_collection_existed(collection_name):

            self.logger.error(
                f"Cannot insert records into non-existent collection "
                f"{collection_name}"
            )

            return False

        if metadata is None:
            metadata = [{} for _ in texts]

        if record_ids is None:
            record_ids = [
                str(uuid.uuid4())
                for _ in texts
            ]

        try:

            collection = self.client.get_collection(
                name=collection_name
            )

            for i in range(0, len(texts), batch_size):

                batch_texts = texts[i : i + batch_size]
                batch_vectors = vectors[i : i + batch_size]
                batch_metadata = metadata[i : i + batch_size]
                batch_ids = record_ids[i : i + batch_size]

                collection.add(
                    ids=batch_ids,
                    embeddings=batch_vectors,
                    documents=batch_texts,
                    metadatas=batch_metadata
                )

            return True

        except Exception as e:

            self.logger.error(
                f"Error while inserting batch: {e}"
            )

            return False

     def search_by_vector(self, collection_name: str,
                                      vector: list,
                                      limit: int = 5) -> List[RetrievedDocument]:

        collection = self.client.get_collection(
            name=collection_name
        )

        results = collection.query(
            query_embeddings=[vector],
            n_results=limit
        )

        if not results or not results["documents"]:
            return None

        documents = results["documents"][0]
        distances = results["distances"][0]

        return [
            RetrievedDocument(**{
                "score": 1 - distance,
                "text": document
            })
            for document, distance in zip(documents, distances)
        ]