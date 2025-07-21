# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
from datetime import UTC, datetime

import jwt
import requests
from fastapi.responses import JSONResponse
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError

from beeai_server.api.dependencies import ConfigurationDependency
from beeai_server.configuration import get_configuration

from .models import AuthenticatedUser

logger = logging.getLogger(__name__)

configuration: ConfigurationDependency = get_configuration()

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


# Initialize JWKS only if OIDC is enabled
if not configuration.oidc.disable_oidc:
    AUDIENCE = configuration.oidc.client_id
    JWKS_URL = configuration.oidc.jwks_url
    JWKS_FOLDER = "./jwks"
    JWKS_FILE = os.path.join(JWKS_FOLDER, "pubkeys.json")

    os.makedirs(JWKS_FOLDER, exist_ok=True)

    try:
        response = requests.get(JWKS_URL)
        response.raise_for_status()
        with open(JWKS_FILE, "w") as f:
            json.dump(response.json(), f, indent=2)
        print(f"JWKS downloaded and saved to: {JWKS_FILE}")
    except Exception as e:
        logger.error("Failed to fetch JWKS: %s", e)
        raise

    def get_jwks_dict():
        with open(JWKS_FILE) as key_file:
            return json.load(key_file)

    jwks_dict = get_jwks_dict()
else:
    jwks_dict = None
    AUDIENCE = None


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

        token = None

        # Step 2: Try Authorization header (CLI)
        auth_header = conn.headers.get("Authorization")
        if auth_header:
            try:
                scheme, credentials = auth_header.split()
                if scheme.lower() == "bearer":
                    token = credentials
                else:
                    return
            except ValueError:
                logger.warning("Invalid Authorization header format")

        # Step 3: Fall back to cookie if no token in header
        if not token:
            token = conn.cookies.get("beeai-platform")

        # Step 4: Require token if not exempt
        if not token:
            logger.error("Missing token in Authorization header and cookies.")
            return

        # Step 5: Try JWKS public keys
        for pub_key in jwks_dict["keys"]:
            try:
                obj_key = jwt.PyJWK(pub_key)
                # explicitly only check exp and iat, nbf (not before time) is not included in w3id
                claims = jwt.decode(token, obj_key, ["RS256"], None, True, audience=AUDIENCE)
                logger.debug("Verified token claims: %s", json.dumps(claims))
                is_admin = False
                return AuthCredentials(["authenticated"]), AuthenticatedUser(
                    claims["sub"], is_admin, claims["displayName"], claims["email"]
                )
            except Exception as err:
                if "expired" in str(err):
                    logger.error("Expired token: %s", err)
                continue
        # if execution reaches here, the JWT failed to verify against any of the supplied keys (OR, the verified user is not in the bluegroup)
        logger.info("iterated over all available keys and jwt verification failed.")
        raise AuthenticationError("JWT verification failed")


def on_auth_error(request, exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)
