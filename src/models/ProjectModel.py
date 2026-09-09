from .BaseDataModel import BaseDataModel
from models import Project
from sqlalchemy import func, select

class ProjectModel(BaseDataModel):
    def __init__(self, db_client : object):
        super().__init__(db_client=db_client)

        self.db_client = db_client


    @classmethod
    async def create_instance(cls, db_client: object):
         instance = cls(db_client)
         return instance

    

    async def insert_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)

            await session.refresh(project)

        return project


    async def get_project_or_create_one(self, project_id: str):

        async with self.db_client() as session:
            result = await session.execute(
                select(Project).where(
                    Project.project_id == project_id
                )
            )

            project = result.scalar_one_or_none()

            if project is None:
                project = Project(
                    project_id=project_id
                )

                session.add(project)
                await session.commit()
                await session.refresh(project)

            return project

    async def get_all_projects(self, page_no: int=1, page_size: int=10):

        if page_no < 1:
                 raise ValueError("page must be >= 1")

        if page_size < 1:
                raise ValueError("page_size must be >= 1")

        async with self.db_client() as session:

            # total number of projects
            result = await session.execute(select(
                func.count(Project.project_id) 
            ))

            total_documents = result.scalar_one()

            total_pages = total_documents // page_size
            if total_documents % page_size > 0:
                total_pages += 1

            query = select(Project).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(query)
            projects = result.scalars().all()


            return projects, total_documents

    
        
