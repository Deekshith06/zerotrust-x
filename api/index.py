import os
import sys
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    os.chdir(ROOT_DIR)
except Exception:
    pass

# Configure serverless defaults: writable /tmp for audit log and absolute artifact paths
os.environ.setdefault("ZEROTRUST_ENV", "demo")
os.environ.setdefault("ZEROTRUST_AUDIT_PATH", "/tmp/audit-chain.jsonl")
os.environ.setdefault("ZEROTRUST_PROCESSED_DIR", str(ROOT_DIR / "data" / "processed"))
os.environ.setdefault("ZEROTRUST_QUARANTINE_DIR", str(ROOT_DIR / "data" / "quarantine"))

from zerotrust_x.web import app as _app

app = _app
