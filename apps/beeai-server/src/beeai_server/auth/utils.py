# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import json
import logging

import jwt
import requests
from fastapi.security import HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWK

from beeai_server.configuration import Configuration

logger = logging.getLogger(__name__)


type JWKS = dict | None


def setup_jwks(config: Configuration) -> JWKS:
    if config.oidc.disable_oidc:
        return None
    try:
        response = requests.get(config.oidc.jwks_url)
        response.raise_for_status()
        jwks_dict = response.json()
        return jwks_dict
    except Exception as e:
        logger.error("Failed to fetch JWKS: %s", e)
        raise


def extract_token(
    header_token: str | HTTPAuthorizationCredentials,
    cookie_token: str | None,
) -> str | None:
    if isinstance(header_token, HTTPAuthorizationCredentials):
        return header_token.credentials

    if header_token:
        try:
            scheme, credentials = header_token.split()
            if scheme.lower() == "bearer":
                return credentials
            raise Exception("Unsupported auth scheme - Bearer is only valid scheme")
        except ValueError as err:
            logger.warning("Invalid Authorization header format")
            raise Exception("Invalid Authorization header format") from err

    # Fall back to cookie if no token in header
    return cookie_token


def decode_jwt_token(token: str, jwks: dict | None = None, aud: str | None = None) -> dict | None:
    jwks = jwks
    aud = aud
    # Decode JWT using keys from JWKS
    for pub_key in jwks.get("keys", []):
        try:
            obj_key = PyJWK(pub_key)
            # explicitly only check exp and iat, nbf (not before time) is not included in w3id
            claims = jwt.decode(token, obj_key, algorithms=["RS256"], options=None, verify=True, audience=aud)
            logger.debug("Verified token claims: %s", json.dumps(claims))
            return claims
        except ExpiredSignatureError as err:
            logger.error("Expired token: %s", err)
        except InvalidTokenError as err:
            logger.debug("Token verification failed: %s", err)
            continue

    logger.info("All JWT verifications failed.")
    return None
