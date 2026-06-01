# Build: Use Node 20 Alpine for minimal footprint
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY package*.json ./
RUN npm install

# Copy application source
COPY . .

# Expose the service port
EXPOSE 3000

# Set environment
ENV NODE_ENV=development

# Startup command
CMD ["npm", "run", "dev"]