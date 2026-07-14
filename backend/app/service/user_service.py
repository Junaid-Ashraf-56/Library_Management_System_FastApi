from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.auth import password as password_auth
from app.auth.jwt_auth import create_access_token
from app.model.enums import UserRole
from app.repository import user_repository
from app.repository.database import SessionLocal


def login_user(*, email: str, password: str, required_role: UserRole | None = None):
    db = SessionLocal()
    try:
        user = user_repository.get_user_by_email(db, email)
        if user is None or not password_auth.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if required_role is not None and user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="This account does not have librarian access.",
            )

        access_token = create_access_token(
            {"sub": str(user.user_id), "role": user.role.value}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()


def register_user(
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
):
    return _register_user(
        name=name,
        email=email,
        phone_number=phone_number,
        password=password,
        role=UserRole.MEMBER,
    )


def register_librarian(
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
):
    return _register_user(
        name=name,
        email=email,
        phone_number=phone_number,
        password=password,
        role=UserRole.LIBRARIAN,
    )


def _register_user(
    *,
    name: str,
    email: str,
    phone_number: str,
    password: str,
    role: UserRole,
):
    db = SessionLocal()
    try:
        user = user_repository.register_user(
            db,
            name=name,
            email=email,
            phone_number=phone_number,
            password=password_auth.hash_password(password),
            role=role,
        )
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"A user already uses {email}.",
        ) from exc
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def has_librarians() -> bool:
    db = SessionLocal()
    try:
        return user_repository.count_librarians(db) > 0
    finally:
        db.close()
