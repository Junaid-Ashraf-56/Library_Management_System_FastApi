import os
from datetime import UTC, datetime, timedelta

import jwt

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"

def create_access_token(data: dict):
    payload = data.copy()
    payload['exp'] = datetime.now(UTC)+timedelta(minutes=30)
    return jwt.encode(payload,SECRET_KEY,algorithms=ALGORITHM)

def verify_tokens(token: str):
    try:
        return jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

