# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import base64
import hashlib
import json
import secrets
import time
import webbrowser
from urllib.parse import urlencode

import anyio
import httpx
import uvicorn
from fastapi import FastAPI, Request

from beeai_cli.async_typer import AsyncTyper, console
from beeai_cli.configuration import Configuration

app = AsyncTyper()

config = Configuration()


async def get_resource_metadata(resource_url: str, force_refresh=False):
    if not force_refresh and config.resource_metadata_file.exists():
        data = json.loads(config.resource_metadata_file.read_text())
        if data.get("expiry", 0) > time.time():
            return data["metadata"]

    url = f"{resource_url}/.well-known/oauth-protected-resource"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        metadata = resp.json()

    payload = {"metadata": metadata, "expiry": config.resource_metadata_ttl}
    config.resource_metadata_file.write_text(json.dumps(payload, indent=2))
    return metadata


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode()
    return code_verifier, code_challenge


@app.command("login")
async def cli_login():
    # metadata = await get_resource_metadata(resource_url=resource_url)

    # as_config = metadata["authorization_servers"][0]
    # issuer = as_config["issuer"]

    issuer = "https://sox.verify.ibm.com/oidc/endpoint/default"

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{issuer}/.well-known/openid-configuration")
        oidc = resp.json()

    client_id = "48eb31b8-fd49-438e-b23f-e62387647a9d"  # pre-registered with AS
    redirect_uri = "http://localhost:9001/callback"
    scope = "openid profile email"

    code_verifier, code_challenge = generate_pkce_pair()

    auth_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{oidc['authorization_endpoint']}?{urlencode(auth_params)}"

    console.print(f"[INFO] Opening browser for login: {auth_url}")
    webbrowser.open(auth_url)

    # Start local FastAPI server to handle redirect
    app = FastAPI()
    result = {}
    got_code = anyio.Event()

    @app.get("/callback")
    async def callback(request: Request):
        query = dict(request.query_params)
        result.update(query)
        got_code.set()
        return {"message": "Login successful! You can close this tab."}

    server_config = uvicorn.Config(app, host="127.0.0.1", port=9001, log_level="error")
    server = uvicorn.Server(config=server_config)

    async def run_server():
        await server.serve()

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_server)

        # Wait for the event instead of busy-wait
        await got_code.wait()

        server.should_exit = True

    code = result["code"]

    token_req = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(oidc["token_endpoint"], data=token_req)
        token_resp.raise_for_status()
        tokens = token_resp.json()

    if tokens:
        config.set_auth_token(tokens)
        console.print("\n[bold green]Ok! Login successful.[/bold green]")
        return

    console.print("\n [bold red] Login timed out or not successful. [/bold red] ")
    raise RuntimeError("Login failed.")


@app.command("logout")
async def logout():
    config.clear_auth_token()
    if (
        config.resource_metadata_file.exists()
        and json.loads(config.resource_metadata_file.read_text()).get("expiry", 0) <= time.time()
    ):
        config.resource_metadata_file.unlink()
    console.print("\n[bold yellow]You have been logged out.[/bold yellow]")
