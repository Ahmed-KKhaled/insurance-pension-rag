from .BaseDataModel import BaseDataModel
from models import Chunk
from bson.objectid import ObjectId
from bson.objectid import ObjectId
from sqlalchemy import func, select, delete

class ChunkModel(BaseDataModel):

    def __init__(self, db_client : object):
        super().__init__(db_client)

        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    

    async def insert_chunk(self, chunk: Chunk):

        async with self.db_client() as session:
                    async with session.begin():
                        session.add(chunk)
        
                    await session.refresh(chunk)
        
        return chunk

    async def get_chunk(self, chunk_id: int):
        async with self.db_client() as session:
               result = await session.execute(
                             select(Chunk).where(
                                 Chunk.chunk_id == chunk_id
                             )
                         )

               chunk = result.scalar_one_or_none()

        return chunk

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        async with self.db_client() as session:
             async with session.begin():
                  for i in range(0, len(chunks), batch_size):
                       batch = chunks[i : batch_size + i]
                       session.add_all(batch)
             

        return len(chunks)
    

    async def delete_chunks_by_project_id(self, project_id: int):
            
            async with self.db_client() as session:
              dele = delete(Chunk).where(Chunk.chunk_project_id == project_id)
              result = await session.execute(dele)

              await session.commit()

            return result.rowcount

    async def get_chunks_by_project_id(self, project_id: int,
                                             page_no: int=1,
                                             page_size: int=50):

         async with self.db_client() as session:
              stmt = select(Chunk).where(Chunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
              result = await session.execute(stmt)
              records = result.scalars().all()

         return records

    async def get_total_chunk_count(self, project_id: int):
         async with self.db_client() as session:
              count_sql = select(
                    func.count(Chunk.chunk_id)
                    ).where(
                    Chunk.chunk_project_id == project_id
               )

              records_count = await session.execute(count_sql)

              return records_count.scalar_one()


    

    

    

    

    