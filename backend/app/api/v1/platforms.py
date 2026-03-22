"""Platform OAuth and account management endpoints."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.platform_account import PlatformAccount
from app.models.user import User
from app.schemas.platform import PlatformAccountResponse, PlatformListResponse
from app.utils.cache import get_redis
from app.utils.security import decrypt_token, encrypt_token

logger = structlog.get_logger()

router = APIRouter(prefix="/platforms", tags=["platforms"])


# --- Helper: OAuth state management via Redis ---


async def _store_oauth_state(user_id: uuid.UUID, platform: str, code_verifier: str) -> str:
    """Generate and store OAuth state in Redis. Returns state token."""
    state = secrets.token_urlsafe(32)
    cache = get_redis()
    await cache.set(
        f"oauth:state:{state}",
        {"user_id": str(user_id), "platform": platform, "code_verifier": code_verifier},
        ttl=600,
    )
    return state


async def _verify_oauth_state(state: str) -> dict | None:
    """Verify and consume OAuth state from Redis."""
    cache = get_redis()
    data = await cache.get(f"oauth:state:{state}")
    if data:
        await cache.delete(f"oauth:state:{state}")
    return data


# --- List connected platforms ---


@router.get("", response_model=PlatformListResponse)
async def list_platforms(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id)
    )
    accounts = result.scalars().all()
    return PlatformListResponse(
        platforms=[PlatformAccountResponse.model_validate(a) for a in accounts]
    )


# --- Disconnect platform ---


@router.delete("/{platform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_platform(
    platform_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        uid = uuid.UUID(platform_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform ID")

    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.id == uid,
            PlatformAccount.user_id == user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Platform account not found")

    await db.delete(account)
    logger.info("platform_disconnected", platform=account.platform, user_id=str(user.id))


# ============================================================
# TWITTER OAuth 2.0 with PKCE
# ============================================================


@router.get("/twitter/authorize")
async def twitter_authorize(
    request: Request,
    user: User = Depends(get_current_user),
):
    """Initiate Twitter OAuth 2.0 PKCE flow."""
    if not settings.twitter_client_id:
        raise HTTPException(status_code=400, detail="Twitter OAuth not configured")

    # Generate PKCE code verifier and challenge
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        hashlib.sha256(code_verifier.encode()).digest()
        # Base64url encode
    )
    import base64
    code_challenge_b64 = base64.urlsafe_b64encode(code_challenge).rstrip(b"=").decode()

    state = await _store_oauth_state(user.id, "twitter", code_verifier)

    params = {
        "response_type": "code",
        "client_id": settings.twitter_client_id,
        "redirect_uri": settings.twitter_callback_url,
        "scope": "tweet.read tweet.write users.read offline.access",
        "state": state,
        "code_challenge": code_challenge_b64,
        "code_challenge_method": "S256",
    }
    auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/twitter/callback")
async def twitter_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle Twitter OAuth callback."""
    # Verify state
    state_data = await _verify_oauth_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    user_id = uuid.UUID(state_data["user_id"])
    code_verifier = state_data["code_verifier"]

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.twitter_callback_url,
                "code_verifier": code_verifier,
                "client_id": settings.twitter_client_id,
            },
            auth=(settings.twitter_client_id, settings.twitter_client_secret),
        )
        if token_resp.status_code != 200:
            logger.error("twitter_token_exchange_failed", status=token_resp.status_code, body=token_resp.text)
            return RedirectResponse(url=f"{settings.frontend_url}/settings?error=twitter_auth_failed")

        tokens = token_resp.json()
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 7200)

        # Fetch user info
        user_resp = await client.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_resp.json().get("data", {})

    # Store or update platform account
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user_id,
            PlatformAccount.platform == "twitter",
        )
    )
    account = result.scalar_one_or_none()

    if account:
        account.access_token = encrypt_token(access_token)
        account.refresh_token = encrypt_token(refresh_token) if refresh_token else None
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        account.platform_user_id = user_data.get("id", "")
        account.display_name = f"@{user_data.get('username', '')}"
        account.is_active = True
    else:
        account = PlatformAccount(
            user_id=user_id,
            platform="twitter",
            platform_user_id=user_data.get("id", ""),
            display_name=f"@{user_data.get('username', '')}",
            access_token=encrypt_token(access_token),
            refresh_token=encrypt_token(refresh_token) if refresh_token else None,
            token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            scopes=["tweet.read", "tweet.write", "users.read", "offline.access"],
            is_active=True,
        )
        db.add(account)

    await db.flush()
    logger.info("twitter_connected", user_id=str(user_id), twitter_user=user_data.get("username"))
    return RedirectResponse(url=f"{settings.frontend_url}/settings?connected=twitter")


# ============================================================
# LINKEDIN OAuth 2.0
# ============================================================


@router.get("/linkedin/authorize")
async def linkedin_authorize(
    request: Request,
    user: User = Depends(get_current_user),
):
    """Initiate LinkedIn OAuth 2.0 flow."""
    if not settings.linkedin_client_id:
        raise HTTPException(status_code=400, detail="LinkedIn OAuth not configured")

    state = await _store_oauth_state(user.id, "linkedin", "")

    params = {
        "response_type": "code",
        "client_id": settings.linkedin_client_id,
        "redirect_uri": settings.linkedin_callback_url,
        "scope": "openid profile email w_member_social",
        "state": state,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/linkedin/callback")
async def linkedin_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle LinkedIn OAuth callback."""
    state_data = await _verify_oauth_state(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    user_id = uuid.UUID(state_data["user_id"])

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.linkedin_callback_url,
                "client_id": settings.linkedin_client_id,
                "client_secret": settings.linkedin_client_secret,
            },
        )
        if token_resp.status_code != 200:
            logger.error("linkedin_token_exchange_failed", status=token_resp.status_code, body=token_resp.text)
            return RedirectResponse(url=f"{settings.frontend_url}/settings?error=linkedin_auth_failed")

        tokens = token_resp.json()
        access_token = tokens["access_token"]
        expires_in = tokens.get("expires_in", 5184000)  # 60 days default
        refresh_token = tokens.get("refresh_token")

        # Fetch user profile
        profile_resp = await client.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_data = profile_resp.json() if profile_resp.status_code == 200 else {}

    # LinkedIn member ID from sub claim
    member_id = profile_data.get("sub", "")
    display_name = profile_data.get("name", "")

    # Store or update
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user_id,
            PlatformAccount.platform == "linkedin",
        )
    )
    account = result.scalar_one_or_none()

    if account:
        account.access_token = encrypt_token(access_token)
        account.refresh_token = encrypt_token(refresh_token) if refresh_token else None
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        account.platform_user_id = member_id
        account.display_name = display_name
        account.is_active = True
    else:
        account = PlatformAccount(
            user_id=user_id,
            platform="linkedin",
            platform_user_id=member_id,
            display_name=display_name,
            access_token=encrypt_token(access_token),
            refresh_token=encrypt_token(refresh_token) if refresh_token else None,
            token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            scopes=["openid", "profile", "email", "w_member_social"],
            is_active=True,
        )
        db.add(account)

    await db.flush()
    logger.info("linkedin_connected", user_id=str(user_id), member_id=member_id)
    return RedirectResponse(url=f"{settings.frontend_url}/settings?connected=linkedin")
