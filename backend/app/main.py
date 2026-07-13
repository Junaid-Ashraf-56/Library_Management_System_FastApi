from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.library_routes import router as library_router

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


@app.get("/")
async def root():
    return {"message": "Library Management API is running"}
