from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import os, logging, sys, json, re
from bson import ObjectId
from datetime import datetime

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

RATINGS = {
    "Nike Air Max": {"rating": 4.5, "reviews": 234},
    "Adidas Ultraboost": {"rating": 4.7, "reviews": 189},
    "Levi Jeans": {"rating": 4.2, "reviews": 156},
    "Puma Running Shoes": {"rating": 4.3, "reviews": 98}
}

def enrich(products):
    for p in products:
        r = RATINGS.get(p.get("name",""), {"rating": 4.0, "reviews": 50})
        p["rating"] = r["rating"]
        p["reviews"] = r["reviews"]
    return products

def fuzzy_match(product_name, products):
    product_name = product_name.lower().strip()
    # Exact match
    for p in products:
        if product_name in p.get("name","").lower():
            return p
    # Word by word match
    words = [w for w in product_name.split() if len(w) > 2]
    for p in products:
        pname = p.get("name","").lower()
        if any(w in pname for w in words):
            return p
    return None

def make_invoice(o):
    sub = o.get("total", 0)
    tax = round(sub * 0.18, 2)
    grand = round(sub + tax, 2)
    pay = o.get("payment_method", "cash").upper()
    pay_status = o.get("payment_status", "pending").upper()
    return (
        f"🧾 INVOICE\n"
        f"{'='*30}\n"
        f"Order ID  : {o['order_id']}\n"
        f"Customer  : {o['customer']}\n"
        f"Product   : {o['product']} x{o['quantity']}\n"
        f"{'-'*30}\n"
        f"Subtotal  : ${sub}\n"
        f"GST (18%) : ${tax}\n"
        f"{'='*30}\n"
        f"GRAND TOTAL: ${grand}\n"
        f"Payment   : {pay} (COD)\n"
        f"Pay Status: {pay_status}\n"
        f"Order     : {o['status'].upper()}\n"
        f"{'='*30}\n"
        f"Thank you for shopping with us! 🙏"
    )

def agent(msg_original, products, orders, database):
    msg = msg_original.lower().strip()
    products = enrich(products)

    # 1. CREATE ORDER
    if re.search(r'create order|place order|new order', msg):
        name = re.search(r'for\s+(.+?)\s+product', msg_original, re.I)
        prod = re.search(r'product\s+(.+?)(?:\s+qty|$)', msg_original, re.I)
        qty = re.search(r'qty\s+(\d+)', msg_original, re.I)
        customer = name.group(1).strip().title() if name else "Walk-in Customer"
        product_name = prod.group(1).strip() if prod else ""
        quantity = int(qty.group(1)) if qty else 1
        matched = fuzzy_match(product_name, products)
        total = round(matched["price"] * quantity, 2) if matched else 0
        order = {
            "order_id": f"ORD-{datetime.now().strftime('%d%H%M%S')}",
            "customer": customer,
            "product": matched["name"] if matched else product_name,
            "quantity": quantity,
            "status": "processing",
            "total": total,
            "payment_method": "cash",
            "payment_status": "pending",
            "created_at": datetime.now().isoformat()
        }
