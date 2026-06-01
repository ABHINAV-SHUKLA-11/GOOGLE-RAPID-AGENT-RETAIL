"""
Test suite for MongoDB Retail Agent

This package contains unit tests, integration tests, and performance tests
for the MongoDB Retail Agent system including:
- Agent core functionality and task planning
- MongoDB MCP Server integration
- Retail use case scenarios
- Performance and scalability tests
"""

import pytest
import os
from pathlib import Path

# Set test environment variables
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")

# Add src directory to path for imports
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in __path__:
    import sys
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def test_config():
    """
    Session-scoped fixture providing test configuration
    """
    from src.config import Config
    return Config


@pytest.fixture(scope="session")
def mongodb_test_uri():
    """
    Provides MongoDB test database URI
    Uses Docker Compose MongoDB or environment variable
    """
    return os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017/retail_agent_test")


@pytest.fixture(scope="function")
def cleanup_mongodb(mongodb_test_uri):
    """
    Fixture to clean up test database after each test
    """
    yield
    from pymongo import MongoClient
    try:
        client = MongoClient(mongodb_test_uri, serverSelectionTimeoutMS=2000)
        client.drop_database("retail_agent_test")
        client.close()
    except Exception as e:
        print(f"Cleanup warning: {e}")


def pytest_configure(config):
    """
    pytest hook for initial configuration
    """
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (deselect with '-m \"not asyncio\"')"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "retail: mark test as retail scenario test"
    )


def pytest_collection_modifyitems(config, items):
    """
    pytest hook to add markers based on test location
    """
    for item in items:
        # Add integration marker for certain tests
        if "mongodb" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "retail" in item.nodeid:
            item.add_marker(pytest.mark.retail)
