from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator

# Values that shipped as defaults in earlier revisions of this file. They are
# public knowledge (they are in the git history), so a deployment that sets one
# of them is no better off than a deployment that sets nothing.
_KNOWN_INSECURE = {
    "dev_secret_key_123",
    "CHANGE_ME_TO_A_RANDOM_SECRET_KEY",
    "changeme",
    "secret",
}


class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend Service"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/neuro_db"

    # INTERNAL AUTH — shared secret proving a request came from the Next.js
    # server rather than the browser. Required: no default, because a default
    # here fails open.
    INTERNAL_API_KEY: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"

    # Groq (legacy chat path)
    GROQ_API_KEY: str = ""
    # Model id is a setting, not a literal at the call site. Providers retire
    # models without notice — llama-3.3-70b-versatile was removed and every
    # chat request began returning 404 — and a retirement should be a config
    # change, not a code edit in two places.
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Gemini — generation, multimodal and embeddings.
    # Model ids are explicit settings, not literals at the call site, so a
    # model change is configuration rather than a code edit.
    GEMINI_API_KEY: str = ""
    # gemini-2.5-flash-lite (AGENTS.md §5's frozen choice) was retired for
    # new callers as of this verification -- confirmed live 2026-08-29, the
    # API itself names gemini-3.5-flash-lite as the replacement. Same class
    # of failure as the Groq model retirement (K-12): kept as a setting, not
    # a literal, so the next retirement is a config change.
    GEMINI_GENERATION_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    # Bounded provider calls keep a stalled upstream request from holding a
    # durable processing stage indefinitely. This is an unvalidated V1
    # operational default and can be tuned through deployment configuration.
    GEMINI_GENERATION_TIMEOUT_SECONDS_V1: int = 45
    # One corrected re-prompt is allowed for malformed structured extraction
    # output; a second malformed result abstains rather than inventing data.
    CONCEPT_EXTRACTION_MAX_GENERATION_ATTEMPTS_V1: int = 2

    # Worker / queue. Redis is local in Compose and Upstash-compatible in
    # production. Task dispatch is intentionally separate from request work.
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Indexed in bounded batches. These versioned values are unvalidated
    # defaults until the benchmark suite records representative measurements.
    INDEXING_BATCH_SIZE_V1: int = 10
    INDEXING_WORKER_CONCURRENCY_V1: int = 2

    # Private S3-compatible storage (Supabase Storage production endpoint).
    STORAGE_BUCKET: str = "neurolearn-sources"
    STORAGE_S3_ENDPOINT: str = ""
    STORAGE_S3_ACCESS_KEY: str = ""
    STORAGE_S3_SECRET_KEY: str = ""
    STORAGE_SIGNED_URL_TTL_SECONDS_V1: int = 900

    @field_validator("INTERNAL_API_KEY", "SECRET_KEY")
    @classmethod
    def _reject_weak_secret(cls, v: str, info) -> str:
        """
        Fail at startup rather than serve requests with a guessable secret.

        A short or publicly-known value is worse than a missing one, because a
        missing one is obvious and a weak one silently looks like it works.
        """
        if v in _KNOWN_INSECURE:
            raise ValueError(
                f"{info.field_name} is set to a publicly-known placeholder. "
                "Generate one with: python -c \"import secrets; "
                "print(secrets.token_urlsafe(32))\""
            )
        if len(v) < 32:
            raise ValueError(
                f"{info.field_name} must be at least 32 characters "
                f"(got {len(v)})."
            )
        return v

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
