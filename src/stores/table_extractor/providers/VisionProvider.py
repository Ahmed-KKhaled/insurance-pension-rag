import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
from ..TableExtractorInterface import TableExtractorInterface
import time

class VisionProvider(TableExtractorInterface):

    def __init__(self, template_parser, model_id: str=None):

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = AutoProcessor.from_pretrained(model_id)

        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto"
        )

        self.template_parser = template_parser

    async def extract(self, image: str) -> str:

        vision_table_extractor_prompt = self.template_parser.get(
            group="rag",
            key="vision_table_extractor_prompt",
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image
                    },
                    {
                        "type": "text",
                        "text": vision_table_extractor_prompt
                    }
                ]
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt"
        )

        inputs = inputs.to(self.model.device)

        print(
            "Image:",
            image.size if hasattr(image, "size") else type(image)
        )

        print(
            "Input tokens:",
            inputs.input_ids.shape
        )

        print(
            "Device:",
            self.model.device
        )

        start_time = time.time()

        generated_ids = self.model.generate(
            **inputs,
            max_new_tokens=512
        )

        elapsed_time = time.time() - start_time

        print(
            f"Generation time: {elapsed_time:.2f} seconds"
        )


        generated_ids_trimmed = [
            output_ids[len(input_ids):]
            for input_ids, output_ids
            in zip(inputs.input_ids, generated_ids)
        ]

        output = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        return output.strip()