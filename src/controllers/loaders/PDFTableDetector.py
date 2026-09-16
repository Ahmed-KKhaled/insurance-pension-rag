import pdfplumber


class PDFTableDetector:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def detect_table_pages(self) -> list[int]:

        table_pages = []

        with pdfplumber.open(self.file_path) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                tables = page.extract_tables()

                if tables:
                    table_pages.append(page_number)

        return table_pages