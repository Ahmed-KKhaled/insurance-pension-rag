from .TableExtractorInterface import TableExtractorInterface
from .providers.Img2TableProvider import Img2TableProvider
from .providers.VisionProvider import VisionProvider
from .TableExtractorEnums import TableExtractorEnums

class TableExtractorFactory:

    def __init__(self, config, template_parser):
        self.config = config
        self.template_parser = template_parser

    
    def create(self, extractor_type: str):

        if extractor_type == TableExtractorEnums.IMG2TABLE.value:
            return Img2TableProvider(
                model_id=self.config.VISION_MODEL_ID,
                template_parser=self.template_parser
            )

        if extractor_type == TableExtractorEnums.VISION_MODEL.value:
            return VisionProvider(
                model_id=self.config.VISION_MODEL_ID,
                template_parser=self.template_parser
            )

        raise ValueError(
            f"Unsupported table extractor: {extractor_type}"
        )