def smart_agent(user_message, products, orders):
    msg = user_message.lower()

    # PRICE FILTER - "under $100", "below 50", "less than 80"
    import re
    price_under = re.search(r'under\s*\$?(\d+)|below\s*\$?(\d+)|less than\s*\$?(\d+)|cheaper than\s*\$?(\d+)', msg)
    price_above = re.search(r'above\s*\$?(\d+)|over\s*\$?(\d+)|more than\s*\$?(\d+)', msg)

    # LOW STOCK - "low stock", "running out", "less than X units"
    low_stock = any(w in msg for w in ["low stock", "running out", "low on stock", "out of stock"])
    stock_under = re.search(r'stock\s*(under|below|less than)\s*(\d+)', msg)

    # ADD PRODUCT - "add product", "insert", "new product"
    add_product = any(w in msg for w in ["add", "insert", "new product", "create product"])

    if price_under:
        max_price = float(next(x for x in price_under.groups() if x))
        filtered = [p for p in products if float(p.get('price', 999)) <= max_price]
        if filtered:
            lines = [f"- {p.get('name')} | Price: ${p.get('price')} | Stock: {p.get('stock')} units" for p in filtered]
            return f"Products under ${max_price}:\n" + "\n".join(lines)
        return f"No products found under ${max_price}."

    elif price_above:
        min_price = float(next(x for x in price_above.groups() if x))
        filtered = [p for p in products if float(p.get('price', 0)) >= min_price]
        if filtered:
            lines = [f"- {p.get('name')} | Price: ${p.get('price')} | Stock: {p.get('stock')} units" for p in filtered]
            return f"Products above ${min_price}:\n" + "\n".join(lines)
        return f"No products found above ${min_price}."

    elif low_stock:
        filtered = [p for p in products if int(p.get('stock', 999)) < 40]
        if filtered:
            lines = [f"- {p.get('name')} | Stock: {p.get('stock')} units ⚠️" for p in filtered]
            return f"Low stock products (less than 40 units):\n" + "\n".join(lines)
        return "All products have sufficient stock!"

    elif any(w in msg for w in ["product", "item", "inventory", "catalogue"]):
        if products:
            lines = [f"- {p.get('name')} | Price: ${p.get('price')} | Stock: {p.get('stock')} units" for p in products]
            return f"Here are {len(products)} products in our inventory:\n" + "\n".join(lines)
        return "No products found."

    elif any(w in msg for w in ["order", "purchase", "buy", "transaction"]):
        if orders:
            lines = [f"- {o.get('customer')} ordered {o.get('product')} x{o.get('quantity')} | Status: {o.get('status')} | Total: ${o.get('total')}" for o in orders]
            return f"Found {len(orders)} recent orders:\n" + "\n".join(lines)
        return "No orders found."

    elif any(w in msg for w in ["summary", "report", "dashboard", "overview"]):
        total_stock = sum(int(p.get('stock', 0)) for p in products)
        return f"Store Overview:\n- Total Products: {len(products)}\n- Total Stock Units: {total_stock}\n- Recent Orders: {len(orders)}\n- Latest Status: {orders[0].get('status', 'N/A') if orders else 'No orders yet'}"

    elif any(w in msg for w in ["hello", "hi", "help", "what"]):
        return f"Hello! I am your Retail AI Agent powered by Google Cloud Run + MongoDB.\nI can help you with:\n- Product inventory ({len(products)} products)\n- Price filtering (e.g. 'show products under $100')\n- Low stock alerts\n- Order management ({len(orders)} orders)\nJust ask!"

    else:
        return f"Retail Store has {len(products)} products and {len(orders)} orders. Ask me about products, orders, price filters, or store summary!"
