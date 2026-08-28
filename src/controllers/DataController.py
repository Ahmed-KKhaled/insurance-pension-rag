from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal


class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # convert MB to bytes


    def validate_uploaded_file(self, file: UploadFile) -> bool:

        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEDDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value