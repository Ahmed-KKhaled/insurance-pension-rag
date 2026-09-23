from ollama import AsyncClient

from ..VisionInterface import VisionInterface


class OllamaProvider(VisionInterface):

    def __init__(
        self,
        template_parser,
        model_id: str,
        ollama_host: str,
        api_key: str=None,
        base_url: str=None
        
    ):
        self.template_parser = template_parser
        self.model_id = model_id

        self.client = AsyncClient(
            host=ollama_host
        )

    async def extract(self, image: str) -> str:

        vision_table_extractor_prompt = self.template_parser.get(
            group="rag",
            key="vision_table_extractor_prompt",
        )

        response = await self.client.chat(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": vision_table_extractor_prompt,
                    "images": [image],
                }
            ],
            think=False
        )

        return response["message"]["content"].strip()