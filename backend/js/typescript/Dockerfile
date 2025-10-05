FROM node:20-alpine AS base

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY package.json ./
COPY package-lock.json ./

RUN npm install

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 4321


COPY . .

FROM base AS production

ENV NODE_PATH=./build

RUN npm run build


CMD ["npm","run","dev","--","--host"]
