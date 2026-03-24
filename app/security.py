# ruff: noqa: B008

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import ProjectMember, ProjectRole, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

READ_ROLES = {
    ProjectRole.OWNER.value,
    ProjectRole.MANAGER.value,
    ProjectRole.CONTRIBUTOR.value,
    ProjectRole.REVIEWER.value,
}
WRITE_ROLES = {
    ProjectRole.OWNER.value,
    ProjectRole.MANAGER.value,
    ProjectRole.CONTRIBUTOR.value,
}
DELETE_ROLES = {ProjectRole.OWNER.value, ProjectRole.MANAGER.value}
OWNER_ROLES = {ProjectRole.OWNER.value}


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt, digest = hashed_password.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        base64.b64decode(salt.encode("utf-8")),
        int(iterations),
    )
    return hmac.compare_digest(
        base64.b64encode(candidate).decode("utf-8"),
        digest,
    )


def get_password_hash(password: str) -> str:
    iterations = 100_000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.b64encode(salt).decode("utf-8"),
        base64.b64encode(digest).decode("utf-8"),
    )


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    payload = {"sub": subject, "type": token_type, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int) -> str:
    return _create_token(
        str(user_id),
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        str(user_id),
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> int:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_type = payload.get("type")
        subject = payload.get("sub")
        if token_type != expected_type or subject is None:
            raise ValueError
        return int(subject)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_token(token, "access")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


async def get_project_member_or_404(
    db: AsyncSession,
    user_id: int,
    project_id: int,
) -> ProjectMember:
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id_project == project_id,
            ProjectMember.id_user == user_id,
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project access denied",
        )
    return membership


async def require_project_roles(
    db: AsyncSession,
    user: User,
    project_id: int,
    allowed_roles: set[str],
) -> ProjectMember:
    membership = await get_project_member_or_404(db, user.id, project_id)
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient project permissions",
        )
    return membership
