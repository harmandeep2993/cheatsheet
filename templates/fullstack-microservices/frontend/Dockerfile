# Stage 1: build the static files with Node
FROM node:22-alpine AS build
WORKDIR /app
# Dependencies first, so this layer is cached until package-lock.json changes
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: only Nginx and the built files; Node and node_modules are not in the final image
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
