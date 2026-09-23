from enum import Enum


class ProcessControllerEnums(Enum):

    NO_AVAILABLE_DOCUMENT_ANSWER = (
        "عذرًا، لا تتوفر في المستندات المتاحة معلومات كافية "
        "للإجابة عن هذا السؤال بدقة. "
        "يرجى إعادة صياغة السؤال أو تقديم مزيد من التفاصيل."
    )

    base_metadata = {
        "source": "قانون التأمينات الاجتماعية والمعاشات رقم 148 لسنة 2019",
        "document_type": "law",
        "law_number": "148",
        "law_year": "2019",
        "language": "ar",
    }

    ALLOWED_METADATA_VALUES = {
        "law_number": {"148"},
        "law_year": {"2019"},
    }

    PORMPT_INJUCTED_ANSWER = "عذرًا، لا يمكنني معالجة هذا الطلب."
