# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

from fastapi import HTTPException, Request

from .models import AuthenticatedUser


async def get_current_user(request: Request) -> AuthenticatedUser:
    user = request.user
    if not user or not user.is_authenticated:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
