


import pytest
import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure, 
    ServerSelectionTimeoutError,
    DuplicateKeyError,
    OperationFailure
)
from dotenv import load_dotenv
import json

# Import your modules
from src.mongodb_mcp_server import MongoDBMCPServer
from src.models import Product, Order, Customer
from src.config import Settings

load_dotenv()


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def mongodb_uri():
    """MongoDB connection URI"""
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


@pytest.fixture(scope="session")
def test_database_name():
    """Test database name"""
    return "retail_agent_test"


@pytest.fixture(scope="session")
async def mongodb_connection(mongodb_uri, test_database_name):
    """Establish MongoDB connection"""
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        yield client[test_database_name]
        # Cleanup
        client.drop_database(test_database_name)
        client.close()
    except (ConnectionFailure, ServerSelectionTimeoutError):
        pytest.skip("MongoDB server not available")


@pytest.fixture
async def mcp_server(mongodb_uri, test_database_name):
    """Initialize MongoDB MCP Server"""
    server = MongoDBMCPServer(
        mongodb_uri=mongodb_uri,
        database_name=test_database_name
    )
    await server.connect()
    yield server
    await server.disconnect()


@pytest.fixture
def retail_products():
    """Sample retail products with embeddings for Vector Search"""
    return [
        {
            "_id": "prod_wireless_headphones",
            "name": "Premium Wireless Headphones",
            "category": "Electronics",
            "price": 79.99,
            "stock": 150,
            "sku": "WH-P-001",
            "description": "High-quality noise-canceling wireless headphones with 30-hour battery life",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],  # Mock embedding
            "created_at": datetime.utcnow(),
            "rating": 4.5,
            "supplier_id": "sup_001",
            "cost": 35.00,
            "margin": 0.55
        },
        {
            "_id": "prod_usb_cable",
            "name": "Fast Charging USB-C Cable",
            "category": "Accessories",
            "price": 12.99,
            "stock": 500,
            "sku": "USB-C-001",
            "description": "Durable 2-meter USB-C charging cable with 100W power delivery",
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
            "created_at": datetime.utcnow(),
            "rating": 4.2,
            "supplier_id": "sup_001",
            "cost": 4.00,
            "margin": 0.69
        },
        {
            "_id": "prod_phone_case",
            "name": "Protective Phone Case",
            "category": "Accessories",
            "price": 24.99,
            "stock": 300,
            "sku": "CASE-001",
            "description": "Shock-absorbing phone case with premium materials",
            "embedding": [0.3, 0.4, 0.5, 0.6, 0.7],
            "created_at": datetime.utcnow(),
            "rating": 4.3,
            "supplier_id": "sup_002",
            "cost": 8.00,
            "margin": 0.68
        }
    ]


@pytest.fixture
def retail_customers():
    """Sample retail customers"""
    return [
        {
            "_id": "cust_john_doe",
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0101",
            "address": "123 Main Street, Springfield, IL 62701",
            "created_at": datetime.utcnow() - timedelta(days=365),
            "total_orders": 12,
            "lifetime_value": 1250.50,
            "segment": "premium",
            "last_purchase_date": datetime.utcnow() - timedelta(days=5),
            "average_order_value": 104.21
        },
        {
            "_id": "cust_jane_smith",
            "name": "Jane Smith",
            "email": "jane.smith@email.com",
            "phone": "+1-555-0102",
            "address": "456 Oak Avenue, Chicago, IL 60601",
            "created_at": datetime.utcnow() - timedelta(days=180),
            "total_orders": 5,
            "lifetime_value": 425.75,
            "segment": "standard",
            "last_purchase_date": datetime.utcnow() - timedelta(days=15),
            "average_order_value": 85.15
        },
        {
            "_id": "cust_robert_wilson",
            "name": "Robert Wilson",
            "email": "robert.wilson@email.com",
            "phone": "+1-555-0103",
            "address": "789 Pine Road, Boston, MA 02101",
            "created_at": datetime.utcnow() - timedelta(days=30),
            "total_orders": 1,
            "lifetime_value": 150.00,
            "segment": "new",
            "last_purchase_date": datetime.utcnow() - timedelta(days=25),
            "average_order_value": 150.00
        }
    ]


