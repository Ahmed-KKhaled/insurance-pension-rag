from abc import ABC, abstractmethod
from typing import List

from models.db_schemes import RetrievedDocument


class RerankerInterface(ABC):

    @abstractmethod
    def rerank(self, query: str,
                     documents: List[RetrievedDocument]) -> List[RetrievedDocument]:

        """
        Rerank retrieved documents based on their relevance to the query.
        """
        pass