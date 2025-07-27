# Stage 1: Build React frontend
FROM node:20 AS frontend-builder
WORKDIR /app/react-frontend
COPY react-frontend/package.json react-frontend/package-lock.json ./
RUN npm install
COPY react-frontend/ ./
RUN npm run build

# Stage 2: Build Flask backend
FROM python:3.13-slim AS backend
WORKDIR /app

# Copy requirements and install
COPY flask-backend/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend code
COPY flask-backend/ ./

# Copy React build output to Flask static directory
COPY --from=frontend-builder /app/react-frontend/build/ flask-backend/static/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
