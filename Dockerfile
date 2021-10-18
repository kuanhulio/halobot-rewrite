FROM python:3.9-bullseye
LABEL maintainer="Sami Altamimi <saltamimi@kuantum.link>"

RUN apt update && apt upgrade -y

WORKDIR /halobot

COPY . .

RUN pip install --no-cache-dir pipenv
RUN pipenv install --skip-lock

CMD ["pipenv", "run", "python", "bot.py"]