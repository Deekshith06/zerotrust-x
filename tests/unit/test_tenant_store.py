from pathlib import Path

import pytest

from zerotrust_x.tenant import TenantContext
from zerotrust_x.tenant_store import TenantRecord, TenantStore


def test_tenant_store_scopes_reads_and_writes(tmp_path: Path):
    store = TenantStore(tmp_path / "tenant.sqlite")
    tenant_a = TenantContext("TENANT_A", "analyst-a", "SOC_ANALYST")
    tenant_b = TenantContext("TENANT_B", "analyst-b", "SOC_ANALYST")
    store.put(tenant_a, TenantRecord("TENANT_A", "user", "EMP1", {"risk": 10}))
    store.put(tenant_b, TenantRecord("TENANT_B", "user", "EMP1", {"risk": 90}))

    assert store.get(tenant_a, "user", "EMP1").payload == {"risk": 10}
    assert store.get(tenant_b, "user", "EMP1").payload == {"risk": 90}
    assert [item.payload for item in store.list(tenant_a, "user")] == [{"risk": 10}]


def test_tenant_store_rejects_cross_tenant_write(tmp_path: Path):
    store = TenantStore(tmp_path / "tenant.sqlite")
    context = TenantContext("TENANT_A", "analyst-a", "SOC_ANALYST")
    with pytest.raises(PermissionError):
        store.put(context, TenantRecord("TENANT_B", "user", "EMP1", {}))
