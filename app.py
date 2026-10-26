from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Mock database: an array of inventory items
inventory = [
    {
        "id": 1,
        "barcode": "1234567890123",
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "ingredients": "Filtered water, almonds, cane sugar",
        "price": 350.00,
        "stock": 20
    },
    {
        "id": 2,
        "barcode": "2345678901234",
        "name": "Whole Wheat Bread",
        "brand": "Example Bakery",
        "ingredients": "Whole wheat flour, water, yeast, salt",
        "price": 180.00,
        "stock": 15
    }
]

NEXT_ID = 3

# OpenFoodFacts API endpoints
BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def find_item(item_id):
    """Find an inventory item using its ID."""
    return next(
        (item for item in inventory if item["id"] == item_id),
        None
    )


def validate_item(data, partial=False):
    """Validate data received from a client."""
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    required = {"name", "price", "stock"}

    if not partial:
        missing = required - data.keys()
        if missing:
            return "Missing fields: " + ", ".join(sorted(missing))

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "Name must be a non-empty string."

    if "price" in data:
        price = data["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            return "Price must be a non-negative number."

    if "stock" in data:
        stock = data["stock"]
        if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
            return "Stock must be a non-negative integer."

    for field in ("barcode", "brand", "ingredients"):
        if field in data and not isinstance(data[field], str):
            return f"{field} must be a string."

    return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Inventory Management API",
        "endpoints": [
            "GET /inventory",
            "GET /inventory/<id>",
            "POST /inventory",
            "PATCH /inventory/<id>",
            "DELETE /inventory/<id>",
            "GET /products/barcode/<barcode>",
            "GET /products/search?name=almond milk",
            "POST /products/import"
        ]
    }), 200


# 1. GET: Retrieve all inventory items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


# 2. GET: Retrieve one item by ID
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    return jsonify(item), 200


# 3. POST: Add an inventory item
@app.route("/inventory", methods=["POST"])
def create_item():
    global NEXT_ID

    data = request.get_json(silent=True)
    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    item = {
        "id": NEXT_ID,
        "name": data["name"].strip(),
        "price": float(data["price"]),
        "stock": data["stock"],
        "barcode": data.get("barcode", ""),
        "brand": data.get("brand", ""),
        "ingredients": data.get("ingredients", "")
    }

    inventory.append(item)
    NEXT_ID += 1

    return jsonify(item), 201


# 4. PATCH: Update selected item fields
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    data = request.get_json(silent=True)
    error = validate_item(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    allowed_fields = {
        "name", "price", "stock",
        "barcode", "brand", "ingredients"
    }

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        if field == "name":
            item[field] = value.strip()
        elif field == "price":
            item[field] = float(value)
        else:
            item[field] = value

    return jsonify(item), 200


# 5. DELETE: Remove an item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    inventory.remove(item)

    return jsonify({
        "message": f"Inventory item {item_id} deleted successfully"
    }), 200


def fetch_product(barcode=None, name=None):
    """Fetch product details from OpenFoodFacts."""

    headers = {
        "User-Agent": "MoringaInventoryLab/1.0"
    }

    if barcode:
        response = requests.get(
            BARCODE_URL.format(barcode),
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        if result.get("status") != 1 or not result.get("product"):
            return None

        product = result["product"]

    elif name:
        response = requests.get(
            SEARCH_URL,
            params={
                "search_terms": name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 5
            },
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        result = response.json()
        products = result.get("products", [])

        if not products:
            return None

        product = products[0]
        barcode = product.get("code", "")

    else:
        return None

    return {
        "barcode": barcode or product.get("code", ""),
        "name": product.get("product_name", ""),
        "brand": product.get("brands", ""),
        "ingredients": product.get("ingredients_text", ""),
        "image_url": product.get("image_front_url", "")
    }


# 6. GET: Look up a product using its barcode
@app.route("/products/barcode/<barcode>", methods=["GET"])
def lookup_barcode(barcode):
    try:
        product = fetch_product(barcode=barcode)
    except (requests.RequestException, ValueError):
        return jsonify({"error": "External API request failed"}), 502

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product), 200


# 7. GET: Search for a product by name
@app.route("/products/search", methods=["GET"])
def search_product():
    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({
            "error": "Provide a product name using ?name=..."
        }), 400

    try:
        product = fetch_product(name=name)
    except (requests.RequestException, ValueError):
        return jsonify({"error": "External API request failed"}), 502

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product), 200


# 8. POST: Import an external product into inventory
@app.route("/products/import", methods=["POST"])
def import_product():
    global NEXT_ID

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Provide a JSON object"}), 400

    barcode = str(data.get("barcode", "")).strip()
    name = str(data.get("name", "")).strip()

    if not barcode and not name:
        return jsonify({
            "error": "Provide either a barcode or a product name"
        }), 400

    try:
        if barcode:
            product = fetch_product(barcode=barcode)
        else:
            product = fetch_product(name=name)
    except (requests.RequestException, ValueError):
        return jsonify({"error": "External API request failed"}), 502

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    item = {
        "id": NEXT_ID,
        "barcode": product.get("barcode", ""),
        "name": product.get("name") or name or f"Product {barcode}",
        "brand": product.get("brand", ""),
        "ingredients": product.get("ingredients", ""),
        "price": 0.0,
        "stock": 0
    }

    inventory.append(item)
    NEXT_ID += 1

    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True, port=5000)
