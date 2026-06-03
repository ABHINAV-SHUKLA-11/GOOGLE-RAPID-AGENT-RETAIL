from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os, logging, sys, json
from bson import ObjectId

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Environment variables
PORT = int(os.getenv("PORT", 8080))
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "retail_db")

# MongoDB connection
mongo_client = None
db = None

def get_db():
    global mongo_client, db
    if db is None:
        mongo_client = MongoClient(MONGODB_URI)
        db = mongo_client[DB_NAME]
    return db

# ---- AI Agent (Google AI Studio) ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def query_gemini_agent(user_message, mongo_context=""):
    import requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    system_prompt = f"""You are a smart retail AI agent. You help users with:
- Finding products
- Checking inventory
- Creating orders
- Tracking order status

Current data from MongoDB:
{mongo_context}

Answer based on this data. Be concise and helpful."""

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": system_prompt + "\n\nUser: " + user_message}]}
        ]
    }
    
    resp = requests.post(url, json=payload)
    result = resp.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]

# ---- Routes ----

@app.route('/', methods=['GET'])
def root():
    return {"status": "running", "service": "Retail AI Agent",
            "endpoints": {"/health": "GET", "/query": "POST", "/mcp/tools": "GET"}}, 200

@app.route('/health', methods=['GET'])
def health():
    try:
        get_db().command("ping")
        mongo_status = "connected"
    except:
        mongo_status = "disconnected"
    return {"status": "healthy", "mongodb": mongo_status}, 200

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        data = request.get_json()
        if not data or not data.get("message"):
            return {"status": "error", "message": "Message field is required"}, 400

        user_message = data["message"]
        session_id = data.get("session_id", f"session-{os.urandom(4).hex()}")

        # MongoDB se context fetch karo
        database = get_db()
        
        # Products fetch karo
        products = list(database.products.find({}, {"_id": 0}).limit(10))
        orders = list(database.orders.find({}, {"_id": 0}).limit(5))
        
        mongo_context = f"Products: {json.dumps(products)}\nRecent Orders: {json.dumps(orders)}"
        
        # Gemini se answer lo
        reply = query_gemini_agent(user_message, mongo_context)

        return {"status": "success", "response": reply, "session_id": session_id}, 200

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}, 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    return {
        "get_products": {"description": "Query products from MongoDB", "params": ["filter"]},
        "create_order": {"description": "Create order", "params": ["customer_id", "products"]},
        "update_inventory": {"description": "Update stock", "params": ["product_id", "quantity"]},
        "check_order_status": {"description": "Check order status", "params": ["order_id"]}
    }, 200

@app.route('/products', methods=['GET'])
def get_products():
    try:
        db = get_db()
        products = list(db.products.find({}, {"_id": 0}).limit(20))
        return {"status": "success", "products": products, "count": len(products)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        db = get_db()
        orders = list(db.orders.find({}, {"_id": 0}).limit(20))
        return {"status": "success", "orders": orders}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        db = get_db()
        result = db.orders.insert_one(data)
        return {"status": "success", "order_id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.errorhandler(404)
def not_found(e):
    return {"status": "error", "message": "Endpoint not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
