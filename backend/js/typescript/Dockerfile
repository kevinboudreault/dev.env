FROM node:22-alpine AS base

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk update

COPY package.json package-lock.json tsconfig.json ./

RUN npm install

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 4321

COPY . .

FROM base AS production

RUN apk update
RUN apk add --no-cache libc6-compat
RUN apk add --no-cache openssl

ENV NODE_PATH=./build

RUN npm run build

CMD ["npm","run","dev","--","--host"]