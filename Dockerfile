# Multi-stage Docker build for ShellHacks 2025 Ops Mesh Demo
FROM node:18-slim AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend package files
COPY ops-mesh-frontend/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY ops-mesh-frontend/ ./

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY ops-mesh-backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY ops-mesh-backend/ ./

# Create database directory
RUN mkdir -p /app/data

# Production stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy backend application
COPY ops-mesh-backend/ ./

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/public
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/
COPY --from=frontend-builder /app/frontend/node_modules /app/frontend/node_modules
COPY --from=frontend-builder /app/frontend/next.config.ts /app/frontend/

# Create startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create data directory
RUN mkdir -p /app/data

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/ops_mesh.db
ENV API_V1_STR=/api/v1
ENV PROJECT_NAME="Ops Mesh Backend"
ENV BACKEND_CORS_ORIGINS='["http://localhost:3000","http://localhost:3001","http://127.0.0.1:3000","http://127.0.0.1:3001"]'
ENV DEBUG=false
ENV RELOAD=false

# Use startup script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
