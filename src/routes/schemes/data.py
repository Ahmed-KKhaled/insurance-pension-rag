from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0


Asset_config={
        "document_type": "law",
        "law_number": "148",
        "law_year": "2019",
        "title": "قانون التأمينات الاجتماعية والمعاشات",
        "source": "قانون التأمينات الاجتماعية والمعاشات رقم 148 لسنة 2019",
        "language": "ar",
    }
