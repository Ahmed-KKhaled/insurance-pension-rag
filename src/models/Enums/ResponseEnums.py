from enum import Enum


class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file validated success"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEDDED = "file size excedded"
    FILE_UPLOADED_SUCCESS = 'file uploaded success'
    FILE_UPLOADED_FAIL = 'file uploaded fail'
    
    