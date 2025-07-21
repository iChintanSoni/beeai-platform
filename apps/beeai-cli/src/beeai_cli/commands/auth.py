# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import webbrowser

from beeai_cli.api import api_request
from beeai_cli.async_typer import AsyncTyper, console
from beeai_cli.token_store import clear_token, save_token

app = AsyncTyper()

TOKEN_PATH = os.path.expanduser("~/.beeai_token")


@app.command("login")
async def cli_login():
    """
    Login to BeeAI using the default browser (OIDC flow).
    """
    login_resp = await api_request("POST", "login", params={"cli": "true"}, use_auth=False)
    login_url = login_resp["login_url"]
    login_id = login_resp["login_id"]

    console.print("Opening login URL in browser...")
    webbrowser.open(login_url)
    input("🔑 Press [Enter] once login is complete...")

    for _ in range(60):
        await asyncio.sleep(1)
        poll_resp = await api_request("GET", "cli/token", params={"login_id": login_id}, use_auth=False)
        if poll_resp and "token" in poll_resp:
            await save_token(poll_resp["token"])
            console.print("Login successful! Token saved.")
            return
    console.print("\n Login timed out or token not received")
    raise


@app.command("logout")
async def cli_logout():
    """
    Logout to BeeAI.
    """
    await clear_token()
    console.print("Logout successful!")
