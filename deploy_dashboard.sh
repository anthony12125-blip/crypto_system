#!/bin/bash
# Deploy Crypto Bot Dashboard to Google Cloud Run

PROJECT_ID="${PROJECT_ID:-proud-climber-421817}"
SERVICE_NAME="crypto-bot"
REGION="us-central1"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "==============================================="
echo "Deploying Crypto Bot Dashboard to Cloud Run"
echo "==============================================="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Build the container
echo "Building container..."
gcloud builds submit --tag $IMAGE_TAG

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="DASHBOARD_API_KEY=crypto-bot-2026" \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --max-instances=10 \
  --min-instances=1

echo ""
echo "==============================================="
echo "Deployment Complete!"
echo "==============================================="
echo "Dashboard URL: https://$SERVICE_NAME-409495160162.$REGION.run.app"
echo ""