database.orders.insert_one(order)
tax = round(total * 0.18, 2)

        grand = round(total + tax, 2)
        return (
            f"✅ Order Created!\n"
            f"- ID      : {order['order_id']}\n"
            f"- Customer: {customer}\n"
            f"- Product : {order['product']}\n"
            f"- Qty     : {quantity}\n"
            f"- Subtotal: ${total}\n"
            f"- GST 18% : ${tax}\n"
            f"- Total   : ${grand}\n"
            f"- Payment : Cash on Delivery\n"
            f"- Status  : Processing"
        )

    # 2. DELETE ORDER
    if re.search(r'delete order|cancel order|remove order', msg):
        ord_match = re.search(r'ORD-[\w]+', msg_original.upper())
        if ord_match:
            oid = ord_match.group(0)
            r = database.orders.delete_one({"order_id": oid})
            return f"🗑️ Order {oid} deleted!" if r.deleted_count else f"Order {oid} not found."
        name_match = re.search(r'(?:delete|cancel|remove)\s+order\s+(?:for\s+)?(.+)', msg_original, re.I)
        if name_match:
            cname = name_match.group(1).strip()
            if len(cname) < 3:
                return "Please provide valid customer name (min 3 characters)."
            r = database.orders.delete_many({"customer": {"$regex": cname, "$options": "i"}})
            return f"🗑️ Deleted {r.deleted_count} order(s) for {cname}!" if r.deleted_count else f"No orders for {cname}."
        return "Specify Order ID (e.g. ORD-001) or full customer name."

    # 3. UPDATE ORDER STATUS
    if re.search(r'update order|mark.*delivered|mark.*pending|mark.*processing|change status', msg):
        ord_match = re.search(r'ORD-[\w]+', msg_original.upper())
        status_match = re.search(r'(?:as|to)\s+(delivered|pending|processing|cancelled)', msg)
        if ord_match and status_match:
            oid = ord_match.group(0)
            new_status = status_match.group(1)
            database.orders.update_one({"order_id": oid}, {"$set": {"status": new_status}})
            return f"✅ Order {oid} status updated to {new_status}!"
        return "Specify Order ID and status (e.g. 'mark ORD-001 as delivered')"

    # 4. RESTOCK
    if re.search(r'restock|add stock|update stock', msg):
        qty_match = re.search(r'(\d+)', msg)
        qty = int(qty_match.group(1)) if qty_match else 0
        for p in products:
            if p.get("name","").lower() in msg:
                database.products.update_one({"name": p["name"]}, {"$inc": {"stock": qty}})
                return f"✅ {p['name']} restocked! +{qty} units added."
        return "Specify product name and quantity."

    # 5. LOW STOCK
    if re.search(r'low stock|running low|stock alert|reorder', msg):
        low = [p for p in products if p.get("stock", 0) < 30]
        if low:
            lines = [f"- {p['name']} | Stock: {p['stock']} units ⚠️" for p in low]
            return f"⚠️ Low Stock Alert! {len(low)} products:\n" + "\n".join(lines)
        return "✅ All products have sufficient stock!"

    # 6. REVENUE
    if re.search(r'revenue|earning|total sales|income', msg):
        total = sum(o.get("total", 0) for o in orders)
        delivered = len([o for o in orders if o.get("status") == "delivered"])
        processing = len([o for o in orders if o.get("status") == "processing"])
        pending = len([o for o in orders if o.get("status") == "pending"])
        return (
            f"💰 Revenue Report:\n"
            f"- Total Revenue: ${round(total,2)}\n"
            f"- Total Orders : {len(orders)}\n"
            f"- Delivered    : {delivered}\n"
            f"- Processing   : {processing}\n"
            f"- Pending      : {pending}"
        )

    # 7. BILL/INVOICE
    if re.search(r'bill|invoice|receipt', msg):
        ord_match = re.search(r'ORD-[\w]+', msg_original.upper())
        if ord_match:
            oid = ord_match.group(0)
            o = next((x for x in orders if x.get("order_id") == oid), None)
            if o:
                return make_invoice(o)
            return f"Order {oid} not found."
        name_match = re.search(r'(?:bill|invoice|receipt)\s+(?:for\s+)?(.+)', msg_original, re.I)
        if name_match:
            cname = name_match.group(1).strip()
            matched = [o for o in orders if cname.lower() in o.get("customer","").lower()]
            if matched:
                if len(matched) == 1:
                    return make_invoice(matched[0])
                else:
                    bills = []
                    for o in matched:
                        sub = o.get("total", 0)
                        tax = round(sub * 0.18, 2)
                        grand = round(sub + tax, 2)
                        bills.append(f"- {o['order_id']} | {o['product']} | ${sub} + GST ${tax} = ${grand}")
                    return f"🧾 Bills for {cname} ({len(matched)} orders):\n" + "\n".join(bills)
            return f"No orders found for {cname}."

    # 8. TOP RATED
    if re.search(r'best|top rated|popular|recommended|highest rated', msg):
        sorted_p = sorted(products, key=lambda x: x.get("rating",0), reverse=True)
        lines = [f"- {p['name']} | ⭐{p['rating']} ({p['reviews']} reviews) | ${p['price']}" for p in sorted_p[:3]]
        return "🏆 Top Rated Products:\n" + "\n".join(lines)

    # 9. PRICE FILTER
    price_match = re.search(r'under\s*\$?(\d+)', msg)
    if price_match:
        limit = float(price_match.group(1))
        filtered = [p for p in products if p.get("price",0) <= limit]
        if filtered:
            lines = [f"- {p['name']} | ${p['price']} | ⭐{p['rating']} | Stock: {p['stock']}" for p in filtered]
            return f"🔍 Products under ${limit}:\n" + "\n".join(lines)
        return f"No products under ${limit}."

    # 10. RATING FILTER
    rating_match = re.search(r'rating\s*(?:above|over|more than)?\s*(\d+\.?\d*)', msg)
    if rating_match:
        min_r = float(rating_match.group(1))
        filtered = [p for p in products if p.get("rating",0) >= min_r]
        if filtered:
            lines = [f"- {p['name']} | ⭐{p['rating']} | ${p['price']}" for p in filtered]
            return f"⭐ Products rated {min_r}+:\n" + "\n".join(lines)
        return f"No products with rating {min_r}+."

    # 11. CATEGORY FILTER
    for cat in ["shoes", "clothing", "electronics", "accessories"]:
        if cat in msg:
            filtered = [p for p in products if cat in p.get("category","").lower()]
            if filtered:
                lines = [f"- {p['name']} | ${p['price']} | ⭐{p['rating']}" for p in filtered]
                return f"👟 {cat.title()} ({len(filtered)} items):\n" + "\n".join(lines)

    # 12. ORDERS FOR CUSTOMER
    if re.search(r'orders?\s+for\s+|show.*orders.*for', msg):
        name_match = re.search(r'(?:orders?\s+for|show.*for)\s+(.+)', msg_original, re.I)
        if name_match:
            cname = name_match.group(1).strip()
            matched = [o for o in orders if cname.lower() in o.get("customer","").lower()]
            if matched:
                lines = [f"- {o['order_id']} | {o['product']} x{o['quantity']} | {o['status']} | ${o['total']}" for o in matched]
                return f"📋 Orders for {cname}:\n" + "\n".join(lines)
            return f"No orders for {cname}."

    # 13. WHO BOUGHT
    if re.search(r'who bought|who ordered|sales of', msg):
        words = [w for w in msg.split() if len(w) > 3]
        matched_product = None
        for p in products:
            pname = p['name'].lower()
            if any(w in pname for w in words):
                matched_product = p
                break
        if matched_product:
            matched = [o for o in orders if matched_product['name'].lower() in o.get("product","").lower()]
            if matched:
                lines = [f"- {o['customer']} | Qty: {o['quantity']} | ${o['total']}" for o in matched]
                return f"🛒 {matched_product['name']} buyers:\n" + "\n".join(lines)
            return f"No one has bought {matched_product['name']} yet."
        return "Please specify a product name."

    # 14. DASHBOARD
    if re.search(r'dashboard|summary|overview|analytics|report', msg):
        total_rev = sum(o.get("total",0) for o in orders)
        low = [p for p in products if p.get("stock",0) < 30]
        best = max(products, key=lambda x: x.get("rating",0)) if products else {}
        return (
            f"📊 Store Dashboard:\n"
            f"- Products   : {len(products)}\n"
            f"- Orders     : {len(orders)}\n"
            f"- Revenue    : ${round(total_rev,2)}\n"
            f"- Low Stock  : {len(low)} items\n"
            f"- Top Product: {best.get('name','N/A')} ⭐{best.get('rating','')}"
        )

    # 15. ALL ORDERS
    if re.search(r'all orders|show orders|list orders|orders', msg):
        if orders:
            lines = [f"- {o.get('order_id','?')} | {o.get('customer','?')} | {o.get('product','?')} x{o.get('quantity','?')} | {o.get('status','?')} | ${o.get('total','?')}" for o in orders]
            return f"🛒 All Orders ({len(orders)}):\n" + "\n".join(lines)
        return "No orders found."

    # 16. ALL PRODUCTS
    if re.search(r'all products|show products|list products|products|inventory', msg):
        if products:
            lines = [f"- {p['name']} | ${p['price']} | ⭐{p['rating']} | Stock: {p['stock']}" for p in products]
            return f"📦 Inventory ({len(products)} products):\n" + "\n".join(lines)
        return "No products found."

    # SPECIFIC PRODUCT INFO
    if re.search(r'stock of|price of|info of|details of|tell me about|about product', msg):
        for p in products:
            if p.get('name','').lower() in msg:
                return f"📦 {p['name']}\n- Price: ${p['price']}\n- Stock: {p['stock']} units\n- Category: {p.get('category','N/A')}\n- Rating: ⭐{p['rating']} ({p['reviews']} reviews)"
        words = msg.split()
        for word in words:
            if len(word) > 3:
                matched = next((p for p in products if word in p.get('name','').lower()), None)
                if matched:
                    return f"📦 {matched['name']}\n- Price: ${matched['price']}\n- Stock: {matched['stock']} units\n- Category: {matched.get('category','N/A')}\n- Rating: ⭐{matched['rating']} ({matched['reviews']} reviews)"
        return "Product not found. Type 'show all products' to see available items."

    # 17A. PAYMENT METHOD
    if re.search(r'payment method|how to pay|payment options|pay by|payment mode', msg):
        return (
            "💳 Payment Options:\n\n"
            "💵 Cash on Delivery (COD)\n"
            "- Pay when order arrives\n"
            "- No extra charges\n\n"
            "💳 Card Payment\n"
            "- Debit/Credit Card accepted\n"
            "- Visa, Mastercard, Rupay\n\n"
            "📱 UPI Payment\n"
            "- Google Pay, PhonePe, Paytm\n"
            "- Instant payment\n"
        )

    # 17B. PAYMENT STATUS
    if re.search(r'payment status|is payment done|payment pending|payment complete', msg):
        ord_match = re.search(r'ORD-[\w]+', msg_original.upper())
        if ord_match:
            oid = ord_match.group(0)
            o = next((x for x in orders if x.get("order_id") == oid), None)
            if o:
                return (
                    f"💳 Payment Status for {oid}:\n"
                    f"- Customer      : {o.get('customer','?')}\n"
                    f"- Total         : ${o.get('total','?')}\n"
                    f"- Payment Method: {o.get('payment_method','Cash').upper()}\n"
                    f"- Payment Status: {o.get('payment_status','Pending').upper()}\n"
                    f"- Order Status  : {o.get('status','?').upper()}"
                )
            return f"Order {oid} not found."
        return "Please specify Order ID (e.g. 'payment status ORD-001')"

    # 17. HELLO/HELP
    if re.search(r'hello|hi|help|what can you', msg):
        return (
            "👋 Hello! I am your Retail AI Agent!\n\n"
            "🔍 PRODUCTS:\n"
            "- show all products\n"
            "- products under $100\n"
            "- top rated products\n"
            "- show shoes / clothing\n"
            "- rating above 4.5\n\n"
            "🛒 ORDERS:\n"
            "- show all orders\n"
            "- orders for [customer name]\n"
            "- create order for [name] product [item] qty [n]\n"
            "- delete order [ORD-ID or customer name]\n"
            "- mark ORD-001 as delivered\n\n"
            "🧾 BILLING:\n"
            "- bill for [customer name]\n"
            "- bill for ORD-001\n\n"
            "💳 PAYMENTS:\n"
            "- payment method\n"
            "- payment status ORD-001\n\n"
            "📊 ANALYTICS:\n"
            "- revenue report\n"
            "- store dashboard\n"
            "- low stock alerts\n"
            "- who bought Nike Air Max\n\n"
            "Ask me anything!"
        )

    # DEFAULT
    total_rev = sum(o.get("total",0) for o in orders)
    return f"🏪 Store: {len(products)} products | {len(orders)} orders | Revenue: ${round(total_rev,2)}\nType 'help' to see all commands!"


