from fastapi import APIRouter
from dotenv import load_dotenv
import os
from fastapi import UploadFile
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from fastapi.responses import JSONResponse
from ..uploads.logic import create_image_file


# Permettre à l'utilisateur de téléverser
# une ou plusieurs image et de voir la description
router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"],
)
load_dotenv()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")


@router.post("/create-activity/")
async def upload_images(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier téléversé")

    file_paths = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail=f"Le fichier {file.filename} n'est pas une image")

        file_path = create_image_file(file)
        file_paths.append(file_path)

    return JSONResponse(content={"message": "Images téléversées avec succès", "file_paths": file_paths})
