from img2table.document import Image as TableImage
from img2table.ocr import TesseractOCR
from ..VisionInterface import VisionInterface


class Img2TableProvider(VisionInterface):

    def __init__(self, model_id: str=None, template_parser: None=None, ollama_host:str=None, api_key: str=None, base_url: str=None):
        self.ocr = TesseractOCR(
            n_threads=1,
            lang="ara"
        )

    async def extract(self, image: str) -> str:

        document = TableImage(src=image)

        tables = document.extract_tables(
            ocr=self.ocr,
            implicit_rows=True,
            implicit_columns=True,
            borderless_tables=True
        )

        extracted_text = []

        for table in tables:

            dataframe = table.df

            for _, row in dataframe.iterrows():

                cells = []

                for cell in row.tolist():

                    if cell is None:
                        continue

                    cell = str(cell).strip()

                    if not cell or cell.lower() == "nan":
                        continue

                    # Fix Arabic word order
                    cell = " ".join(cell.split()[::-1])

                    cells.append(cell)

                if cells:
                    extracted_text.append(" | ".join(cells))

        return "\n".join(extracted_text)

    async def extract_text_from_image(self, image: str) -> str:
            raise NotImplementedError