FROM --platform=linux/amd64 ghcr.io/owl-corp/python-poetry-base:3.10-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "wopr"]
