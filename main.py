from flask import Flask, request, jsonify
from google.cloud import aiplatform
import os
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
AGENT_ID = os.getenv("AGENT_ID")
LOCATION = "us-central1"
PORT = int(os.getenv("PORT", 8080))

logger.info(f"Starting Flask app with PROJECT_ID={PROJECT_ID}, AGENT_ID={AGENT_ID}, PORT={PORT}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health check called")
    return jsonify({
        "status": "healthy",
        "project_id": PROJECT_ID if PROJECT_ID else "NOT SET",
        "agent_id": AGENT_ID if AGENT_ID else "NOT SET"
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Flask AI Agent API is running",
        "endpoints": {
            "/health": "GET - Health check",
            "/query": "POST - Query the AI Agent",
            "/mcp/tools": "GET - Get available tools"
        }
    }), 200

@app.route('/query', methods=['POST'])
def query_agent():
    """Query the AI Agent"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Empty request body received")
            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty"
            }), 400
        
        user_message = data.get("message", "")
        
        if not user_message:
            logger.warning("Message field missing")
            return jsonify({
                "status": "error",
                "message": "Message field is required"
            }), 400
        
        if not PROJECT_ID or not AGENT_ID:
            logger.error("GCP credentials not configured")
            return jsonify({
                "status": "error",
                "message": "GCP_PROJECT_ID or AGENT_ID not configured"
            }), 500
        
        # Initialize client
        try:
            client = aiplatform.gapic.AgentsClient()
            agent_path = client.agent_path(PROJECT_ID, LOCATION, AGENT_ID)
        except Exception as e:
            logger.error(f"Failed to initialize GCP client: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"GCP client initialization failed: {str(e)}"
            }), 500
        
        session_id = data.get("session_id", "default-session")
        
        logger.info(f"Query received - Message: {user_message[:100]}, Session: {session_id}")
        
        # Call the agent
        try:
            response = client.generate_response(
                agent=agent_path,
                session_id=session_id,
                input=user_message
            )
            
            logger.info(f"Agent response generated successfully")
            
            return jsonify({
                "status": "success",
                "response": response.output_text,
                "session_id": session_id
            }), 200
            
        except Exception as e:
            logger.error(f"Agent API call failed: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Agent API call failed: {str(e)}"
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in query_agent: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    """Get available MCP tools"""
    logger.info("Tools endpoint called")
    tools = {
        "get_products": {
            "description": "Query products from MongoDB",
            "params": ["filter"]
        },
        "create_order": {
            "description": "Create order",
            "params": ["customer_id", "products"]
        },
        "update_inventory": {
            "description": "Update stock",
            "params": ["product_id", "quantity"]
        },
        "check_order_status": {
            "description": "Check order status",
            "params": ["order_id"]
        }
    }
    return jsonify(tools), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "GET /",
            "GET /health",
            "POST /query",
            "GET /mcp/tools"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting Flask app on 0.0.0.0:{PORT}")
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True
    )
