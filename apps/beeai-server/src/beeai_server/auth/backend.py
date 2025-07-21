# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import UTC, datetime

from fastapi.responses import JSONResponse
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError

from beeai_server.auth.utils import decode_jwt_token, extract_token

from .models import AuthenticatedUser

logger = logging.getLogger(__name__)


no_token_paths = [
    "/api/v1/acp/ping",
    "/api/v1/auth",
    "/api/v1/login",
    "/api/v1/cli-complete",
    "/api/v1/cli/token",
    "/api/v1/docs",
    "/api/v1/openapi.json",
    "/api/v1/auth/callback",
]


class JwtAuthBackend(AuthenticationBackend):
    """
    Expects w3id, IBMiD, or ingestion Bearer token (JWT) in Authorization header.

    Any w3id | IBMiD, or ingestion user can be considered authenticated provided they supply a valid
    token in the authorization header.

    """

    def __init__(self) -> None:
        self.cit = datetime.now(UTC).timestamp()

    async def authenticate(self, conn):
        logger.debug("-->authenticate()")

        # Step 1: Allow unauthenticated access for exempt paths
        if conn.url.path in no_token_paths:
            return

        token = extract_token(conn)
        if not token:
            logger.error("Missing token in Authorization header and cookies.")
            return

        claims = decode_jwt_token(token)
        if claims:
            return AuthCredentials(["authenticated"]), AuthenticatedUser(
                claims.get("sub"), is_admin=False, display_name=claims.get("displayName"), email=claims.get("email")
            )

        raise AuthenticationError("JWT verification failed")


def on_auth_error(request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)
