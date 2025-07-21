# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0
import logging
import uuid

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.responses import RedirectResponse

from beeai_server.api.dependencies import ConfigurationDependency

logger = logging.getLogger(__name__)

SLASH_LOGIN = "/login"

router = APIRouter()


def build_oauth(configuration: ConfigurationDependency):
    if configuration.oidc.disable_oidc:
        return

    oauth = OAuth()
    oauth.register(
        name="oidc_auth_provider",
        client_id=configuration.oidc.client_id,
        client_secret=configuration.oidc.client_secret._secret_value,
        server_metadata_url=str(configuration.oidc.discovery_url),
        jwks_url=str(configuration.oidc.jwks_url),
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


pending_states: dict[str, dict] = {}
pending_tokens: dict[str, str] = {}


@router.post("/login")
async def login(
    request: Request,
    configuration: ConfigurationDependency,
    cli: bool = Query(default=False, description="Set to true if the login request is from a CLI tool"),
):
    oauth = build_oauth(configuration=configuration)
    if oauth is None:
        return {"login_url": None, "login_id": "dev", "dev_token": "beeai-dev-token"}

    login_id = str(uuid.uuid4())
    redirect_uri = str(request.url_for("auth_callback"))

    if cli:
        # Inject state manually in redirect URL, using login_id as state
        response = await oauth.oidc_auth_provider.authorize_redirect(request, redirect_uri, state=login_id)
        authorization_url = response.headers.get("location")
        key = f"_state_oidc_auth_provider_{login_id}"
        oidc_state_dict = request.session.get(key)
        pending_states[login_id] = {
            "login_id": login_id,
            "oidc_state": oidc_state_dict,
        }
        return JSONResponse({"login_url": str(authorization_url), "login_id": login_id})

    # UI clients - use session (cookie-backed)
    request.session["is_cli"] = False
    request.session["login_id"] = login_id
    return await oauth.oidc_auth_provider.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request, configuration: ConfigurationDependency):
    oauth = build_oauth(configuration)
    if oauth is None:
        raise HTTPException(status_code=503, detail="OIDC disabled in configuration")

    state = request.query_params.get("state")
    login_id = None

    if state and state in pending_states:
        stored_state = pending_states.pop(state)
        login_id = stored_state["login_id"]
        key = f"_state_oidc_auth_provider_{state}"
        request.session[key] = stored_state["oidc_state"]
        is_cli = True
    else:
        login_id = request.session.get("login_id")
        is_cli = request.session.get("is_cli", False)

    try:
        token = await oauth.oidc_auth_provider.authorize_access_token(request)
    except Exception as err:
        logger.debug("Error running authorize_access_token %s", str(err))
        return RedirectResponse(SLASH_LOGIN)

    id_token = token.get("id_token")

    if login_id and id_token:
        pending_tokens[login_id] = id_token

    response = RedirectResponse("/api/v1/cli-complete" if is_cli else "/")
    if is_cli:
        response.set_cookie("token", token, secure=True, samesite="strict")
    else:
        response.set_cookie("beeai-platform", token, httponly=True, secure=True, samesite="strict")

    return response


@router.get("/cli-complete")
async def cli_complete():
    return HTMLResponse("""
        <html><body>
        <h3>Login Successful</h3>
        <script>
            const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];
            fetch('/auth/poll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token })
            });
        </script>
        You can close this window.
        </body></html>
    """)


@router.get("/cli/token")
async def get_token(login_id: str):
    if login_id == "dev":
        return JSONResponse(status_code=200, content={"token": "beeai-dev-token"})
    token = pending_tokens.pop(login_id, None)
    if token:
        return JSONResponse(status_code=200, content={"token": token})
    raise HTTPException(status_code=404, detail="Token not found or expired")
