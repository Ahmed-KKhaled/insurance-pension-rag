from abc import ABC, abstractmethod


class VisionInterface(ABC):

    @abstractmethod
    async def extract_text_from_table(self, image: list[str]) -> str:
        pass


    @abstractmethod
    async def extract_text_from_image(self, image: str) -> str:
        pass



    