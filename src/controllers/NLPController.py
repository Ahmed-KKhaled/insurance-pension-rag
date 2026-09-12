from .BaseController import BaseController
from models import Project, Chunk
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.vectordb.VectorDBEnums import PgVectorTableSchemeEnums
import logging
from models.db_schemes import RetrievedDocument

class NLPController(BaseController):

    def __init__(self, vectordb_client, 
                       generation_client,
                       embedding_client,
                       template_parser,
                       reranker_client):
        
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        self.reranker_client = reranker_client
        self.logger = logging.getLogger("uvicorn")


    def create_collection_name(self, project_id: str):
        return f"{PgVectorTableSchemeEnums._PREFIX.value}_collection_{self.vectordb_client.default_vector_size}_{project_id}"

    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(
            project_id=project.project_id
        )

        return await self.vectordb_client.delete_collection(
            collection_name=collection_name
        )

    async def get_vector_collection_info(self, project: Project):
        collection_name = self.create_collection_name(
                    project_id=project.project_id
                )

        collection_info = await self.vectordb_client.get_collection_info(
            collection_name=collection_name
        )
        return collection_info


    async def index_into_vector_db(self, project: Project,
                                  chunks: List[Chunk],
                                  do_reset: bool=False,
                                  chunks_ids: List[int]=None):


        # 1) get collection name
        collection_name = self.create_collection_name(
            project_id=project.project_id
        )

        # 2) manage items
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = self.embedding_client.embed_text(
                text=texts,
                document_type=DocumentTypeEnum.DOCUMENT.value
            )

        if any(vector is None for vector in vectors):
            self.logger.error(
                "Embedding failed for one or more chunks — check the "
                "embedding backend/API key before indexing."
            )
            return False

        # 3) create collection if not exists
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )


        # 4) insert into vector db
        is_inserted = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=chunks_ids
        )

        return is_inserted


    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        query_vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)


        if not query_vector or len(query_vector) == 0:
            return False

        # step3: do semantic search
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector= query_vector,
            limit=limit
        )

        if not results:
            return False

        return results

    async def search_hybrid(
        self,
        project: Project,
        text: str,
        limit: int = 20
    ):

        
        collection_name = self.create_collection_name(
            project_id=project.project_id
        )


        query_vector = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not query_vector:
            return []

        vector_results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        keyword_results = await self.vectordb_client.search_by_keyword(
            collection_name=collection_name,
            query=text,
            limit=limit
        )

        return self.merge_results(
            vector_results=vector_results,
            keyword_results=keyword_results,
            limit=limit
        )


    async def answer_rag_questions(self, project: Project, query: str, limit: int=10, retrieval_limit: int = 20):


        answer, full_prompt, chat_history = None, None, None

        # 1) retrieve related documents
        retrieved_documents = await self.search_hybrid(
            project=project,
            text=query,
            limit=retrieval_limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history


        # 2) Rerank retrieved documents
        reranked_documents = self.reranker_client.rerank(
            query=query,
            documents=retrieved_documents
        )

        if not reranked_documents or len(reranked_documents) == 0:
            return answer, full_prompt, chat_history

        # 3) Keep only the top-k reranked documents
        if len(reranked_documents) >= limit:
             retrieved_documents = reranked_documents[:limit]

        else:
            retrieved_documents = reranked_documents

        # 4) construct the llm prompt
        system_prompt = self.template_parser.get(
            group="rag",
            key="system_prompt",
        )

        documents_prompts = "\n".join([self.template_parser.get(
            group="rag",
            key="document_prompt",
            vars={
                "doc_num":idx + 1,
                "chunk_text": self.generation_client.process_text(doc.text)
            }
        )  for idx, doc in  enumerate(retrieved_documents)])

        footer_prompt = self.template_parser.get(
            group="rag",
            key="footer_prompt",
            vars={
                "query" : query
            }
        )

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value

            )
        ]

        full_prompt = "\n\n".join([
            documents_prompts,
            footer_prompt
        ])


        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,

        )

        return answer, full_prompt, chat_history, retrieved_documents


    def merge_results(
        self,
        vector_results: List[RetrievedDocument],
        keyword_results: List[RetrievedDocument],
        limit: int = 20,
        k: int = 60
    ) -> List[RetrievedDocument]:

        scores = {}
        documents = {}

        for rank, document in enumerate(vector_results, start=1):

            document_id = document.text

            documents[document_id] = document

            scores[document_id] = scores.get(
                document_id,
                0
            ) + (1 / (k + rank))

        for rank, document in enumerate(keyword_results, start=1):

            document_id = document.text

            documents[document_id] = document

            scores[document_id] = scores.get(
                document_id,
                0
            ) + (1 / (k + rank))

        ranked_documents = sorted(
            documents.items(),
            key=lambda x: scores[x[0]],
            reverse=True
        )

        return [
            documents[document_id]
            for document_id, _ in ranked_documents[:limit]
        ]

        



        




