"""Security utilities: password hashing, JWT tokens, Fernet encryption."""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.fernet import Fernet

from app.config import settings

# --- Password Hashing (bcrypt) ---


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# --- JWT Tokens ---

ALGORITHM = "HS256"


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises jwt.InvalidTokenError on failure."""
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])


# --- Fernet Encryption (for OAuth tokens) ---

_fernet = Fernet(settings.encryption_key.encode()) if settings.encryption_key != "change-me-to-a-fernet-key" else None


def encrypt_token(plaintext: str) -> str:
    if _fernet is None:
        raise RuntimeError("ENCRYPTION_KEY not configured")
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    if _fernet is None:
        raise RuntimeError("ENCRYPTION_KEY not configured")
    return _fernet.decrypt(ciphertext.encode()).decode()
