"""Local compatibility role access controls; replace with OIDC in deployment."""
from __future__ import annotations

from enum import StrEnum

from fastapi import Header, HTTPException

from zerotrust_x.tenant import TenantContext


class Role(StrEnum):
    EMPLOYEE = "EMPLOYEE"
    SOC_ANALYST = "SOC_ANALYST"
    SOC_ADMIN = "SOC_ADMIN"


_DEMO_TOKENS = {
    "employee-demo": (Role.EMPLOYEE, "EMP10001"),
    "analyst-demo": (Role.SOC_ANALYST, None),
    "admin-demo": (Role.SOC_ADMIN, None),
}


def identity(x_demo_token: str | None = Header(default=None)) -> tuple[Role, str | None]:
    if x_demo_token not in _DEMO_TOKENS:
        raise HTTPException(status_code=401, detail="Valid local authentication adapter token required")
    return _DEMO_TOKENS[x_demo_token]


def require_role(*roles: Role):
    def dependency(x_demo_token: str | None = Header(default=None)) -> tuple[Role, str | None]:
        current = identity(x_demo_token)
        if current[0] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return current
    return dependency


def tenant_context(actor: tuple[Role, str | None], tenant_id: str) -> TenantContext:
    return TenantContext(tenant_id=tenant_id, subject=actor[1] or actor[0].value, role=actor[0].value)


def can_read_user(actor: tuple[Role, str | None], user_id: str) -> bool:
    return actor[0] in {Role.SOC_ANALYST, Role.SOC_ADMIN} or actor[1] == user_id
