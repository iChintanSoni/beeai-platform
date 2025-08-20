# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import functools
import importlib.metadata
import pathlib
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pydantic
import pydantic_settings
from beeai_sdk.platform import PlatformClient, use_platform_client
from pydantic import HttpUrl, SecretStr


@functools.cache
def version():
    # Python strips '-', we need to re-insert it: 1.2.3rc1 -> 1.2.3-rc1
    return re.sub(r"([0-9])([a-z])", r"\1-\2", importlib.metadata.version("beeai-cli"))


@functools.cache
class Configuration(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=None, env_prefix="BEEAI__", env_nested_delimiter="__", extra="allow"
    )
    host: pydantic.AnyUrl = HttpUrl("http://localhost:8333")
    ui_url: pydantic.AnyUrl = HttpUrl("http://localhost:8334")
    playground: str = "playground"
    debug: bool = False
    home: pathlib.Path = pathlib.Path.home() / ".beeai"
    agent_registry: pydantic.AnyUrl = HttpUrl(
        f"https://github.com/i-am-bee/beeai-platform@v{version()}#path=agent-registry.yaml"
    )
    admin_password: SecretStr | None = None
    oidc_enabled: bool = False
    auth_token: SecretStr | None = None

    @property
    def lima_home(self) -> pathlib.Path:
        return self.home / "lima"

    @property
    def token_file(self) -> pathlib.Path:
        return self.home / "token.json"

    @property
    def load_auth_token(self) -> SecretStr | None:
        if self.auth_token:
            return self.auth_token

        if self.token_file.exists():
            token = self.token_file.read_text().strip()
            if token:
                self.auth_token = SecretStr(token)
                return self.auth_token
        return None

    def set_auth_token(self, token: str):
        """Persist and cache auth token (after login)."""
        self.home.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(token)
        self.auth_token = SecretStr(token)
        print(f"here----------------{self.auth_token}")

    def clear_auth_token(self):
        """Remove persisted token and clear from memory."""
        self.auth_token = None
        if self.token_file.exists():
            self.token_file.unlink()

    @asynccontextmanager
    async def use_platform_client(self) -> AsyncIterator[PlatformClient]:
        auth = ("admin", self.admin_password.get_secret_value()) if self.admin_password else None
        auth_token = self.load_auth_token.get_secret_value() if self.load_auth_token else None
        async with use_platform_client(auth=auth, auth_token=auth_token, base_url=str(self.host), timeout=30) as client:
            yield client
