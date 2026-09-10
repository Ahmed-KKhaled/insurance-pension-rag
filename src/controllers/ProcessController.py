from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
import logging
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content : str
    metadata: dict

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        self.logger = logging.getLogger(__name__)


    def get_file_extension(self, file_id: str):
        file_ext = os.path.splitext(file_id)[-1]

        return file_ext

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        elif file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)

        if loader:
         return loader.load()

        return None


    def process_file_content(self, file_id: str,
                             chunk_size: int=100, overlap_size: int=20):

        
        file_content = self.get_file_content(file_id=file_id)

        if file_content is None:
            self.logger.error(f"Error While processing {file_id}")
            return None

        file_content_texts = [rec.page_content for rec in file_content]

        file_content_metadata = [rec.metadata for rec in file_content]

        chunks = self.process_simplier_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size
        )

        return chunks


    def process_simplier_splitter(
        self,
        texts: List[str],
        metadatas: List[dict],
        chunk_size: int,
        splitter_tag: str = "\n"
    ):

        chunks = []

        for text, metadata in zip(texts, metadatas):

            lines = [
                line.strip()
                for line in text.split(splitter_tag)
                if len(line.strip()) > 1
            ]

            cur_chunk = ""

            for line in lines:

                cur_chunk += line + splitter_tag

                if len(cur_chunk) >= chunk_size:

                    chunks.append(
                        Document(
                            page_content=cur_chunk.strip(),
                            metadata=metadata.copy()
                        )
                    )

                    cur_chunk = ""

            if len(cur_chunk.strip()) > 0:

                chunks.append(
                    Document(
                        page_content=cur_chunk.strip(),
                        metadata=metadata.copy()
                    )
                )

        return chunks
       
