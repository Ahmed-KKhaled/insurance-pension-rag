from enum import Enum


class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file validated success"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEDDED = "file size excedded"
    FILE_UPLOADED_SUCCESS = 'file uploaded success'
    FILE_UPLOADED_FAIL = 'file uploaded fail'
    FILE_PROCESSED_SUCCESS = "file_processed_success"
    FILE_PROCESSED_FAIL = "file_processed_fail"
    
    