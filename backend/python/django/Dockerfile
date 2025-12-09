FROM python:3.6.3-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

RUN apk update \
    && apk add \
    build-base \
    postgresql \
    postgresql-dev \
    libpq \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8800

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8800"]