@pytest.fixture
def retail_orders():
    """Sample retail orders"""
    return [
        {
            "_id": "ord_001_001",
            "customer_id": "cust_john_doe",
            "order_date": datetime.utcnow() - timedelta(days=10),
            "items": [
                {"product_id": "prod_wireless_headphones", "quantity": 1, "price": 79.99},
                {"product_id": "prod_usb_cable", "quantity": 2, "price": 12.99}
            ],
            "total_amount": 105.97,
            "status": "completed",
            "shipping_address": "123 Main Street, Springfield, IL 62701",
            "payment_method": "credit_card",
            "shipping_cost": 9.99,
            "tax": 8.48,
            "discount_applied": 0,
            "fulfillment_date": datetime.utcnow() - timedelta(days=8)
        },
        {
            "_id": "ord_001_002",
            "customer_id": "cust_john_doe",
            "order_date": datetime.utcnow() - timedelta(days=2),
            "items": [
                {"product_id": "prod_phone_case", "quantity": 3, "price": 24.99}
            ],
            "total_amount": 74.97,
            "status": "pending",
            "shipping_address": "123 Main Street, Springfield, IL 62701",
            "payment_method": "credit_card",
            "shipping_cost": 7.99,
            "tax": 5.62,
            "discount_applied": 0,
            "fulfillment_date": None
        },
        {
            "_id": "ord_002_001",
            "customer_id": "cust_jane_smith",
            "order_date": datetime.utcnow() - timedelta(days=5),
            "items": [
                {"product_id": "prod_usb_cable", "quantity": 1, "price": 12.99}
            ],
            "total_amount": 12.99,
            "status": "completed",
            "shipping_address": "456 Oak Avenue, Chicago, IL 60601",
            "payment_method": "paypal",
            "shipping_cost": 5.99,
            "tax": 0.98,
            "discount_applied": 0,
            "fulfillment_date": datetime.utcnow() - timedelta(days=3)
        },
        {
            "_id": "ord_003_001",
            "customer_id": "cust_robert_wilson",
            "order_date": datetime.utcnow() - timedelta(days=25),
            "items": [
                {"product_id": "prod_wireless_headphones", "quantity": 2, "price": 79.99}
            ],
            "total_amount": 159.98,
            "status": "completed",
            "shipping_address": "789 Pine Road, Boston, MA 02101",
            "payment_method": "debit_card",
            "shipping_cost": 12.99,
            "tax": 12.80,
            "discount_applied": 0,
            "fulfillment_date": datetime.utcnow() - timedelta(days=23)
        }
    ]


# ============================================================================
# 1. CONNECTION & MCP SERVER TESTS
# ============================================================================

class TestMongoDBMCPConnection:
    """Test MongoDB MCP Server connectivity - Validates Technological Implementation"""

    @pytest.mark.asyncio
    async def test_mcp_server_connects(self, mcp_server):
        """Verify MCP server establishes MongoDB connection"""
        assert mcp_server.client is not None
        assert mcp_server.db is not None

    @pytest.mark.asyncio
    async def test_database_ping(self, mcp_server):
        """Test database connectivity with ping command"""
        result = await mcp_server.ping()
        assert result is True

    @pytest.mark.asyncio
    async def test_list_databases(self, mcp_server):
        """Test listing available databases"""
        databases = await mcp_server.list_databases()
        assert isinstance(databases, list)
        assert len(databases) > 0

    @pytest.mark.asyncio
    async def test_list_collections(self, mcp_server, retail_products):
        """Test listing collections in database"""
        await mcp_server.insert_many("products", retail_products)
        collections = await mcp_server.list_collections()
        assert "products" in collections

    @pytest.mark.asyncio
    async def test_connection_pooling(self, mcp_server):
        """Test connection pool is properly managed"""
        # Make multiple concurrent requests
        tasks = [
            mcp_server.ping(),
            mcp_server.ping(),
            mcp_server.ping()
        ]
        results = await asyncio.gather(*tasks)
        assert all(results)

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self, mongodb_uri):
        """Test graceful handling of connection timeouts"""
        invalid_uri = "mongodb://invalid-host:27017"
        server = MongoDBMCPServer(
            mongodb_uri=invalid_uri,
            database_name="test"
        )
        
        with pytest.raises((ConnectionFailure, ServerSelectionTimeoutError)):
            await server.connect()


