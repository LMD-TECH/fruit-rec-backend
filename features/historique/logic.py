
from dotenv import load_dotenv
import os
from fastapi import APIRouter, Response, Request, Depends, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
import uuid
from typing import List
from urllib.parse import urljoin
from features.historique.models import Historique
from features.uploads.models import Image
from core.dbconfig import get_db
from core.utils import chat_with_gemini, get_auth_token_in_request, get_user_from_session
from features.auth.models import Utilisateur
from .utils import encode_image_results, format_result
from ..uploads.logic import create_image_file
import pathlib
from google.genai import types

load_dotenv()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")

router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"],
)


@router.post("/create-activity/")
async def upload_images(
    request: Request,
    response: Response,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db)
):

    token = get_auth_token_in_request(request)

    user: Utilisateur = get_user_from_session(session, token)

    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier téléversé")

    file_paths = []

    for file in files:
        if not file.content_type.startswith("image/"):
            continue

        file_path = create_image_file(file)
        file_paths.append(file_path)

    images = []
    for path in file_paths:
        prompt = "Analyse cette image et identifie les fruits présents. Fournis le résultat strictement au format suivant : 'quantité,nom_du_fruit;quantité,nom_du_fruit;...'. Assure-toi d'utiliser des noms simples et reconnaissables pour chaque fruit. Si aucun fruit n'est détecté, renvoie exactement cette chaîne sans modification : 'aucun,fruit détecté'"

        b64_image = types.Part.from_bytes(
            data=pathlib.Path(path[1:]).read_bytes(),
            mime_type="image/jpeg"
        )

        contents = [prompt, b64_image]
        result = chat_with_gemini(contents)
        # fake_result = "5,bananes mûres;3,pommes vertes;6,autres fruits"
        image = Image(image_path=path,
                      id_image=uuid.uuid4(), resultat=result)
        images.append(image)

    result_dict = encode_image_results(images)

    description = "\n\n".join([format_result(result["fruits"])
                               for result in result_dict])

    activity_data = {
        "nbre_total_img": len(file_paths),
        "description": description,
        "images": images,
        "id_utilisateur": user.id_utilisateur,
    }

    new_activity: Historique = Historique(**activity_data)

    try:
        session.add(new_activity)
        session.commit()
        session.refresh(new_activity)

    except Exception as e:
        session.rollback()
        return JSONResponse(
            content={"message": "Une erreur s'est produite !",
                     "error": str(e)},
            status_code=500
        )

    results = []
    for r in result_dict:
        new_result = r.copy()
        new_result["image_url"] = urljoin(
            str(request.base_url), r["image_url"])
        results.append(new_result)

    return JSONResponse(
        content={
            "message": "Images téléversées avec succès",
            "global_result": activity_data["description"],
            "result_data": results,
            "images": [urljoin(str(request.base_url), image.image_path) for image in new_activity.images]
        },
        status_code=201
    )


@router.get("/activities")
def get_all_historiques(request: Request, response: Response, session: Session = Depends(get_db)):

    token = get_auth_token_in_request(request)
    user: Utilisateur = get_user_from_session(session, token)

    historiques = (
        session.query(Historique)
        .options(joinedload(Historique.images))
        .filter(Historique.id_utilisateur == user.id_utilisateur)
    )

    histories = []
    for hist in historiques:
        data = hist.__dict__
        images = encode_image_results(hist.images)
        new_images = []
        for image in images:
            img = image.copy()
            img["image_url"] = urljoin(
                str(request.base_url), image["image_url"])
            new_images.append(img)
        data["images"] = new_images
        histories.append(data)

    total_images = 0
    for hist in historiques:
        total_images += len(hist.images)

    total_fruits = 0
    for history in histories:
        for image in history["images"]:
            total_fruits += len(image["fruits"])

    try:
        moyenne_fruits_images = round(total_fruits/total_images, 2)
    except:
        moyenne_fruits_images = 0

    stats = {
        "total_images": total_images,
        "total_fruits": total_fruits,
        "moyenne_fruits_images": moyenne_fruits_images,
    }

    return {"histories": histories, "stats": stats}
