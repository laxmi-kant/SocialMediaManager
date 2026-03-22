"""Unit tests for security utilities (JWT, bcrypt, Fernet)."""

import uuid
from unittest.mock import patch

import jwt
import pytest

from app.utils.security import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_hash(self):
        hashed = hash_password("MySecurePass123")
        assert hashed != "MySecurePass123"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("MySecurePass123")
        assert verify_password("MySecurePass123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("MySecurePass123")
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("SamePass")
        h2 = hash_password("SamePass")
        assert h1 != h2  # different salts


class TestJWT:
    def test_create_access_token(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        user_id = uuid.uuid4()
        token = create_refresh_token(user_id)
        payload = decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_decode_invalid_token_raises(self):
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("invalid-token")

    def test_decode_expired_token_raises(self):
        user_id = uuid.uuid4()
        with patch("app.utils.security.settings") as mock_settings:
            mock_settings.secret_key = "test-key"
            mock_settings.access_token_expire_minutes = -1  # already expired
            token = create_access_token(user_id)

        with pytest.raises(jwt.InvalidTokenError):
            decode_token(token)

    def test_token_contains_exp_claim(self):
        user_id = uuid.uuid4()
        token = create_access_token(user_id)
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "exp" in payload


class TestFernetEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key().decode()
        with patch("app.utils.security._fernet", Fernet(test_key.encode())):
            from app.utils.security import decrypt_token, encrypt_token

            plaintext = "my-oauth-access-token"
            encrypted = encrypt_token(plaintext)
            assert encrypted != plaintext
            decrypted = decrypt_token(encrypted)
            assert decrypted == plaintext

    def test_encrypt_fails_without_key(self):
        with patch("app.utils.security._fernet", None):
            from app.utils.security import encrypt_token

            with pytest.raises(RuntimeError, match="ENCRYPTION_KEY not configured"):
                encrypt_token("test")
