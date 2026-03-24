# Frontend Dockerfile - Multi-stage build for optimization
FROM node:18-slim as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with proper permissions
RUN npm install --legacy-peer-deps && npm ci --legacy-peer-deps 2>/dev/null || true
RUN chmod -R 755 node_modules/.bin/ && chmod -R 755 node_modules/vite/bin/ 2>/dev/null || true

# Copy source code
COPY . .

# Build optimized production bundle
RUN npm run build || (npm install && npm run build)

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
