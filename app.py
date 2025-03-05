

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.dbconfig import create_tables
from features.auth.logic import router as auth_router
from features.historique.logic import router as activities_router


import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="API Fruit Rec")

app.include_router(auth_router)
app.include_router(activities_router)


@app.on_event("startup")
def startup():
    create_tables()


@app.get("/")
def read_root():
    return {"message": "API Fruit Rec "}


@app.exception_handler(500)
async def custom_internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": f"{str(exc)}"
        }
    )
