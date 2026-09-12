from ..RerankerInterface import RerankerInterface
from sentence_transformers import CrossEncoder

from models.db_schemes import RetrievedDocument
from typing import List

class CrossEncoderProvider(RerankerInterface):

    def __init__(self, model_id: str, max_length: int):
        
        self.model = CrossEncoder(
            model_id,
            max_length=max_length,
            trust_remote_code=True
        )



    def rerank(self, query: str,
                     documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
    
            
            
        if not documents:
            return []

        pairs = [
            [query, document.text] for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked_documents = sorted(
            zip(documents, scores),
            key = lambda x: x[1],
            reverse=True
        )

        return [
            document for document, _ in ranked_documents
        ]