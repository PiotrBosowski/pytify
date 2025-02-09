FROM python:3.11-slim

WORKDIR /app

ENV POETRY_VERSION=2.0 \
    PYTIFY_PORT=5001


RUN apt update && apt install -y ffmpeg curl

RUN pip install poetry==$POETRY_VERSION
    
COPY . .

RUN poetry install --no-root --no-interaction --no-ansi

CMD [ "poetry", "run", "python", "main.py" ]
