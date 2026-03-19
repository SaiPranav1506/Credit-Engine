# Frontend Dockerfile - Multi-stage build for optimization
FROM node:18-slim as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci || npm install

# Copy source code
COPY . .

# Build optimized production bundle
RUN npm run build

# Production stage - serve with lightweight server
FROM node:18-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Expose port (will use PORT env var from Render)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:${PORT:-3000}/ || exit 1

# Start the application - respects PORT environment variable for Render
CMD ["sh", "-c", "serve -s dist -l ${PORT:-3000}"]
