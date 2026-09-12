from .providers import CrossEncoderProvider
from .RerankerEnums import RerankerEnums


class RerankerProviderFactory:

    def __init__(self, config):

        self.config = config


    def create(self, provider: str):

        if provider == RerankerEnums.CrossEncoder.value:

            return CrossEncoderProvider(
                model_id=self.config.RERANKER_MODEL_ID,
                max_length=self.config.RERANKER_MAX_LENGTH
            )


        return None