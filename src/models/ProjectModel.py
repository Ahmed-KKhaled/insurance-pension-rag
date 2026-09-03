from .BaseDataModel import BaseDataModel
from models import Project
from models import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)

        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]


    async def create_project(self, project: Project):

        # mongodb store info in dict format key, value
        result = await self.collection.insert_one(project.dict())
        project._id = result.inserted_id

        return project

    async def get_project_or_create_one(self, project_id: str):

            record = await self.collection.find_one({
                 "project_id" : project_id
            })

            if record is None:
                project = Project(project_id=project_id)
                project = await self.create_project(project=project)

                return project

            return Project(**record)

    async def get_all_projects(self, page_no: int=1, page_size: int=10):

         # count total records
         total_records = await self.collection.count_documents({})


         total_pages = total_records // page_size
         if total_records % page_size > 0:
              total_pages += 1

         cursor = self.collection.find().skip((page_no - 1) * page_size).limit(page_size)

         projects = [Project(**doc) async for doc in cursor]

         return projects, total_pages

    
        
