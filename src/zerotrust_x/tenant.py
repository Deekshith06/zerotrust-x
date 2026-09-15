"""Tenant-aware request context; durable storage must enforce this boundary too."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    subject: str
    role: str


def require_same_tenant(context: TenantContext, resource_tenant_id: str) -> None:
    if context.tenant_id != resource_tenant_id:
        raise PermissionError("cross-tenant resource access denied")
