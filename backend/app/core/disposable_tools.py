"""Explicitly guard historical seed/reset utilities, never application startup."""
import os
from urllib.parse import urlparse


def require_disposable_database() -> None:
    name = urlparse(os.environ.get("DATABASE_URL", "")).path.lstrip("/")
    if os.environ.get("ALLOW_DISPOSABLE_DB_TOOLS") != "1" or not name.startswith("neurolearn_test"):
        raise SystemExit("This utility requires ALLOW_DISPOSABLE_DB_TOOLS=1 and an explicit DATABASE_URL named neurolearn_test*. Never use learner data.")
