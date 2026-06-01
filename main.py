from flask import Flask, request, jsonify
from google.cloud import aiplatform
import os
import json

app = Flask(__name__)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
AGENT_ID = os.getenv("AGENT_ID")
LOCATION = "us-central1"

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        client = aiplatform.gapic.AgentsClient()
        agent_path = client.agent_path(PROJECT_ID, LOCATION, AGENT_ID)
        
        session_id = data.get("session_id", "default")
        
        response = client.generate_response(
            agent=agent_path,
            session_id=session_id,
            input=user_message
        )
        
        return jsonify({
            "status": "success",
            "response": response.output_text,
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
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
            "description": "Check order",
            "params": ["order_id"]
        }
    }
    return jsonify(tools)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)