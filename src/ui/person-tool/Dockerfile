FROM node:20-alpine

WORKDIR /app

# Accept build argument for API base URL
ARG REACT_APP_API_BASE=http://localhost:8000/api/v1
ENV REACT_APP_API_BASE=$REACT_APP_API_BASE

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Install serve to serve the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the production server
CMD ["serve", "-s", "build", "-l", "3000"]

