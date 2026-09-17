import json
import logging


class MetadataFilterExtractor:

    def __init__(self, generation_client, template_parser):
        self.generation_client = generation_client
        self.template_parser = template_parser
        self.logger = logging.getLogger("uvicorn.error")

    async def extract(
        self,
        query: str,
        available_fields: list[str]
    ) -> dict:

        metadata_filter_extractor_prompt = self.template_parser.get(
            group="rag",
            key="metadata_filter_extractor_prompt",
            vars={
                "available_fields": available_fields,
                "query": query
            }
        )

        try:
            response =  self.generation_client.generate_text(
                prompt=metadata_filter_extractor_prompt
            )

            response = response.strip()

            if response.startswith("```json"):
                response = response[7:]

            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()

            result = json.loads(response)

            filters = result.get("filters", {})

            if not isinstance(filters, dict):
                return {}

            filters = {
                key: value
                for key, value in filters.items()
                if key in available_fields
            }

            return filters

        except Exception as e:
            self.logger.error(
                f"Metadata extraction error: {e}"
            )
            return {}