# Build stage
FROM node:22-slim AS build

WORKDIR /app

# Install dependencies using cache mount for npm
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm install

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Create a non-root user and group
# Alpine's nginx package already includes an 'nginx' user, 
# but we need to ensure permissions for non-root execution on port 8080.

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build artifacts from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Adjust permissions for non-root execution
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
