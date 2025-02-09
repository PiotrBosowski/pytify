FROM python:3.11-slim

WORKDIR /app

ENV POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="$POETRY_HOME/bin:$PATH" \
    PYTIFY_PORT=5001


RUN apt update && apt install -y ffmpeg && \
    curl -sSL https://install.python-poetry.org | python3 -
    
COPY . .

RUN poetry install --no-root --no-interaction --no-ansi

CMD [ "poetry", "run", "python", "webserver.py" ]
