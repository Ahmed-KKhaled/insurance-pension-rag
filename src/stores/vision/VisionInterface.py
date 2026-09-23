from abc import ABC, abstractmethod


class VisionInterface(ABC):

    @abstractmethod
    async def extract(self, image: list[str]) -> str:
        pass

    