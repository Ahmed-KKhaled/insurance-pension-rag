from .providers.Img2TableProvider import Img2TableProvider
from .providers.OllamaProvider import OllamaProvider
from .providers.OpenRouterProvider import OpenRouterProvider
from .VisionEnums import VisionEnums

class VisionFactory:

    def __init__(self, config, template_parser):
        self.config = config
        self.template_parser = template_parser

    
    def create(self, provider: str):

        if provider == VisionEnums.IMG2TABLE.value:
            return Img2TableProvider(
                model_id=self.config.VISION_MODEL_ID,
                template_parser=self.template_parser,
                ollama_host=self.config.OLLAMA_HOST
            )

        if provider == VisionEnums.OLLAMA.value:
            return OllamaProvider(
                model_id=self.config.VISION_MODEL_ID,
                template_parser=self.template_parser,
                ollama_host=self.config.OLLAMA_HOST,
            )
        
        if provider == VisionEnums.OPENROUTER.value:
            return OpenRouterProvider(
                model_id=self.config.VISION_MODEL_ID,
                template_parser=self.template_parser,
                api_key=self.config.OPENROUTER_API_KEY,
                base_url=self.config.OPENROUTER_BASE_URL
            )

        raise ValueError(
            f"Unsupported table extractor: {provider}"
        )