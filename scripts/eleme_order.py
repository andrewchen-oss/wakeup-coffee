"""
eleme_order.py
--------------
Places a food order on Ele.me using captured session credentials.

Setup:
  1. Install a packet capture tool (Stream / Charles on iOS)
  2. Open the Ele.me app and browse to your favorite item
  3. Find requests to amdc.m.ele.me and extract:
     - sid (session ID)
     - device_id
  4. Also find your shop_id, item_id, and address_id from the order flow
  5. Fill these into config/config.json

Note: Ele.me requests use a dynamic 'sign' parameter tied to time.
      This script uses the restapi.ele.me endpoints which accept
      session-based auth without dynamic signing.
"""

import json
import time
import urllib.request
import urllib.parse

ELEME_API = "https://restapi.ele.me/v4"

HEADERS_TEMPLATE = {
    "User-Agent": "eleme/53072515 CFNetwork/3860.400.51 Darwin/25.3.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def build_headers(config):
    headers = HEADERS_TEMPLATE.copy()
    headers["Cookie"] = f"sid={config['eleme']['sid']}"
    return headers


def get_cart(config):
    """Get or create a cart for the given shop."""
    url = f"{ELEME_API}/carts"
    payload = json.dumps({
        "restaurant_id": config["eleme"]["shop_id"],
        "address_id": config["eleme"]["address_id"],
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    for k, v in build_headers(config).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def add_to_cart(config, cart_id):
    """Add the configured item to the cart."""
    url = f"{ELEME_API}/carts/{cart_id}/items"
    payload = json.dumps({
        "item_id": config["eleme"]["item_id"],
        "spec_id": config["eleme"]["item_spec_id"],
        "quantity": 1,
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    for k, v in build_headers(config).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def apply_coupon(config, cart_id):
    """Apply coupon if configured."""
    coupon_id = config["eleme"].get("coupon_id", "")
    if not coupon_id:
        return None
    url = f"{ELEME_API}/carts/{cart_id}/coupon"
    payload = json.dumps({"coupon_id": coupon_id}).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    for k, v in build_headers(config).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def place_order(config, cart_id):
    """Submit the order."""
    url = f"{ELEME_API}/orders"
    payload = json.dumps({
        "cart_id": cart_id,
        "address_id": config["eleme"]["address_id"],
        "description": "请放门口，谢谢",
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    for k, v in build_headers(config).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def order_coffee(config, demo=False):
    """
    Full order flow: cart → add item → coupon → place order.
    Returns order info dict.
    """
    item_name = config["order"]["item_name"]

    if demo:
        print(f"[eleme] 🎭 DEMO MODE — simulating order for: {item_name}")
        time.sleep(1)
        return {
            "order_id": "DEMO-20260301-001",
            "item_name": item_name,
            "total_price": 9.9,
            "original_price": 22.0,
            "coupon_discount": 12.1,
            "estimated_delivery_minutes": 22,
            "status": "demo_success",
        }

    print(f"[eleme] Creating cart for shop {config['eleme']['shop_id']}...")
    cart = get_cart(config)
    cart_id = cart["id"]

    print(f"[eleme] Adding {item_name} to cart...")
    add_to_cart(config, cart_id)

    coupon_result = apply_coupon(config, cart_id)
    if coupon_result:
        print(f"[eleme] Coupon applied ✓")

    print(f"[eleme] Placing order...")
    order = place_order(config, cart_id)

    return {
        "order_id": order.get("id", "unknown"),
        "item_name": item_name,
        "total_price": order.get("total_price", 0),
        "estimated_delivery_minutes": order.get("delivery_time", 30),
        "status": "success",
    }


if __name__ == "__main__":
    import sys
    demo_mode = "--demo" in sys.argv
    with open("config/config.json") as f:
        config = json.load(f)
    result = order_coffee(config, demo=demo_mode)
    print(f"[eleme] Order result: {result}")
