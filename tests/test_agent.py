"""
Unit tests for the MongoDB Retail Agent
Tests core agent functionality, task planning, and execution
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.app import app
from src.config import Config
from fastapi.testclient import TestClient


client = TestClient(app)


class TestAgentCore:
    """Test core agent functionality"""

    def test_agent_initialization(self):
        """Test that agent initializes with correct configuration"""
        assert Config.GEMINI_MODEL is not None
        assert Config.MONGODB_URI is not None
        assert Config.MCP_SERVER_ENABLED is True

    def test_agent_task_planning(self):
        """Test agent can break down complex retail tasks into steps"""
        response = client.post(
            "/api/agent/plan",
            json={
                "task": "Find low-stock items in Electronics category and create reorder alerts",
                "context": {"store_id": "store_001"}
            }
        )
        assert response.status_code == 200
        plan = response.json()
        assert "steps" in plan
        assert len(plan["steps"]) > 0
        assert any("MongoDB" in str(step) for step in plan["steps"])

    @pytest.mark.asyncio
    async def test_agent_mongodb_integration(self):
        """Test agent can query MongoDB via MCP server"""
        response = client.post(
            "/api/agent/execute",
            json={
                "action": "query_inventory",
                "params": {
                    "category": "Electronics",
                    "min_stock": 5
                }
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "items" in result or "error" not in result

    def test_agent_multi_step_execution(self):
        """Test agent executes multiple steps in sequence"""
        response = client.post(
            "/api/agent/execute_workflow",
            json={
                "workflow": "inventory_optimization",
                "params": {
                    "store_id": "store_001",
                    "reorder_threshold": 10
                }
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert result["status"] in ["success", "completed", "in_progress"]

    def test_agent_error_handling(self):
        """Test agent gracefully handles errors"""
        response = client.post(
            "/api/agent/execute",
            json={
                "action": "invalid_action",
                "params": {}
            }
        )
        assert response.status_code in [400, 422]
        assert "error" in response.json()

    def test_agent_retail_scenario_missing_stock(self):
        """Test: Agent identifies missing stock items and triggers reorder"""
        response = client.post(
            "/api/agent/scenario",
            json={
                "scenario_id": "missing_stock",
                "data": {
                    "items": [
                        {"sku": "ITEM001", "stock": 0, "reorder_point": 5},
                        {"sku": "ITEM002", "stock": 2, "reorder_point": 10}
                    ]
                }
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "reorders_created" in result
        assert len(result["reorders_created"]) >= 1

    def test_agent_retail_scenario_customer_journey(self):
        """Test: Agent optimizes customer journey in brick-and-mortar retail"""
        response = client.post(
            "/api/agent/scenario",
            json={
                "scenario_id": "customer_navigation",
                "data": {
                    "customer_location": "entrance",
                    "shopping_list": ["shoes", "jacket"],
                    "store_layout": "mall_001"
                }
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "navigation_path" in result
        assert "estimated_time" in result

    def test_agent_reasoning_transparency(self):
        """Test: Agent provides transparent reasoning for decisions"""
        response = client.post(
            "/api/agent/execute",
            json={
                "action": "complex_decision",
                "params": {"include_reasoning": True}
            }
        )
        assert response.status_code == 200
        result = response.json()
        assert "reasoning" in result
        assert "decision" in result
        assert len(result["reasoning"]) > 0


class TestMCPIntegration:
    """Test MongoDB MCP Server integration"""

    def test_mcp_server_connection(self):
        """Test MCP server establishes connection"""
        response = client.get("/api/health/mcp")
        assert response.status_code == 200
        assert response.json()["mcp_connected"] is True

    def test_mcp_server_tools_available(self):
        """Test MCP server exposes expected MongoDB tools"""
        response = client.get("/api/mcp/tools")
        assert response.status_code == 200
        tools = response.json()["tools"]
        expected_tools = ["find", "insert", "update", "delete", "aggregate"]
        assert all(tool in [t["name"] for t in tools] for tool in expected_tools)

    def test_mcp_database_read_operation(self):
        """Test MCP server executes read operations on MongoDB"""
        response = client.post(
            "/api/mcp/execute",
            json={
                "tool": "find",
                "collection": "products",
                "query": {"category": "Electronics"}
            }
        )
        assert response.status_code == 200
        assert "results" in response.json()

    def test_mcp_database_write_operation(self):
        """Test MCP server executes write operations on MongoDB"""
        response = client.post(
            "/api/mcp/execute",
            json={
                "tool": "insert",
                "collection": "audit_log",
                "data": {
                    "action": "test_write",
                    "timestamp": "2026-05-31T00:00:00Z"
                }
            }
        )
        assert response.status_code == 200
        assert "inserted_id" in response.json() or "success" in response.json()

    def test_mcp_aggregation_pipeline(self):
        """Test MCP server executes complex aggregation pipelines"""
        response = client.post(
            "/api/mcp/execute",
            json={
                "tool": "aggregate",
                "collection": "orders",
                "pipeline": [
                    {"$match": {"status": "completed"}},
                    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
                    {"$sort": {"total": -1}}
                ]
            }
        )
        assert response.status_code == 200
        assert "results" in response.json()


class TestRetailUseCases:
    """Test real-world retail scenarios"""

    def test_inventory_management_workflow(self):
        """Test: Complete inventory management workflow"""
        # Step 1: Check stock levels
        response = client.post(
            "/api/retail/inventory/check",
            json={"store_id": "store_001"}
        )
        assert response.status_code == 200
        stock_data = response.json()

        # Step 2: Generate reorder recommendations
        response = client.post(
            "/api/retail/inventory/recommend",
            json={"stock_data": stock_data}
        )
        assert response.status_code == 200
        recommendations = response.json()
        assert "reorders" in recommendations

        # Step 3: Create purchase orders
        response = client.post(
            "/api/retail/inventory/create_orders",
            json={"recommendations": recommendations["reorders"]}
        )
        assert response.status_code == 200
        assert "orders_created" in response.json()

    def test_dynamic_pricing_workflow(self):
        """Test: Agent optimizes pricing based on demand"""
        response = client.post(
            "/api/retail/pricing/optimize",
            json={
                "category": "Fashion",
                "time_period": "weekend",
                "demand_level": "high"
            }
        )
        assert response.status_code == 200
        pricing = response.json()
        assert "recommended_prices" in pricing
        assert "reasoning" in pricing

    def test_shopper_experience_enhancement(self):
        """Test: Agent enhances in-store shopper experience"""
        response = client.post(
            "/api/retail/experience/optimize",
            json={
                "store_layout": "mall_001",
                "shopper_profile": "budget_conscious",
                "current_location": "electronics_aisle"
            }
        )
        assert response.status_code == 200
        experience = response.json()
        assert "recommendations" in experience
        assert "promotions" in experience


class TestPerformance:
    """Test performance and scalability"""

    def test_agent_response_time(self):
        """Test agent responds within acceptable time"""
        import time
        start = time.time()
        response = client.post(
            "/api/agent/execute",
            json={"action": "quick_query", "params": {}}
        )
        elapsed = time.time() - start
        assert elapsed < 5.0, f"Agent took {elapsed}s, expected < 5s"
        assert response.status_code == 200

    def test_mongodb_query_performance(self):
        """Test MongoDB queries perform efficiently"""
        response = client.post(
            "/api/mcp/execute",
            json={
                "tool": "find",
                "collection": "products",
                "limit": 1000
            }
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_concurrent_agent_requests(self):
        """Test agent handles concurrent requests"""
        tasks = [
            asyncio.create_task(
                asyncio.to_thread(
                    client.post,
                    "/api/agent/execute",
                    json={"action": "test", "params": {}}
                )
            ) for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)
        assert all(r.status_code in [200, 201] for r in results)
