from flask import Flask, request, jsonify
from google.cloud import aiplatform
import os
from mongodb_mcp_server import MongoDBMCPServer

app = Flask(__name__)

# Config
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
AGENT_ID = os.getenv("AGENT_ID")
LOCATION = "us-central1"

# Initialize
aiplatform.init(project=PROJECT_ID, location=LOCATION)
mcp_server = MongoDBMCPServer()

@app.route('/mcp', methods=['POST'])
async def handle_mcp():
    """MCP endpoint for Tool Calls from Agent Builder"""
    data = request.json
    tool_name = data.get("tool")
    tool_input = data.get("input", {})
    
    # MongoDB MCP Server se result fetch karo
    result = await mcp_server.handle_tool_call(tool_name, tool_input)
    return jsonify(result)

@app.route('/query', methods=['POST'])
def query_agent():
    """Frontend/User query ko Agent Builder tak bhejo"""
    try:
        data = request.json
        user_message = data.get("message", "")
        
        # Agent Builder Client
        client = aiplatform.gapic.AgentsClient()
        agent_path = client.agent_path(PROJECT_ID, LOCATION, AGENT_ID)
        
        response = client.generate_response(
            agent=agent_path,
            input=user_message
        )
        
        return jsonify({
            "status": "success",
            "response": response.output_text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)