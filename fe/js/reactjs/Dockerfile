ARG NODE_VERSION=24.14.0-alpine
ARG PORT=3000
ARG PORT_UI=80

FROM node:${NODE_VERSION} AS builder

WORKDIR /app

COPY ./my-react-app/package.json ./my-react-app/package-lock.json ./

RUN --mount=type=cache,target=/root/.npm npm ci

COPY ./my-react-app/ .

RUN npm run build

FROM node:${NODE_VERSION} AS runner

ENV NODE_ENV=production

WORKDIR /app

COPY --link --from=builder /app/dist ./dist

RUN --mount=type=cache,target=/root/.npm npm install serve@^14.2.6 --omit=dev

USER node

EXPOSE ${PORT}

CMD ["npx", "serve", "-s", "dist", "-l", "${PORT}"]

FROM node:18-alpine AS build
WORKDIR /app
COPY ./my-react-app/package*.json ./
RUN npm install
COPY ./my-react-app/. .
RUN npm run build

FROM nginx:stable-alpine AS production
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE ${PORT_UI}
CMD ["nginx", "-g", "daemon off;"]
