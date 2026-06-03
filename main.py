from flask import Flask, request, jsonify
from google.cloud import aiplatform

from google.cloud.aiplatform_v1beta1.services.agents_client import AgentsClient
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
AGENT_ID = os.getenv("AGENT_ID")
LOCATION = "us-central1"
PORT = int(os.getenv("PORT", 8080))

logger.info(f"Flask app initializing - PROJECT_ID={PROJECT_ID}, AGENT_ID={AGENT_ID}")

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return jsonify({
        "status": "running",
        "service": "Flask AI Agent",
        "endpoints": {
            "/health": "GET",
            "/query": "POST",
            "/mcp/tools": "GET"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    logger.info("Health check called")
    return jsonify({
        "status": "healthy",
        "service": "Flask AI Agent",
        "timestamp": str(os.getcwd())
    }), 200

@app.route('/query', methods=['POST'])
def query_agent():
    """Query the AI Agent"""
    try:
        logger.info("Query endpoint called")
        
        data = request.get_json()
        if not data:
            logger.warning("Empty request body")
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
            logger.error("GCP credentials not set")
            return jsonify({
                "status": "error",
                "message": "GCP credentials not configured"
            }), 500
        
        try:
            logger.info("Initializing AI Platform client")
      
client = AgentsClient(client_options={"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"})
            agent_path = client.agent_path(PROJECT_ID, LOCATION, AGENT_ID)
            
            session_id = data.get("session_id", f"session-{os.urandom(4).hex()}")
            logger.info(f"Sending query to agent - Session: {session_id}")
            
            response = client.generate_response(
                agent=agent_path,
                session_id=session_id,
                input=user_message
            )
            
            logger.info(f"Agent response received successfully")
            
            return jsonify({
                "status": "success",
                "response": response.output_text,
                "session_id": session_id
            }), 200
            
        except Exception as e:
            logger.error(f"Agent API error: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": f"Agent API error: {str(e)}"
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    """Get MCP tools"""
    logger.info("MCP tools endpoint called")
    return jsonify({
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
    }), 200

@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 Server Error: {str(e)}", exc_info=True)
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info(f"🚀 Starting Flask on 0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
