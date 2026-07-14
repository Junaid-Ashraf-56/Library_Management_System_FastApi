from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.paths import GENERATED_DIR
from app.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from app.routes.book_routes import router as book_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthorizationError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})

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
app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


@app.get("/")
async def root():
    return {"message": "Library Management API is running"}
