import os
import shutil
from fastapi import UploadFile
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")


def create_image_file(file: UploadFile):
    timestamp = str(uuid.uuid4())
    file_name = timestamp + "." + file.filename.split(".")[-1]
    path = os.path.join(UPLOADS_DIR, file_name)
    with open(path, "wb") as blob:
        shutil.copyfileobj(file.file, blob)
    return "/"+UPLOADS_DIR + "/" + file_name
