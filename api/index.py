import sys
from pathlib import Path

# Add project root and src to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from zerotrust_x.web import app  # noqa: E402

# Handler for Vercel serverless function
app = app
