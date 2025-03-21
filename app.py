import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from core.dbconfig import create_tables
from fastapi.staticfiles import StaticFiles
from features.auth.logic import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from features.historique.logic import router as activities_router
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

load_dotenv()

# Lecture des Var Environment
STATIC_DIR = os.getenv('STATIC_DIR')


logger = logging.getLogger(__name__)

# app = FastAPI(title="API Fruit Rec")

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="API Fruit Rec", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(activities_router)

# TODO: revoir la methode de demarrage de l'app -> le deco


# @app.on_event("startup")
# def startup():
#     create_tables()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)


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
