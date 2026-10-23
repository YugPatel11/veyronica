"""Role-Based Access Control (RBAC).

Defines the permission matrix and provides FastAPI dependencies for
enforcing role-based access on endpoints.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import TokenPayload, TokenType, decode_token
from app.core.errors import ForbiddenError, UnauthorizedError

# ── Roles ────────────────────────────────────────────────────────────────────

class Role(StrEnum):
    ADMIN = "admin"
    FACULTY = "faculty"
    APPROVER = "approver"
    OPERATOR = "operator"


# ── Permissions ──────────────────────────────────────────────────────────────

class Permission(StrEnum):
    WORKFLOWS_RUN = "workflows.run"
    WORKFLOWS_MANAGE = "workflows.manage"
    APPROVALS_DECIDE = "approvals.decide"
    AUDIT_READ = "audit.read"
    AUDIT_VERIFY = "audit.verify"
    AUDIT_EXPORT = "audit.export"
    SETTINGS_MANAGE = "settings.manage"
    POLICIES_MANAGE = "policies.manage"
    BUDGETS_MANAGE = "budgets.manage"
    USERS_MANAGE = "users.manage"
    CONNECTORS_VIEW = "connectors.view"
    COPILOT_USE = "copilot.use"
    SECURITY_MANAGE = "security.manage"
    ANALYTICS_VIEW = "analytics.view"
    SANDBOX_MANAGE = "sandbox.manage"


# ── Role → Permission matrix ────────────────────────────────────────────────

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),  # Admin has all permissions
    Role.FACULTY: {
        Permission.WORKFLOWS_RUN,
        Permission.AUDIT_READ,
        Permission.CONNECTORS_VIEW,
        Permission.COPILOT_USE,
        Permission.ANALYTICS_VIEW,
    },
    Role.APPROVER: {
        Permission.APPROVALS_DECIDE,
        Permission.AUDIT_READ,
    },
    Role.OPERATOR: {
        Permission.AUDIT_READ,
        Permission.AUDIT_VERIFY,
        Permission.CONNECTORS_VIEW,
        Permission.SECURITY_MANAGE,
        Permission.ANALYTICS_VIEW,
        Permission.SANDBOX_MANAGE,
    },
}


def get_permissions_for_roles(roles: list[str]) -> set[Permission]:
    """Return the union of permissions for the given roles."""
    permissions: set[Permission] = set()
    for role_str in roles:
        try:
            role = Role(role_str)
        except ValueError:
            continue
        permissions |= ROLE_PERMISSIONS.get(role, set())
    return permissions


# ── FastAPI Dependencies ─────────────────────────────────────────────────────

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> TokenPayload:
    """Extract and validate the current user from the Bearer token.

    Raises UnauthorizedError if no token or token is invalid.
    """
    if credentials is None:
        raise UnauthorizedError("Missing authentication token")

    token_payload = decode_token(credentials.credentials, TokenType.ACCESS)

    # Store on request state for downstream use
    request.state.user_id = token_payload.sub
    request.state.user_roles = token_payload.roles

    return token_payload


CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def require_permissions(*required: Permission) -> Callable[..., Any]:
    """Return a dependency that checks the current user has all required permissions."""

    async def _check(user: CurrentUser) -> TokenPayload:
        user_permissions = get_permissions_for_roles(user.roles)
        missing = set(required) - user_permissions
        if missing:
            raise ForbiddenError(
                f"Missing permissions: {', '.join(p.value for p in missing)}"
            )
        return user

    return _check


def require_roles(*required: Role) -> Callable[..., Any]:
    """Return a dependency that checks the current user has at least one required role."""

    async def _check(user: CurrentUser) -> TokenPayload:
        user_roles = set(user.roles)
        if not user_roles & {r.value for r in required}:
            raise ForbiddenError(
                f"Requires one of: {', '.join(r.value for r in required)}"
            )
        return user

    return _check