@app.route('/', methods=['GET'])
def root():
    return {"status": "running", "service": "Retail AI Agent", "team": "Team Cloud Craft"}, 200

@app.route('/health', methods=['GET'])
def health():
    try:
        get_db().command("ping")
        mongo_status = "connected"
    except:
        mongo_status = "disconnected"
    return {"status": "healthy", "mongodb": mongo_status}, 200

@app.route('/ui', methods=['GET'])
def serve_ui():
    return open('index.html').read(), 200, {'Content-Type': 'text/html'}

@app.route('/query', methods=['POST'])
def query_agent():
    try:
        data = request.get_json()
        if not data or not data.get("message"):
            return {"status": "error", "message": "Message required"}, 400
        user_message = data["message"]
        session_id = data.get("session_id", f"session-{os.urandom(4).hex()}")
        database = get_db()
        products = list(database.products.find({}, {"_id": 0}).limit(10))
        orders = list(database.orders.find({}, {"_id": 0}).limit(20))
        reply = agent(user_message, products, orders, database)
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
        formatted = [{"order_id": o.get("order_id",""), "customer": o.get("customer",""), "product": o.get("product",""), "quantity": o.get("quantity",0), "status": o.get("status",""), "total": o.get("total",0)} for o in orders]
        return {"status": "success", "orders": formatted, "count": len(formatted)}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        result = get_db().orders.insert_one(request.get_json())
        return {"status": "success", "order_id": str(result.inserted_id)}, 201
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        result = get_db().orders.delete_one({"order_id": order_id})
        return {"status": "success"} if result.deleted_count else {"status": "error", "message": "Not found"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        get_db().orders.update_one({"order_id": order_id}, {"$set": request.get_json()})
        return {"status": "success", "message": "Updated"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route('/mcp/tools', methods=['GET'])
def get_mcp_tools():
    return {
        "get_products": {"description": "Get all products with ratings"},
        "get_orders": {"description": "Get all orders"},
        "create_order": {"description": "Create new order"},
        "delete_order": {"description": "Delete order by ID or customer"},
        "update_order": {"description": "Update order status"},
        "get_revenue": {"description": "Get revenue report"},
        "get_low_stock": {"description": "Get low stock alerts"},
        "generate_bill": {"description": "Generate invoice for order"}
    }, 200

@app.errorhandler(404)
def not_found(e):
    return {"status": "error", "message": "Not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
