FROM python:3.8-alpine
LABEL maintainer="Sami Altamimi <saltamimi@kuantum.link>"

RUN apk update && apk upgrade

RUN apk add --no-cache python3-dev git make build-base linux-headers gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev

WORKDIR /halobot-rewrite

COPY bot.py ./bot.py
COPY config.json ./config.json
COPY Pipfile ./Pipfile
COPY Pipfile.lock ./Pipfile.lock
COPY ./cogs ./cogs

RUN pip install --no-cache-dir pipenv
RUN pipenv install

CMD ["pipenv", "run", "python", "bot.py"]
