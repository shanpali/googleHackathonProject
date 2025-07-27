#!/bin/bash
# Build and deploy Flask backend for x86_64 (amd64) on Mac (arm64)

read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter Artifact Registry region (e.g., asia-east1): " REGION
REPO_NAME="flask-backend-repo"
IMAGE_NAME="flask-backend"
TAG="latest"
SERVICE_NAME="flask-backend"

# Authenticate gcloud
#gcloud auth login
gcloud config set project $PROJECT_ID

# Authenticate Docker with Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push the unified image for linux/amd64
podman build --arch amd64 -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$TAG .

podman push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$TAG

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$TAG \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080

echo "Deployment complete. Check Cloud Run logs if you encounter issues."

