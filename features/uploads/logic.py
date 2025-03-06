import os
import shutil
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")


def create_image_file(file: UploadFile):
    path = os.path.join(UPLOADS_DIR, file.filename)
    with open(path, "wb") as blob:
        shutil.copyfileobj(file.file, blob)
    return "/"+UPLOADS_DIR + "/" + file.filename
