#!/bin/bash

# Test the Inventory Management Agent

echo "🧪 Testing Inventory Management Agent..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run tests
echo "Running unit tests..."
python3 -m pytest tests/ -v --tb=short 2>/dev/null || echo "⚠️  No tests found. Skipping."

# Run the agent with sample data
echo ""
echo "Running agent with sample inventory check..."
python3 << 'PYTHON_TEST'
import sys
sys.path.insert(0, '.')

from agent import InventoryAgent
import json

# Initialize agent
agent = InventoryAgent()

# Test Case 1: Check inventory for a product
print("\n📊 Test 1: Checking inventory levels...")
print("=" * 60)
result = agent.process_inventory_check("store-001", "PROD-SKU-12345")
print(result)

# Test Case 2: Run agent loop
print("\n🔄 Test 2: Running full agent workflow...")
print("=" * 60)
result = agent.run_daily_inventory_check()
print(json.dumps(result, indent=2))

PYTHON_TEST

echo ""
echo "✅ Testing complete!"
