FROM postgres:16-alpine

ENV POSTGRES_PASSWORD={$PG_PASSWORD:"db_Pass_postgres1"}
ENV POSTGRES_USER={$PG_USER:"user_postgres"}
ENV POSTGRES_DB={$PG_DB:"postgres_db"}
ENV POSTGRES_ROOT_PASSWORD={$PG_ROOT_PWD:"rootPWD"}
ENV POSTGRES_PORT={$PG_PORT:"5432"}

COPY ./init.sql /docker-entrypoint-initdb.d/