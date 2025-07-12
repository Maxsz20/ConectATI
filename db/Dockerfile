FROM ubuntu:latest

# Instalacion de SQLite
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev \
    && mkdir /db

WORKDIR /db

CMD ["tail", "-f", "/dev/null"]