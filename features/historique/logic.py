
from dotenv import load_dotenv
import os
from fastapi import APIRouter, Response, Request, Depends, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import urllib.parse
import uuid
from typing import List
from urllib.parse import urljoin
from features.historique.models import Historique
from features.uploads.models import Image
from core.dbconfig import get_db
from core.utils import get_auth_token_in_request, get_user_from_session
from features.auth.models import Utilisateur
from ..uploads.logic import create_image_file

load_dotenv()

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "static")

router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"],
)


def format_result(results: List[dict]) -> List[str]:
    fruit_counts = {}

    for item in results:
        name = item["fruit_name"]
        quantity = int(item["quantity"])

        if name in fruit_counts:
            fruit_counts[name] += quantity
        else:
            fruit_counts[name] = quantity

    formatted_fruits = [f"{qty} {fruit}" for fruit,
                        qty in fruit_counts.items()]

    return ", ".join(formatted_fruits) + "."


def get_dict_result(results):
    results_data = []
    for r in results:
        info = {}
        info["quantity"] = r.split(",")[0]
        info["fruit_name"] = r.split(",")[-1]
        results_data.append(info)
    return results_data


def encode_image_results(images: list[Image]):
    result_dict = []
    for item in images:
        res: str = item.resultat
        results = res.split(";")
        info_dict = {}
        info_dict["img_id"] = str(item.id_image)
        info_dict["image_url"] = str(item.image_path)
        fruits = get_dict_result(results)
        info_dict["fruits"] = fruits
        result_dict.append(info_dict)
    return result_dict


@router.post("/create-activity/")
async def upload_images(
    request: Request,
    response: Response,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db)
):

    token = get_auth_token_in_request(request)

    user: Utilisateur = get_user_from_session(session, token)

    print("OwerFiles", files)
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
        # les fruits sont separé par des ; [puis les infos(la quantité et le nom) sur chaque fruit sont separé par des , simples]

        fruits = [
            {
                "quantity": 1,
                "name": "Banane"
            },
            {
                "quantity": 1,
                "name": "Pomme"
            },
        ]
        result = "5,bananes mûres;3,pommes vertes;6,autres fruits"  # Call api ici
        image = Image(image_path=path, id_image=uuid.uuid4(), resultat=result)
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
