ARG APP_PORT=5173
ENV APP_PORT=${APP_PORT}

FROM node:18-alpine

WORKDIR /app
COPY ./app/package*.json ./

RUN npm install

COPY ./app/ .

EXPOSE ${APP_PORT}

CMD ["npm", "run", "dev", "--", "--host"]
