FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements.txt

# Cache the real tokenizer once at build time; startup never downloads it.
ENV TIKTOKEN_CACHE_DIR=/opt/tiktoken-cache
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"
COPY . .

RUN chmod +x wait-for-db.sh start-api.sh start-worker.sh

FROM runtime AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -c constraints.txt -r requirements-dev.txt
CMD ["python", "-m", "pytest"]

# Keep production as the default Docker target for Railway. Compose selects
# `runtime` explicitly for local development; CI can select `test` explicitly.
FROM runtime AS production
CMD ["./start-api.sh"]
