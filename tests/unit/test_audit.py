import json
from pathlib import Path

from zerotrust_x.audit import LocalAuditSink, verify_audit_chain


def test_local_audit_chain_detects_tampering(tmp_path: Path):
    path = tmp_path / "audit.jsonl"
    sink = LocalAuditSink(path)
    sink.append("analyst", "investigate", "EMP1", "success")
    sink.append("analyst", "read_timeline", "EMP1", "success")
    assert verify_audit_chain(path) == (True, None)

    rows = path.read_text(encoding="utf-8").splitlines()
    record = json.loads(rows[0])
    record["actor"] = "attacker"
    path.write_text(json.dumps(record) + "\n" + rows[1] + "\n", encoding="utf-8")
    valid, reason = verify_audit_chain(path)
    assert not valid
    assert reason == "line 1: current hash mismatch"
