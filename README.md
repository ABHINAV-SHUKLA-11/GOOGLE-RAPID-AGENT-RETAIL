# 🛍️ Retail AI Agent — Team Cloud Craft

> Smart AI-powered retail management agent built for **Google Cloud Rapid Agent Hackathon 2026** — Brick-and-Mortar Retail Track.

## 🔗 Live Demo
- **Frontend UI:** https://google-rapid-agent-retail-44551099700.europe-west1.run.app/ui
- **API:** https://google-rapid-agent-retail-44551099700.europe-west1.run.app

## 👥 Team
- **Abhinav Shukla** — Team Cloud Craft
- **Rishabh Gautam** — Team Cloud Craft

## 🏗️ Architecture
User → Frontend UI → Google Cloud Run → MongoDB Atlas
↑
Google Agent Builder (Gemini 2.5 Flash)
↑
MongoDB MCP Server

## 🚀 Features
- 🔍 Product search, price & rating filters
- 🛒 Order create, delete, update via chat
- 🧾 GST Invoice generation (18%)
- 📊 Revenue reports & store analytics
- ⚠️ Low stock alerts
- 🏆 Top rated products

## 💬 Example Commands

show all products
products under $100
top rated products
low stock alerts
revenue report
store dashboard
orders for John Doe
bill for ORD-001
create order for Amit product Nike Air Max qty 2
delete order Rahul Kumar
mark ORD-001 as delivered
who bought Nike Air Max

## 🛠️ Tech Stack
| Layer | Technology |
|-------|-----------|
| AI Agent | Google Agent Builder + Gemini 2.5 Flash |
| Database | MongoDB Atlas |
| MCP Server | MongoDB MCP Server |
| Backend | Python Flask + PyMongo |
| Deployment | Google Cloud Run (europe-west1) |
| Frontend | HTML/CSS/JavaScript |

## 🔧 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /ui | Frontend dashboard |
| POST | /query | AI Agent chat |
| GET | /products | List products |
| POST | /products | Add product |
| GET | /orders | List orders |
| POST | /orders | Create order |
| DELETE | /orders/:id | Delete order |
| PUT | /orders/:id | Update order |
| GET | /mcp/tools | MCP tools |
| GET | /health | Health check |

## 📦 Setup

### Environment Variables

MONGODB_URI=your_mongodb_connection_string
DB_NAME=retail_db

### Deploy to Cloud Run
```bash
gcloud run deploy google-rapid-agent-retail \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars MONGODB_URI="your_uri",DB_NAME="retail_db"
```

### MongoDB MCP Server
```
npm install -g mongodb-mcp-server
MDB_MCP_CONNECTION_STRING="your_mongodb_uri" mongodb-mcp-server
```

## 🏆 Hackathon Track
**Brick-and-Mortar Retail** — Bridges digital convenience and physical retail:
- Real-time inventory management
- Automated order processing via natural language
- Instant GST invoice generation
- AI-powered store analytics & insights

## 📄 License
MIT License


## ⚠️ Important Note — Product Management

This agent is **customer-facing**.

Customers can:
- ✅ Browse products
- ✅ Place orders
- ✅ Get invoices
- ✅ Check order status

## ⚠️ Product Management


Products can be added via:

1. MongoDB Atlas (Direct)
2. REST API → POST /products
3. Postman / Any API Client

Customers CANNOT add products.
This is intentional security design.
