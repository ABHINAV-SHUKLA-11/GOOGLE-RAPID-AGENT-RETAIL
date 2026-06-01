 FastAPI Application Layer (HTTP Interface)
Responsibility: REST API, WebSocket streaming, health monitoring

Key Endpoints:

python


# Agent Endpoints
POST   /api/agent/plan              # Plan multi-step tasks
POST   /api/agent/execute           # Execute agent actions
POST   /api/agent/execute\_workflow  # Run predefined workflows
POST   /api/agent/scenario          # Handle retail scenarios
GET    /api/agent/status            # Check agent status

# Retail Business Endpoints
POST   /api/retail/inventory/*      # Inventory management
POST   /api/retail/pricing/*        # Dynamic pricing
POST   /api/retail/experience/*     # Shopper experience
GET    /api/retail/analytics/*      # Business analytics

# MCP Integration Endpoints
GET    /api/mcp/tools               # List available tools
POST   /api/mcp/execute             # Execute MCP tool
GET    /api/health/mcp              # MCP server status

# System Health
GET    /api/health                  # API health
GET    /api/health/db               # MongoDB connectivity
GET    /api/metrics                 # Performance metrics