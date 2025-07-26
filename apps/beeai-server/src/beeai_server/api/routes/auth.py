# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0
import logging

from fastapi import APIRouter, Query, Request

from beeai_server.api.dependencies import AuthServiceDependency, ConfigurationDependency

logger = logging.getLogger(__name__)

SLASH_LOGIN = "/login"

router = APIRouter()

pending_states: dict[str, dict] = {}
pending_tokens: dict[str, dict] = {}


@router.post("/login")
async def login(
    auth_service: AuthServiceDependency,
    request: Request,
    cli: bool = Query(default=False, description="Set to true if the login request is from a CLI tool"),
):
    return await auth_service.login(request=request, cli=cli, pending_states=pending_states)


@router.get("/auth/callback")
async def auth_callback(request: Request, configuration: ConfigurationDependency, auth_service: AuthServiceDependency):
    return await auth_service.handle_callback(request, pending_states, pending_tokens)


@router.get("/cli-complete")
async def cli_complete(auth_service: AuthServiceDependency):
    return await auth_service.render_cli_complete_page()


@router.get("/cli/token")
async def get_token(login_id: str, auth_service: AuthServiceDependency):
    return await auth_service.get_token_by_login_id(login_id, pending_tokens)
