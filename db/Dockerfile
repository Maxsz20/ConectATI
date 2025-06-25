FROM ubuntu:latest

# Instalacion de SQLite
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev \
    && mkdir /db

WORKDIR /db

# Crea archivo de base de datos vacío
CMD ["sqlite3", "/db/mydatabase.db"]