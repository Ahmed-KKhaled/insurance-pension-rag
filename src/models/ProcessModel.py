from .BaseDataModel import BaseDataModel
from models import DataChunk
from models import DataBaseEnum
from bson.objectid import ObjectId

class ProcessModel(BaseDataModel):

    def __init__(self, db_client : object):
        super().__init__(db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):

        result = await self.collection.insert_one(chunk.dict())
        chunk._id = result.inserted_id

        return chunk

    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({
            "_id" : ObjectId(chunk_id)
        })

        if result is None:
           return None

        return DataChunk(**result)

    

    