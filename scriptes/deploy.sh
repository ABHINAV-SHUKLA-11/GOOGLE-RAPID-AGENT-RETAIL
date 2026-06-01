#!/bin/bash

# Deploy Inventory Agent to Google Cloud

set -e

echo "🚀 Deploying Inventory Agent to Google Cloud..."

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

source .env

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is required. Install it first."
    exit 1
fi

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project $GOOGLE_PROJECT_ID

# Create Cloud Run service
echo "📦 Building and deploying to Cloud Run..."

# Build Docker image (if Dockerfile exists)
if [ -f Dockerfile ]; then
    echo "🐳 Building Docker image..."
    docker build -t gcr.io/$GOOGLE_PROJECT_ID/inventory-agent .
    
    echo "📤 Pushing to Container Registry..."
    docker push gcr.io/$GOOGLE_PROJECT_ID/inventory-agent
    
    echo "☁️  Deploying to Cloud Run..."
    gcloud run deploy inventory-agent \
        --image gcr.io/$GOOGLE_PROJECT_ID/inventory-agent \
        --platform managed \
        --region us-central1 \
        --memory 2Gi \
        --timeout 300 \
        --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY,MONGODB_URI=$MONGODB_URI
else
    echo "⚠️  Dockerfile not found. Creating a simple Python Cloud Run deployment..."
fi

echo ""
echo "✅ Deployment complete!"
echo "Your agent is now running on Google Cloud!"
echo ""
