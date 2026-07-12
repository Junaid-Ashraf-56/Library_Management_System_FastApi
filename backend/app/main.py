from fastapi import FastAPI

from app.routes.library_routes import router as library_router

app = FastAPI()
app.include_router(library_router)


@app.get("/")
async def root():
    return {"message": "Library Management API is running"}
