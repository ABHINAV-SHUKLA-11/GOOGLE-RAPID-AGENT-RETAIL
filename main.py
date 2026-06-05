from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os, logging, sys, json
from bson import ObjectId
import mimetypes

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv("PORT", 8080))
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "retail_db")

mongo_client = None
db = None

def get_db():
    global mongo_client, db
    if db is None:
        mongo_client = MongoClient(MONGODB_URI)
        db = mongo_client[DB_NAME]
    return db

def smart_agent(user_message, products, orders):
    msg = user_message.lower()
    if any(w in msg for w in ["product", "item", "stock", "inventory", "catalogue"]):
        if products:
            lines = [f"- {p.get('name','?')} | Price: ${p.get('price','N/A')} | Stock: {p.get('stock','N/A')} units" for p in products]
            return f"Here are {len(products)} products in our inventory:\n" + "\n".join(lines)
        return "No products found in inventory. Add products using POST /products."
    elif any(w in msg for w in ["order", "purchase", "buy", "transaction"]):
        if orders:
            lines = [f"- {o.get('customer','Unknown')} ordered {o.get('product','?')} x{o.get('quantity','?')} | Status: {o.get('status','processing')} | Total: ${o.get('total','N/A')}" for o in orders]
            return f"Found {len(orders)} recent orders:\n" + "\n".join(lines)
        return "No orders found. Create orders using POST /orders."
    elif any(w in msg for w in ["summary", "report", "dashboard", "overview"]):
        return f"Store Overview:\n- Total Products: {len(products)}\n- Recent Orders: {len(orders)}\n- Latest Status: {orders[0].get('status','N/A') if orders else 'No orders yet'}"
    elif any(w in msg for w in ["hello", "hi", "help", "what"]):
        return f"Hello! I am your Retail AI Agent powered by Google Cloud Run + MongoDB.\nI can help you with:\n- Product inventory ({len(products)} products)\n- Order management ({len(orders)} orders)\n- Store analytics\nJust ask me anything!"
    else:
        return f"Retail Store has {len(products)} products and {len(orders)} orders. Ask me about products, orders, or store summary!"

@app.route('/', methods=['GET'])
def root():
    return {"status": "running", "service": "Retail AI Agent", "team": "Team Cloud Craft", "powered_by": "Google Cloud Run + MongoDB"}, 200

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
        database = get_db()
        products = list(database.products.find({}, {"_id": 0}).limit(10))
        orders = list(database.orders.find({}, {"_id": 0}).limit(5))
        reply = smart_agent(user_message, products, orders)
        return {"status": "success", "response": reply, "session_id": session_id}, 200
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}, 500

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = list(get_db().products.find({}, {"_id": 0}).limit(20))
        return {"status": "success", "products": products, "count": len(products)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/products', methods=['POST'])
def add_product():
    try:
        result = get_db().products.insert_one(request.get_json())
        return {"status": "success", "product_id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        orders = list(get_db().orders.find({}, {"_id": 0}).limit(20))
        return {"status": "success", "orders": orders}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        result = get_db().orders.insert_one(request.get_json())
        return {"status": "success", "order_id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    return {
        "get_products": {"description": "Query products from MongoDB", "params": ["filter"]},
        "create_order": {"description": "Create new order", "params": ["customer", "product", "quantity"]},
        "update_inventory": {"description": "Update stock levels", "params": ["product_id", "quantity"]},
        "check_order_status": {"description": "Check order status", "params": ["order_id"]}
    }, 200

@app.errorhandler(404)
def not_found(e):
    return {"status": "error", "message": "Endpoint not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)

@app.route('/ui', methods=['GET'])
def serve_ui():
    return open('index.html').read(), 200, {'Content-Type': 'text/html'}
