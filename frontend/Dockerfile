# Frontend build stage
FROM node:18-slim as builder

WORKDIR /app

ENV NODE_OPTIONS=--max-old-space-size=4096

COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund --prefer-offline

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]