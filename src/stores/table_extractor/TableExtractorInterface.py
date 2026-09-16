from abc import ABC, abstractmethod


class TableExtractorInterface(ABC):

    @abstractmethod
    async def extract(self, image: str) -> str:
        pass

    