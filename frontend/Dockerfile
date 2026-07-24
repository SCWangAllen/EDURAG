# Build stage
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# 生產同源 API：由 docker-compose.prod.yml 的 build.args 傳入 VITE_API_BASE_URL=/
# 未傳入時（dev docker / 一般 build）為空字串 → axios.js 走既有 hostname fallback，行為不變。
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]