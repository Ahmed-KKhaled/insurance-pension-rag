from .BaseController import BaseController
from models import Project, Chunk
from models.db_schemes.insurance_rag.schemes import Conversation, Message
from typing import List
from stores.llm.LLMEnums import DocumentTypeEnum
from stores.vectordb.VectorDBEnums import PgVectorTableSchemeEnums
import logging
from models.db_schemes import RetrievedDocument
from services.MetadataFilterExtractor import MetadataFilterExtractor
from helpers.metadata import FILTERABLE_METADATA
from .enums.nlp import ProcessControllerEnums

class NLPController(BaseController):

    def __init__(self, vectordb_client, 
                       generation_client,
                       embedding_client,
                       template_parser,
                       reranker_client,
                       message_model):
        
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
        self.reranker_client = reranker_client
        self.message_model = message_model
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

        #step3: extract metadata filters from user query
        metadata_filter = MetadataFilterExtractor(
            generation_client=self.generation_client,
            template_parser=self.template_parser
        )
        filters =  metadata_filter.extract(
            query=text,
            available_fields=FILTERABLE_METADATA
        )

        vector_results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit,
            filters=filters
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
        ), filters

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


    async def answer_rag_questions(self, project: Project,
                                         query: str,
                                         limit: int=10,
                                         retrieval_limit: int = 20,
                                         chat_history: list = None):

        if chat_history is None:
            chat_history = []


        answer, full_prompt = None, None

        # 1) retrieve related documents
        retrieved_documents, filters = await self.search_hybrid(
            project=project,
            text=query,
            limit=retrieval_limit
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            answer = ProcessControllerEnums.ANSWER.value
            
            return answer, full_prompt, chat_history, [], filters


        # 2) Rerank retrieved documents
        reranked_documents = self.reranker_client.rerank(
            query=query,
            documents=retrieved_documents
        )

        if not reranked_documents or len(reranked_documents) == 0:
            return answer, full_prompt, chat_history, []

        # 3) Keep only the top-k reranked documents
        retrieved_documents = reranked_documents[:limit]

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
                "chunk_text": doc.text
            }
        )  for idx, doc in  enumerate(retrieved_documents)])

        footer_prompt = self.template_parser.get(
            group="rag",
            key="footer_prompt",
            vars={
                "query" : query
            }
        )

        system_message = self.generation_client.construct_prompt(
        prompt=system_prompt,
        role=self.generation_client.enums.SYSTEM.value
)

        chat_history = [system_message] + chat_history


        full_prompt = "\n\n".join([
            documents_prompts,
            footer_prompt
        ])


        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,

        )


        self.logger.info(f"Generated answer: {answer!r}")

        return answer, full_prompt, chat_history, retrieved_documents, filters


    def build_chat_history(self, messages: list):
    
        chat_history = []

        for message in messages:

            if message.role == "user":
                role = self.generation_client.enums.USER.value

            elif message.role == "assistant":
                role = self.generation_client.enums.ASSISTANT.value

            else:
                continue

            chat_history.append(
                self.generation_client.construct_prompt(
                    prompt=message.content,
                    role=role
                )
            )

        return chat_history

    def build_rewrite_history(self, messages: list) -> str:

        history = []

        for message in messages:

            history.append(
                f"{message.role}: {message.content}"
            )

        return "\n".join(history)

    async def answer_chat_question(
    self,
    project: Project,
    conversation,
    query: str,
    limit: int = 10,
    retrieval_limit: int = 20):

        # 1. Load previous messages
        messages = await self.message_model.get_messages_by_conversation_id(
            conversation_id=conversation.conversation_id,
        )

        # 2. Convert DB messages to LLM chat history
        chat_history = self.build_chat_history(
            messages=messages
        )

        if messages:
            # For query rewriting
            rewrite_history = self.build_rewrite_history(
                messages=messages
            )

            query_rewriter_prompt = self.template_parser.get(
                        group="rag",
                        key="query_rewriter_prompt",
                        vars={
                            "chat_history" : rewrite_history,
                            "query" : query
                        }
            )

            rewritten_query = self.generation_client.generate_text(
                prompt=query_rewriter_prompt,
                chat_history=[]
            )

            rewritten_query = rewritten_query.strip()

        else:
            rewritten_query=query
        

        # 3. Run RAG
        answer, full_prompt, _, retrieved_documents, filters = (
            await self.answer_rag_questions(
                project=project,
                query=rewritten_query,
                limit=limit,
                retrieval_limit=retrieval_limit,
                chat_history=chat_history
            )
        )

        if not answer:
            return answer, full_prompt, retrieved_documents, chat_history, rewritten_query, filters

        # 4. Save user message
        user_message = Message(
            role=self.generation_client.enums.USER.value,
            content=query,
            message_conversation_id=conversation.conversation_id
        )

        await self.message_model.insert_message(
            message=user_message
        )

        # 5. Save assistant message
        assistant_message = Message(
            role=self.generation_client.enums.ASSISTANT.value,
            content=answer,
            message_conversation_id=conversation.conversation_id
        )

        await self.message_model.insert_message(
            message=assistant_message
        )

        return answer, full_prompt, retrieved_documents, chat_history, rewritten_query, filters