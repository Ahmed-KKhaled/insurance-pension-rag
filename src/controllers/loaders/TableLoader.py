from img2table.document import Image as TableImage
from img2table.ocr import TesseractOCR

import fitz
import io
import os
import tempfile

from PIL import Image as PILImage


class TableLoader:

    def __init__(self, file_path: str, dpi: int = 300):
        self.file_path = file_path
        self.dpi = dpi

        self.ocr = TesseractOCR(
            n_threads=1,
            lang="ara"
        )




    def render_page(self, page_number: int) -> str:

        pdf = fitz.open(self.file_path)

        page = pdf[page_number - 1]

        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        )

        image_path = temp_file.name
        temp_file.close()

        pix.save(image_path)

        pdf.close()

        return image_path
