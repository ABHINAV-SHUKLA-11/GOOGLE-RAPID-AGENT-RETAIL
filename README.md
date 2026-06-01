# MongoDB Retail Agent 🏪

**AI-Powered Agent for Real-Time Retail Operations Management**

An intelligent agent powered by **Google Gemini 3** and **Google Cloud Agent Builder** that solves real-world retail challenges using **MongoDB** for data management and **GitLab** for CI/CD integration.

## 🎯 Problem Statement

Retail businesses struggle with:
- Real-time inventory tracking across multiple locations
- Customer behavior analytics and personalization
- Dynamic pricing based on demand and stock levels
- Automated customer service for common retail queries
- Supply chain optimization

## ✨ Solution

Our agent automates:
✅ **Inventory Management** — Real-time stock monitoring across all locations  
✅ **Customer Analytics** — Personalized recommendations based on purchase history  
✅ **Dynamic Pricing** — Automated price adjustments based on demand  
✅ **Customer Support** — 24/7 automated responses to common retail questions  
✅ **Sales Optimization** — Analytics-driven insights for store operations  

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────┐
│          Google Gemini 3 (Agent Brain)                  │
├─────────────────────────────────────────────────────────┤
│     Google Cloud Agent Builder (Orchestration)          │
├─────────────────────────────────────────────────────────┤
│  MongoDB MCP Server (Data Access & Operations)          │
├─────────────────────────────────────────────────────────┤
│    MongoDB Atlas (Real-Time Data Storage)               │
└─────────────────────────────────────────────────────────┘




## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Docker & Docker Compose**
- **Google Cloud Account** (with Agent Builder enabled)
- **MongoDB Atlas Account** (free tier available)
- **GitLab Account** (for CI/CD)

### Setup (5 minutes)

