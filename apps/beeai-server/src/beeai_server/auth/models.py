# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

"""
User object with admin attribute controlled by bluegroup membership.

"""


class AuthenticatedUser:
    def __init__(self, uid: str, is_admin: bool, display_name: str, email: str) -> None:
        self.username = uid
        self.emailAddress = email
        self.admin = is_admin
        self.rname = display_name

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.rname

    @property
    def email(self) -> str:
        return self.emailAddress

    @property
    def uid(self) -> str:
        return self.username

    @property
    def is_admin(self) -> bool:
        return self.admin
