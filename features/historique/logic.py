
from dotenv import load_dotenv
import os
from fastapi import APIRouter, Response, Request, Depends, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import uuid
from typing import List

from features.historique.models import Historique, Image
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

    return " et ".join(formatted_fruits) + "."


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
        results_data = get_dict_result(results)
        info_dict["results"] = results_data
        result_dict.append(info_dict)
    return result_dict


@router.post("/create-activity/")
async def upload_images(
    request: Request,
    response: Response,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db)
):

    # token = get_auth_token_in_request(request)

    # user: Utilisateur = get_user_from_session(session, token)

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
        result = "5,bananes mûres;3,pommes vertes"  # Call api ici
        image = Image(image_path=path, id_image=uuid.uuid4(), resultat=result)
        images.append(image)

    result_dict = encode_image_results(images)

    description = "\n".join([format_result(result["results"])
                             for result in result_dict])

    activity_data = {
        "nbre_total_img": len(file_paths),
        "description": description,
        "images": images,
        "id_utilisateur": uuid.UUID("01120004-b07f-4c31-8de1-4dbe326c9654"),
    }

    new_activity = Historique(**activity_data)

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

    return JSONResponse(
        content={
            "message": "Images téléversées avec succès",
            "global_result": activity_data["description"],
            "result_data": result_dict,
            "images": [image.image_path for image in new_activity.images]
        },
        status_code=201
    )


@router.get("/activities")
def get_all_historiques(session: Session = Depends(get_db)):
    historiques = (
        session.query(Historique)
        .options(joinedload(Historique.images))
        .all()
    )
    histories = []
    for hist in historiques:
        data = hist.__dict__
        data["images"] = encode_image_results(hist.images)
        histories.append(data)
    return histories