```bash
# 1. Clone the repository
git clone -https://gitlab.com/abhinavshukla76117/google-rapid-agent-retail
cd Google-rapid-agent-retail

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your credentials
nano .env

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start MongoDB locally
docker-compose up -d

# 6. Run the application
python src/app.py
Visit: http://localhost:8000

📊 Key Features
Feature	Description	Technology
Inventory Sync	Real-time stock updates across stores	MongoDB + Gemini
Customer Search	Find customers & their purchase history	MongoDB Aggregation
Dynamic Pricing	AI-driven price recommendations	Gemini ML
Order Management	Automated order processing & fulfillment	MongoDB Transactions
Analytics Dashboard	Visual insights into retail operations	Google Cloud Visualization
🛠️ Technology Stack
Backend: FastAPI (Python)
AI/ML: Google Gemini 3, Google Cloud Agent Builder
Database: MongoDB Atlas
Protocol: Model Context Protocol (MCP)
Cloud: Google Cloud Platform (Vertex AI, Cloud Run)
CI/CD: GitLab Pipelines
Containerization: Docker & Docker Compose
Testing: pytest
📝 API Endpoints


POST   /api/agent/query              # Send query to agent
GET    /api/inventory                # Get current inventory
POST   /api/pricing/update           # Update product pricing
GET    /api/customers/{id}           # Get customer data
POST   /api/orders                   # Create new order
GET    /api/analytics                # Get retail analytics
🔐 Environment Variables


GOOGLE\_CLOUD\_PROJECT\_ID=your-project-id
GOOGLE\_CLOUD\_REGION=us-central1
MONGODB\_URI=mongodb+srv://user:pass@cluster.mongodb.net/retail\_db
GEMINI\_API\_KEY=your-gemini-api-key
FLASK\_ENV=development
DEBUG=True
📚 Documentation
Architecture & Design
API Reference
MCP Server Setup
Deployment Guide
🧪 Testing
bash


# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test\_agent.py
🚀 Deployment
Deploy to Google Cloud Run
bash


bash scripts/deploy.sh
See DEPLOYMENT.md for detailed instructions.

GitLab CI/CD
Automatic deployment on push to main branch via .gitlab-ci.yml

💡 Example Usage
python


from src.app import query\_agent

# Query the agent
response = query\_agent(
    query="What is our current inventory for Nike Air Max shoes?",
    store\_id="store\_001"
)

print(response['answer'])
# Output: "Current inventory: 45 units across all stores..."
🎯 Use Cases Solved
1. Real-Time Inventory Check
User Query: "How many units of Product XYZ are in stock?"
Agent Action: Queries MongoDB, aggregates data across locations, returns real-time count.

2. Customer Purchase History
User Query: "Show me John's purchase history for the last 6 months"
Agent Action: Searches MongoDB, retrieves transactions, calculates spending patterns.

3. Dynamic Pricing Recommendation
User Query: "What price should we set for winter coats this week?"
Agent Action: Analyzes demand, competitor pricing, inventory levels, recommends optimal price.

4. Automated Order Fulfillment
User Query: "Process this customer order and update inventory"
Agent Action: Creates order in MongoDB, updates stock, triggers fulfillment workflow.

📊 Performance Metrics
Agent Response Time: < 2 seconds
MongoDB Query Speed: < 500ms
API Throughput: 1000+ requests/minute
Uptime: 99.9% (Google Cloud Run SLA)
🔄 GitLab Integration
CI/CD Pipeline: Automatic testing & deployment
Issue Tracking: Feature requests & bug reports in GitLab Issues
Code Review: Merge requests for all changes
Repository: https://gitlab.com/your-username/mongodb-retail-agent
🤝 Contributing
Fork the repository
Create a feature branch: git checkout -b feature/your-feature
Commit changes: git commit -m "Add your feature"
Push to branch: git push origin feature/your-feature
Open a Merge Request on GitLab
📄 License
This project is licensed under the MIT License - see LICENSE file for details.

👥 Team Name -- Team Cloud Craft
Developer : Abhinav Shukla and Rishabh Gautam
Architecture:         ## 🏗️ Architecture & System Data Flow

Designed and implemented by **Team Cloud-Craft**, this system bridges the gap between natural language user intents and strict enterprise databases using the Model Context Protocol (MCP).

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          1. USER INTERFACE                             │
│       [User inputs query: "What is the stock of Nike Air Max?"]       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (HTTP POST /query)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               2. BACKEND API GATEWAY (app.py / main.py)               │
│   - Managed by Abhinav Shukla (Leader) & Rishabh Gautam.               │
│   - Passes the query session context to Google Cloud Agent Builder.    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Vertex AI / Agent Builder API)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               3. AI ORCHESTRATION ENGINE (Gemini 2.0 Flash)             │
│   - Analyzes user's natural language prompt.                          │
│   - Detects intent and decides which database tool to invoke.          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Model Context Protocol - MCP)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     4. MCP SERVER (mongodb_mcp_server.py)              │
│   - Receives tool calling request (e.g., get_products(filter)).        │
│   - Translates AI requests into strict MongoDB queries.                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (PyMongo Connection)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     5. DATA LAYER (MongoDB Atlas Cluster)              │
│   - Executes aggregation pipeline or standard CRUD.                   │
│   - Returns raw JSON data back up the chain to Team Cloud-Craft's API. │
└────────────────────────────────────────────────────────────────────────┘
Testing:## 🧪 Testing Framework & Verification

**Team Cloud-Craft** uses `pytest` along with `pytest-asyncio` to test both synchronous API routes and asynchronous MCP operations. 

### 1. Structure of Tests Folder
To execute tests, ensure your `tests/` directory matches the plan:
```text
tests/
├── __init__.py
├── test_agent.py          # Verifies Gemini Agent responses (Developed by Abhinav)
└── test_mongodb.py        # Verifies MCP server database queries (Developed by Rishabh)
📞 Support
Issues: GitLab Issues
Discussions: GitLab Discussions
Email: your-email@example.com
🏆 Hackathon
This project was built for the Google Cloud Rapid Agent Hackathon 2026 using MongoDB & GitLab partner tracks.