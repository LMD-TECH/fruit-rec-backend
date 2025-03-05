from fastapi import APIRouter
from core.lib.session import session

router = APIRouter(
    prefix="/api/activities",
    tags=["Activities"],
)


@router.get("/create")
def create():
    return {"message": "Activities created"}
