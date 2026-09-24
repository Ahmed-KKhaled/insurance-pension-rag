from ..VisionInterface import VisionInterface


import httpx
import base64

class OpenRouterProvider(VisionInterface):

    def __init__(
            self,
            template_parser,
            model_id: str,
            api_key: str,
            base_url: str,
            ollama_host: str=None,
            
    ):

        self.template_parser = template_parser
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url


    async def extract_text_from_table(self, images: list[str]) -> list[str]:

        if not images:
            raise ValueError(
                "At least one image is required."
            )

        if len(images) != 1:
            raise ValueError(
                "Only one image is allowed per request."
            )

        image = images[0]

        prompt = self.template_parser.get(
            group="rag",
            key="extract_text_from_image_prompt",
        )

        with open(image, "rb") as file:
            image_bytes = file.read()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:image/png;base64,{image_base64}"
        )

        content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            },
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
        }

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        text = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        return [text]


    async def extract_text_from_image(self, image: str) -> str:

        if not image:
            raise ValueError(
                "An image is required."
            )

        prompt = self.template_parser.get(
            group="rag",
            key="vision_image_extractor_prompt",
        )

        with open(image, "rb") as file:
            image_bytes = file.read()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:image/png;base64,{image_base64}"
        )

        content = [
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                },
            },
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
        }

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        text = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        return text