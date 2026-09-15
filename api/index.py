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

try:
    from zerotrust_x.web import app
except Exception:  # noqa: BLE001
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    err_traceback = traceback.format_exc()
    app = FastAPI(title="ZeroTrust-X Diagnostic")

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    def error_page(path: str = ""):  # noqa: ARG001
        return HTMLResponse(
            f"<h2>ZeroTrust-X Serverless Startup Error</h2>"
            f"<p>Failed to initialize application in serverless environment:</p>"
            f"<pre style='background:#1a1a24;color:#ff6b6b;padding:16px;border-radius:6px;font-size:13px;overflow-x:auto;'>{err_traceback}</pre>"
            f"<p>Working Dir: {Path.cwd()}</p>"
            f"<p>Root Dir: {ROOT_DIR}</p>"
            f"<p>Data Processed Exists: {(ROOT_DIR / 'data' / 'processed').exists()}</p>",
            status_code=500,
        )
