from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.book_routes import router as book_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

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

app.include_router(user_router)
app.include_router(book_router)
app.include_router(loan_router)


@app.get("/")
async def root():
    return {"message": "Library Management API is running"}
