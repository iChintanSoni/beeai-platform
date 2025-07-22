# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import fastapi
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.datastructures import URL
from starlette.responses import RedirectResponse

logger = logging.getLogger(__name__)

config = Config(".env")
oauth = OAuth(config)
SLASH_LOGIN = "/login"
DISCOVERY_ENDPOINT = os.environ.get("DISCOVERY_ENDPOINT")
oauth.register(name="ibm", server_metadata_url=DISCOVERY_ENDPOINT, client_kwargs={"scope": "openid email profile"})


router = fastapi.APIRouter()


async def auth_success(token, is_cli):
    """Sets a cookie which the receiver can pull from the page"""
    response = RedirectResponse("/")
    response.set_cookie(key="beeai-platform", value=token["id_token"], samesite="strict", secure=True, httponly=True)
    if is_cli:
        response.set_cookie("token", token["id_token"], samesite="strict", secure=True)
    return response


@router.api_route("/login", methods=["GET"], tags=["auth"])
async def login(request: fastapi.requests.Request):
    """
    Invoke the oidc flow
    prepend https instead of http as we're running under istio in ambient mode
    """
    redirect_uri = request.url_for("auth")
    new_redirect_url = URL(scheme="https", netloc=redirect_uri.netloc, path=redirect_uri.path)
    return await oauth.ibm.authorize_redirect(request, new_redirect_url)


@router.api_route("/cli_login", methods=["GET"], tags=["auth"])
async def cli_login(request: fastapi.requests.Request):
    """
    Invoke the oidc flow
    """
    redirect_uri = request.url_for("auth_cli")
    new_redirect_url = URL(scheme="https", netloc=redirect_uri.netloc, path=redirect_uri.path)
    return await oauth.ibm.authorize_redirect(request, new_redirect_url)


@router.api_route("/auth", methods=["GET"], tags=["auth"])
async def auth(request: fastapi.requests.Request):
    """
    request a token from the oidc endpoint
    using UX routes
    """
    logger.debug("--> auth")
    token = ""
    try:
        token = await oauth.ibm.authorize_access_token(request)
    except Exception as err:
        logger.debug("Error running authorize_access_token %s", str(err))
        return RedirectResponse(SLASH_LOGIN)
    return await auth_success(token, False)


@router.api_route("/auth_cli", methods=["GET"], tags=["auth"])
async def auth_cli(request: fastapi.requests.Request):
    """
    request a token from the oidc endpoint
    using UX routes
    """
    logger.debug("--> auth")
    token = ""
    try:
        token = await oauth.ibm.authorize_access_token(request)
    except Exception as err:
        logger.debug("Error running authorize_access_token %s", str(err))
        return RedirectResponse(SLASH_LOGIN)
    return await auth_success(token, True)