# ============================================================================
# 2. CRUD OPERATIONS - CREATE (INSERT)
# ============================================================================

class TestRetailProductCreation:
    """Test product insertion - Real-world retail scenario"""

    @pytest.mark.asyncio
    async def test_insert_single_product(self, mcp_server, retail_products):
        """Agent: Insert a single product to inventory"""
        product = retail_products[0]
        result = await mcp_server.insert_one("products", product)
        assert result.inserted_id == "prod_wireless_headphones"

    @pytest.mark.asyncio
    async def test_insert_multiple_products(self, mcp_server, retail_products):
        """Agent: Bulk insert products to initialize inventory"""
        result = await mcp_server.insert_many("products", retail_products)
        assert len(result.inserted_ids) == 3
        assert "prod_wireless_headphones" in result.inserted_ids

    @pytest.mark.asyncio
    async def test_insert_product_with_validation(self, mcp_server):
        """Agent: Validate product data before insertion"""
        product = {
            "_id": "prod_test",
            "name": "Test Product",
            "category": "Electronics",
            "price": 99.99,
            "stock": 50,
            "sku": "TEST-001"
        }
        result = await mcp_server.insert_one("products", product)
        assert result.inserted_id == "prod_test"

    @pytest.mark.asyncio
    async def test_insert_duplicate_product_fails(self, mcp_server, retail_products):
        """Agent: Prevent duplicate product IDs"""
        product = retail_products[0]
        await mcp_server.insert_one("products", product)
        
        with pytest.raises(DuplicateKeyError):
            await mcp_server.insert_one("products", product)

    @pytest.mark.asyncio
    async def test_create_customer(self, mcp_server, retail_customers):
        """Agent: Register new customer in system"""
        customer = retail_customers[0]
        result = await mcp_server.insert_one("customers", customer)
        assert result.inserted_id == "cust_john_doe"

    @pytest.mark.asyncio
    async def test_bulk_create_customers(self, mcp_server, retail_customers):
        """Agent: Bulk register customers (e.g., import from external system)"""
        result = await mcp_server.insert_many("customers", retail_customers)
        assert len(result.inserted_ids) == 3

    @pytest.mark.asyncio
    async def test_create_order(self, mcp_server, retail_products, retail_customers, retail_orders):
        """Agent: Create new order in system"""
        await mcp_server.insert_many("products", retail_products)
        await mcp_server.insert_many("customers", retail_customers)
        
        order = retail_orders[0]
        result = await mcp_server.insert_one("orders", order)
        assert result.inserted_id == "ord_001_001"

    @pytest.mark.asyncio
    async def test_bulk_create_orders(self, mcp_server, retail_products, retail_customers, retail_orders):
        """Agent: Bulk insert orders"""
        await mcp_server.insert_many("products", retail_products)
        await mcp_server.insert_many("customers", retail_customers)
        
        result = await mcp_server.insert_many("orders", retail_orders)
        assert len(result.inserted_ids) == 4


# ============================================================================
# 3. CRUD OPERATIONS - READ (QUERIES)
# ============================================================================

class TestRetailProductQueries:
    """Test product queries - Core agent capabilities"""

    @pytest.mark.asyncio
    async def test_find_product_by_id(self, mcp_server, retail_products):
        """Agent: Retrieve product details by ID"""
        await mcp_server.insert_many("products", retail_products)
        
        product = await mcp_server.find_one("products", {"_id": "prod_wireless_headphones"})
        assert product is not None
        assert product["name"] == "Premium Wireless Headphones"
        assert product["price"] == 79.99

    @pytest.mark.asyncio
    async def test_find_products_by_category(self, mcp_server, retail_products):
        """Agent: Find all products in a category"""
        await mcp_server.insert_many("products", retail_products)
        
        accessories = await mcp_server.find("products", {"category": "Accessories"})
        assert len(accessories) == 2
        for product in accessories:
            assert product["category"] == "Accessories"