from .BaseController import BaseController
from fastapi import UploadFile
import logging


class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # convert MB to bytes
        self.logger = logging.getLogger(__name__)


    def validate_uploaded_file(self, file: UploadFile) -> bool:

        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            self.logger.error(f"only file types allowed are {self.app_settings.FILE_ALLOWED_EXTENSIONS}")
            return False

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            self.logger.error(f"max size allowed is {self.app_settings.FILE_MAX_SIZE}")
            return False

        return True