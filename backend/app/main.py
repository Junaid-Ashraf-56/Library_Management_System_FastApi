from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.paths import GENERATED_DIR
from app.routes.library_routes import router as library_router

GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(library_router)
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


@app.get("/")
async def root():
    return {"message": "Library Management API is running"}
