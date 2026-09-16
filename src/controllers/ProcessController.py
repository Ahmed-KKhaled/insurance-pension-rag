from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from .loaders import OCRPDFLoader, PDFTableDetector, TableLoader
import re
from models import ProcessingEnum
import logging
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    page_content : str
    metadata: dict

class ProcessController(BaseController):
    def __init__(self, project_id: str, table_extractor):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        self.logger = logging.getLogger("uvicorn.error")
        self.table_extractor = table_extractor


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
            return OCRPDFLoader(file_path)

        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)

        if loader:
         return loader.load()

        return None

    def normalize_text(self, text: str) -> str:

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if len(line) > 1:
                lines.append(line)

        return "\n".join(lines)

    async def process_file_content(self, file_id: str,
                             chunk_size: int=1000, overlap_size: int=100):


        file_ext = self.get_file_extension(file_id=file_id)

        if file_ext == ProcessingEnum.PDF.value:
            return await self.process_pdf(
                file_id=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )

        if file_ext == ProcessingEnum.TXT.value:
            return self.process_text(
                file_id=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )

    def process_text(
    self,
    file_id: str,
    chunk_size: int = 1000,
    overlap_size: int = 100
):

        file_content = self.get_file_content(
            file_id=file_id
        )

        if file_content is None:
            self.logger.error(
                f"Error While processing {file_id}"
            )
            return None

        documents = []

        for page in file_content:

            text = self.normalize_text(
                text=page.page_content
            )

            if not text:
                continue

            page_documents = (
                self.process_section_aware_splitter(
                    text=text,
                    metadata=page.metadata.copy(),
                    chunk_size=chunk_size,
                    overlap_size=overlap_size
                )
            )

            documents.extend(page_documents)

        return documents


    def process_section_aware_splitter(
            self, 
            text: str,
            metadata: dict,
            chunk_size: int,
            overlap_size: int
    ):

        self.logger.info("start split_by_articles")
        
        sections = self.split_by_articles(text)

        chunks = []
        self.logger.info("end split_by_articles")

        self.logger.info("start loop sections")

        for article_num, article_text in sections:

            article_text = article_text.strip()

            if not article_text:
                continue

            article_metadata = metadata.copy()
            article_metadata["article"] = article_num

            article_chunks = self.split_large_section(
                text=article_text,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )

            for chunk in article_chunks:

                chunks.append(
                    Document(
                        page_content=chunk,
                        metadata=article_metadata.copy()
                    )
                )

        self.logger.info("end loop sections")

        return chunks


    def split_by_articles(self, text: str):

        pattern = r"(?=مادة\s*(?:\(\s*)?[0-9٠-٩]+\s*(?:\))?\s*:?)"

        matches = list(
            re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

        if not matches:
            return [
                ("unknown", text)
            ]

        sections = []

        for index, match in enumerate(matches):

            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            article_text = text[start:end].strip()

            article_number = match.group().strip()

            sections.append(
                (
                    article_number,
                    article_text
                )
            )

        return sections


    def split_large_section(
        self,
        text: str,
        chunk_size: int,
        overlap_size: int
    ):

        if len(text) <= chunk_size:
            return [text]

        words = text.split()

        chunks = []

        current_chunk = []
        current_length = 0

        for word in words:

            word_length = len(word) + 1

            if (
                current_length + word_length > chunk_size
                and current_chunk
            ):

                chunk = " ".join(current_chunk)

                chunks.append(chunk)

                overlap_words = []
                overlap_length = 0

                for previous_word in reversed(current_chunk):

                    if overlap_length + len(previous_word) + 1 > overlap_size:
                        break

                    overlap_words.insert(
                        0,
                        previous_word
                    )

                    overlap_length += len(previous_word) + 1

                current_chunk = overlap_words

                current_length = overlap_length

            current_chunk.append(word)
            current_length += word_length

        if current_chunk:
            chunks.append(
                " ".join(current_chunk)
            )

        return chunks

    async def process_pdf(
    self,
    file_id: str,
    chunk_size: int = 1000,
    overlap_size: int = 100
):

        file_path = os.path.join(
            self.project_path,
            file_id
        )

        table_detector = PDFTableDetector(
            file_path=file_path
        )

        table_pages = table_detector.detect_table_pages()

        self.logger.info(
            f"Detected table pages: {table_pages}"
        )

        ocr_loader = OCRPDFLoader(
            file_path=file_path,
            excluded_pages=table_pages
        )

        normal_documents = ocr_loader.load()
        self.logger.info(f"number of normal docs {len(normal_documents)}")

        table_loader = TableLoader(
            file_path=file_path,
            dpi=150
        )

        table_documents = []

        for page_number in table_pages:

            image_path = table_loader.render_page(
                page_number=page_number
            )


            text = ""

            try:
                text = await self.table_extractor.extract(
                    image=image_path
                )

            finally:
                if os.path.exists(image_path):
                    os.unlink(image_path)

            if not text.strip():
                continue

            table_documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": page_number,
                        "content_type": "table",
                        "source": file_id
                    }
                )
            )

        # 4. Process normal text
        documents = []

        for page in normal_documents:

            text = self.normalize_text(
                page.page_content
            )

            if not text:
                continue

            page_documents = (
                self.process_section_aware_splitter(
                    text=text,
                    metadata=page.metadata.copy(),
                    chunk_size=chunk_size,
                    overlap_size=overlap_size
                )
            )

            documents.extend(page_documents)

        # 5. Add tables
        documents.extend(table_documents)

        return documents
                    