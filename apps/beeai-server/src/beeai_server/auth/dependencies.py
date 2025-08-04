# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyCookie, APIKeyHeader
from kink import di

from beeai_server.auth.utils import decode_jwt_token, extract_token
from beeai_server.configuration import Configuration

from .models import AuthenticatedUser

ConfigurationDependency = Annotated[Configuration, Depends(lambda: di[Configuration])]

api_key_cookie = APIKeyCookie(name="beeai-platform", auto_error=False)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
# api_key_header = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> AuthenticatedUser:
    user = request.user
    if not user or not user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def get_authenticated_user(
    configuration: ConfigurationDependency,
    cookie_token: Annotated[str | None, Security(api_key_cookie)],
    header_token: Annotated[str | None, Security(api_key_header)],
) -> AuthenticatedUser:
    if configuration.oidc.disable_oidc:
        # Bypass OIDC validation — return a default user for dev/testing mode
        return AuthenticatedUser(
            uid="dev-user",
            is_admin=True,
            display_name="dev user",
            email="user@beeai.dev",
        )
    try:
        token = extract_token(header_token, cookie_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Authorization header: {e}",
        ) from e
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    claims = decode_jwt_token(token)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    email = claims.get("email")
    is_admin = email in configuration.oidc.admin_emails

    return AuthenticatedUser(
        uid=claims.get("sub"),
        is_admin=is_admin,
        display_name=claims.get("displayName"),
        email=claims.get("email"),
    )


def check_admin(user: Annotated[AuthenticatedUser, Depends(get_authenticated_user)]) -> AuthenticatedUser:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


AuthenticatedUserDependency = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]
AdminUserDependency = Annotated[str, Depends(check_admin)]
