# Stage 1: Build React frontend
FROM node:20 AS frontend-builder
WORKDIR /app/react-frontend
COPY react-frontend/package.json react-frontend/package-lock.json ./
RUN npm install
COPY react-frontend/ ./
RUN npm run build


# Stage 2: Build Flask backend and Go server
FROM python:3.13-slim AS backend
WORKDIR /app

# Install Go
RUN apt-get update && apt-get install -y golang-go && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY flask-backend/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend code
COPY flask-backend/ ./

# Copy Go server code and build binary
COPY fi-mcp-data-server/main.go fi-mcp-data-server/
COPY fi-mcp-data-server/go.mod fi-mcp-data-server/
COPY fi-mcp-data-server/go.sum fi-mcp-data-server/
RUN cd fi-mcp-data-server && go build -o fi-mcp-server main.go


# Copy React build output to Flask static directory
COPY --from=frontend-builder /app/react-frontend/build/ flask-backend/static/

EXPOSE 8080
EXPOSE 8484

# Use supervisord to run both servers
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
