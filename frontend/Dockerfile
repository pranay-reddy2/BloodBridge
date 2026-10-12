# syntax=docker/dockerfile:1

# ---------- build stage: Node toolchain only lives here ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---------- runtime stage: unprivileged Nginx serving static files ----------
# nginx-unprivileged runs as UID 101 and listens on 8080, so no root and no CAP_NET_BIND_SERVICE.
FROM nginxinc/nginx-unprivileged:stable-alpine AS runtime
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="bloodbridge-frontend" \
      org.opencontainers.image.revision="${APP_VERSION}"

# Pick up Alpine security fixes released after the base image was published, then drop back to non-root.
USER root
RUN apk upgrade --no-cache
USER 101

ENV BACKEND_UPSTREAM=backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
