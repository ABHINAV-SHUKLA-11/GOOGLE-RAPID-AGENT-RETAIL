#!/bin/bash

# MongoDB Retail Agent - Setup Script
# Run this first to install all dependencies

set -e

echo "🚀 Setting up MongoDB Retail Agent..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
# Google Cloud Configuration
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_PROJECT_ID=your-project-id-here

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/retail_db
MONGODB_DATABASE=retail_db

# MCP Server Configuration
MONGODB_MCP_URL=http://localhost:5000
MCP_SERVER_PORT=5000

# Agent Configuration
AGENT_MODEL=gemini-2.0-flash
STORE_ID=store-001
EOF
    echo "📝 .env file created. Please update with your credentials."
fi

# Create MongoDB collections (if connecting to Atlas)
echo "📊 Setting up MongoDB collections..."
python3 << 'PYTHON_SCRIPT'
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DATABASE")]
    
    # Create collections if they don't exist
    collections = ["inventory", "sales", "purchase_orders", "suppliers", "alerts"]
    
    for collection_name in collections:
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
            print(f"✅ Created collection: {collection_name}")
        else:
            print(f"⏭️  Collection already exists: {collection_name}")
    
    # Create indexes for performance
    db.inventory.create_index("product_id")
    db.inventory.create_index("store_id")
    db.sales.create_index("product_id")
    db.purchase_orders.create_index("status")
    print("✅ Indexes created successfully")
    
except Exception as e:
    print(f"⚠️  MongoDB setup warning: {e}")
    print("You may need to set up MongoDB manually.")

PYTHON_SCRIPT

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python3 agent.py"
echo ""
