# Stage 1: Build the React application
FROM node:22-bookworm AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --force

# Copy the rest of the application code
COPY . .

# Build the application for production
ARG VITE_API_URL="http://localhost:5000/api/hermes"
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
