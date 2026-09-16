import io
import fitz
import pytesseract

from PIL import Image
from dataclasses import dataclass


@dataclass
class OCRDocument:
    page_content: str
    metadata: dict


class OCRPDFLoader:

    def __init__(self, file_path: str, dpi: int = 150, excluded_pages: list[int] | None = None):
        self.file_path = file_path
        self.dpi = dpi
        self.excluded_pages = set(
            excluded_pages or []
        )

    def load(self):

        pdf = fitz.open(self.file_path)

        documents = []

        zoom = self.dpi / 72

        matrix = fitz.Matrix(
            zoom,
            zoom
        )

        for page_number, page in enumerate(pdf):

            if page_number in self.excluded_pages:
                continue

            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            text = pytesseract.image_to_string(
                image,
                lang="ara"
            )

            if not text.strip():
                continue

            documents.append(
                OCRDocument(
                    page_content=text,
                    metadata={
                        "page": page_number + 1,
                        "source": self.file_path,
                    }
                )
            )

        pdf.close()

        return documents