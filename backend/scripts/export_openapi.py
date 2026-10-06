"""Deterministic contract export; no provider calls, database access or secrets."""
import json
import os
from pathlib import Path
import secrets
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["INTERNAL_API_KEY"] = secrets.token_urlsafe(32)
os.environ["SECRET_KEY"] = secrets.token_urlsafe(32)
from app.main import app  # noqa: E402

expected = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
path = root / "openapi.json"
if "--check" in sys.argv:
    if not path.is_file() or path.read_text() != expected:
        raise SystemExit("OpenAPI snapshot is stale; run contracts:generate")
else:
    path.write_text(expected)
