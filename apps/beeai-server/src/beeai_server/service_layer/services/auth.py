# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import logging
import uuid

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from kink import inject

from beeai_server.configuration import Configuration

logger = logging.getLogger(__name__)

SLASH_LOGIN = "/login"


@inject
class AuthService:
    def __init__(self, configuration: Configuration):
        self._config = configuration
        self._oauth = self._build_oauth()

    def _build_oauth(self) -> OAuth | None:
        if self._config.oidc.disable_oidc:
            return None
        oauth = OAuth()
        oauth.register(
            name="auth_provider",
            client_id=self._config.oidc.client_id,
            client_secret=self._config.oidc.client_secret._secret_value,
            server_metadata_url=str(self._config.oidc.discovery_url),
            jwks_url=str(self._config.oidc.jwks_url),
            client_kwargs={"scope": "openid email profile"},
        )
        return oauth

    async def login(
        self, request: Request, cli: bool, pending_states: dict[str, dict]
    ) -> JSONResponse | RedirectResponse:
        if self._oauth is None:
            return {"login_url": None, "login_id": "dev", "dev_token": "beeai-dev-token"}

        login_id = str(uuid.uuid4())
        redirect_uri = str(request.url_for("auth_callback"))

        # CLI logic to handle login
        if cli:
            response = await self._oauth.auth_provider.authorize_redirect(request, redirect_uri, state=login_id)
            state_key = f"_state_auth_provider_{login_id}"
            auth_state_dict = request.session.get(state_key)
            pending_states[login_id] = {"login_id": login_id, "auth_state": auth_state_dict}
            return JSONResponse({"login_url": response.headers.get("location"), "login_id": login_id})
        # UI logic to handle login
        request.session["is_cli"] = False
        request.session["login_id"] = login_id
        return await self._oauth.auth_provider.authorize_redirect(request, redirect_uri)

    async def handle_callback(self, request: Request, pending_states: dict[str, dict], pending_tokens: dict[str, dict]):
        if self._oauth is None:
            raise HTTPException(status_code=503, detail="OIDC disabled in configuration")

        state = request.query_params.get("state")
        login_id = None

        if state and state in pending_states:
            stored_state = pending_states.pop(state)
            login_id = stored_state["login_id"]
            state_key = f"_state_auth_provider_{login_id}"
            request.session[state_key] = stored_state["auth_state"]
            is_cli = True

        try:
            token = await self._oauth.auth_provider.authorize_access_token(request)
        except Exception as e:
            logger.debug("Error running authorize_access_token %s", str(e))
            return RedirectResponse(SLASH_LOGIN)

        if login_id and token:
            pending_tokens[login_id] = token

        response = RedirectResponse("/api/v1/cli-complete" if is_cli else "/")
        if is_cli:
            response.set_cookie("token", token, secure=True, samesite="strict")
        else:
            response.set_cookie("beeai-platform", token, httponly=True, secure=True, samesite="strict")
        return response

    async def render_cli_complete_page(self) -> HTMLResponse:
        return HTMLResponse("""
            <html><body>
            <h3>Login Successful</h3>
            <script>
                const token = document.cookie.split('; ').find(row => row.startsWith('token=')).split('=')[1];
                fetch('/api/v1/auth/poll', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token })
                });
            </script>
            You can close this window.
            </body></html>
        """)

    async def get_token_by_login_id(self, login_id: str, pending_tokens: dict) -> JSONResponse:
        if login_id == "dev":
            return JSONResponse(status_code=200, content={"token": "beeai-dev-token"})
        token = pending_tokens.pop(login_id, None)
        if token:
            return JSONResponse(status_code=200, content={"token": token})
        raise HTTPException(status_code=404, detail="Token not found or expired")
