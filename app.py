import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.dbconfig import create_tables
from core.utils import verify_credentials
from features.auth.logic import router as auth_router
from features.historique.logic import router as activities_router

# Load environment variables
load_dotenv()

# Read environment variables
STATIC_DIR = os.getenv('STATIC_DIR')

# Logger setup
logger = logging.getLogger(__name__)

# Allowed origins for CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

# Jinja2 templates setup
templates = Jinja2Templates(directory="templates")  # Folder containing HTML files


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


# FastAPI application setup
app = FastAPI(title="API Fruit Rec", lifespan=lifespan, docs_url=None)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(activities_router)

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    return {"message": "API Fruit Rec"}


@app.exception_handler(500)
async def custom_internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": f"{str(exc)}"},
    )


@app.get("/docs", include_in_schema=False)
async def docs(request: Request, authenticated: bool = Depends(verify_credentials)):
    return templates.TemplateResponse("docs/index.html", {"request": request})
