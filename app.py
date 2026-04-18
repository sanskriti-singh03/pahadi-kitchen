"""
Pahadi Kitchen — Flask Web App
EasyOrder | Semester 2 Group Project
"""
from dotenv import load_dotenv
load_dotenv()
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
import os
import datetime
import random
import json

app = Flask(__name__)
app.secret_key = "pahadi_kitchen_s3cr3t_2024"

# ── paths ────────────────────────────────────────────────────
DATA_DIR     = "data"
USERS_FILE   = os.path.join(DATA_DIR, "users.txt")
MENU_FILE    = os.path.join(DATA_DIR, "menu.txt")
ORDERS_DIR   = os.path.join(DATA_DIR, "orders")
HISTORY_FILE = os.path.join(DATA_DIR, "order_history.txt")

ADMIN_USER   = "admin"
ADMIN_PASS   = "admin123"
TAX_RATE     = 0.05
STATUS_FILE  = os.path.join(DATA_DIR, "statuses.json")

FAKE_DRIVERS = [
    {"name": "Ramesh Negi",   "vehicle": "HP01-AB-1234", "rating": "4.8", "bike": "Hero Splendor"},
    {"name": "Mohan Rawat",   "vehicle": "UK07-CD-5678", "rating": "4.6", "bike": "Bajaj Pulsar"},
    {"name": "Suresh Bisht",  "vehicle": "HP02-EF-9012", "rating": "4.9", "bike": "Honda Activa"},
    {"name": "Dinesh Thakur", "vehicle": "UK09-GH-3456", "rating": "4.7", "bike": "TVS Jupiter"},
    {"name": "Prakash Kumar", "vehicle": "HP05-IJ-7890", "rating": "4.5", "bike": "Hero Passion"},
]

CATEGORY_ICONS = {
    "Starters":    "🥗",
    "Main Course": "🍛",
    "Breads":      "🫓",
    "Desserts":    "🍮",
    "Drinks":      "🥤",
}


# ════════════════════════════════════════════════════════════
# Model
# ════════════════════════════════════════════════════════════

class MenuItem:
    def __init__(self, item_id, name, category, price, desc=""):
        self.item_id  = item_id
        self.name     = name
        self.category = category
        self.price    = price
        self.desc     = desc
        self.icon     = CATEGORY_ICONS.get(category, "🍽")

    def to_file_string(self):
        return f"{self.item_id}|{self.name}|{self.category}|{self.price:.2f}|{self.desc}"

    @staticmethod
    def from_file_string(line):
        parts = line.strip().split("|")
        if len(parts) >= 4:
            try:
                desc = parts[4] if len(parts) > 4 else ""
                return MenuItem(int(parts[0]), parts[1], parts[2], float(parts[3]), desc)
            except ValueError:
                return None
        return None


# ════════════════════════════════════════════════════════════
# File Helpers
# ════════════════════════════════════════════════════════════

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ORDERS_DIR, exist_ok=True)


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    users = {}
    with open(USERS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                u, p = line.split(":", 1)
                users[u] = p
    return users


def save_user(username, password):
    ensure_dirs()
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")


def load_menu():
    if not os.path.exists(MENU_FILE):
        return {}
    items = {}
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        for line in f:
            item = MenuItem.from_file_string(line)
            if item:
                items[item.item_id] = item
    return items


def save_menu(menu):
    ensure_dirs()
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        for item in menu.values():
            f.write(item.to_file_string() + "\n")


def initialize_menu():
    if os.path.exists(MENU_FILE):
        return
    default = [
        MenuItem(1,  "Aloo Ke Gutke",          "Starters",     80,  "Spiced baby potatoes tempered with jakhiya seeds & dry red chillies"),
        MenuItem(2,  "Bhatt ke Dubke",          "Starters",     90,  "Black soybean fritters in a tangy tomato-coriander dipping sauce"),
        MenuItem(3,  "Singal Fritters",         "Starters",     70,  "Crispy wild fern fritters served with green mountain chutney"),
        MenuItem(4,  "Til Chutney Platter",     "Starters",     60,  "Roasted sesame chutney served with warm mandua roti strips"),
        MenuItem(5,  "Kafuli",                  "Main Course", 150,  "Slow-cooked spinach & fenugreek greens in a mustard-oil gravy"),
        MenuItem(6,  "Chainsoo",                "Main Course", 130,  "Roasted black gram dal tempered with ghee & asafoetida"),
        MenuItem(7,  "Bhatt ki Churdkani",      "Main Course", 140,  "Creamy black soybean curry in an aromatic ginger-garlic masala"),
        MenuItem(8,  "Gahat ki Dal",            "Main Course", 120,  "Horse gram dal cooked with Pahadi spices — great for the hills"),
        MenuItem(9,  "Thechwani",               "Main Course", 110,  "Slow-cooked radish & potato with jakhiya tempering"),
        MenuItem(10, "Pahadi Ras (Chicken)",    "Main Course", 220,  "Village-style slow-cooked chicken in an aromatic mountain curry"),
        MenuItem(11, "Mandua ki Roti",          "Breads",       40,  "Finger-millet flatbread — naturally gluten-free & earthy"),
        MenuItem(12, "Jhangora Pulao",          "Breads",       70,  "Barnyard millet pilaf tossed with seasonal mountain vegetables"),
        MenuItem(13, "Bal Mithai",              "Desserts",    100,  "Fudgy brown milk sweet rolled in white sugar balls — Almora special"),
        MenuItem(14, "Singori",                 "Desserts",     80,  "Khoya sweet wrapped in a fresh maalu leaf — Kumaoni classic"),
        MenuItem(15, "Jhangora ki Kheer",       "Desserts",     90,  "Creamy millet pudding with cardamom, saffron & dry fruits"),
        MenuItem(16, "Buransh Sharbat",         "Drinks",       70,  "Refreshing rhododendron flower juice from the Himalayan orchards"),
        MenuItem(17, "Chhachh",                 "Drinks",       40,  "Chilled spiced mountain buttermilk with roasted cumin & mint"),
        MenuItem(18, "Kafal Sharbat",           "Drinks",       80,  "Tart & sweet Himalayan bayberry juice — a seasonal favourite"),
    ]
    save_menu({i.item_id: i for i in default})


def load_order_history(username):
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [
            l.strip().split(":", 1)[1]
            for l in f
            if l.strip().startswith(username + ":")
        ]


def save_order_to_history(username, order_id):
    ensure_dirs()
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{username}:{order_id}\n")


# ════════════════════════════════════════════════════════════
# Order Status (JSON)
# ════════════════════════════════════════════════════════════

def load_statuses():
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_statuses(statuses):
    ensure_dirs()
    with open(STATUS_FILE, "w") as f:
        json.dump(statuses, f, indent=2)


def get_order_status(order_id):
    return load_statuses().get(order_id)


def update_order_status(order_id, updates):
    statuses = load_statuses()
    if order_id in statuses:
        statuses[order_id].update(updates)
        save_statuses(statuses)
        return True
    return False


# ════════════════════════════════════════════════════════════
# SMS (Twilio — optional)
# ════════════════════════════════════════════════════════════

def send_sms(to_number, message):
    """Send SMS via Twilio. Set TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM env vars to enable."""
    if not to_number:
        return False
    sid   = os.environ.get("TWILIO_SID")
    token = os.environ.get("TWILIO_TOKEN")
    from_ = os.environ.get("TWILIO_FROM")
    if not all([sid, token, from_]):
        print(f"[SMS — Twilio not configured] → {to_number}: {message}")
        return False
    try:
        from twilio.rest import Client
        Client(sid, token).messages.create(to=to_number, from_=from_, body=message)
        print(f"[SMS sent] → {to_number}")
        return True
    except Exception as e:
        print(f"[SMS failed] {e}")
        return False


# ════════════════════════════════════════════════════════════
# Cart Helpers (session-based)
# ════════════════════════════════════════════════════════════

def get_cart():
    return session.get("cart", {})


def cart_item_count():
    return sum(session.get("cart", {}).values())


def compute_cart(menu):
    rows     = []
    subtotal = 0.0
    for item_id, qty in session.get("cart", {}).items():
        item = menu.get(int(item_id))
        if item:
            amount   = item.price * qty
            subtotal += amount
            rows.append({"item": item, "qty": qty, "amount": amount})
    tax   = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)
    return rows, subtotal, tax, total


# ════════════════════════════════════════════════════════════
# Context processor
# ════════════════════════════════════════════════════════════

@app.context_processor
def inject_globals():
    return {
        "cart_count":   cart_item_count(),
        "current_user": session.get("username"),
        "is_admin":     session.get("is_admin", False),
    }


# ════════════════════════════════════════════════════════════
# Routes — Public
# ════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/menu")
def menu_page():
    menu      = load_menu()
    category  = request.args.get("category", "").strip()
    search    = request.args.get("search",   "").strip().lower()
    max_price = request.args.get("max_price", "").strip()

    items = list(menu.values())
    if category:
        items = [i for i in items if i.category == category]
    if search:
        items = [i for i in items if search in i.name.lower() or search in i.desc.lower()]
    if max_price:
        try:
            items = [i for i in items if i.price <= float(max_price)]
        except ValueError:
            pass

    categories = sorted(set(i.category for i in menu.values()))
    return render_template(
        "menu.html",
        items=items, categories=categories,
        category=category, search=search, max_price=max_price,
        cat_icons=CATEGORY_ICONS,
    )


# ════════════════════════════════════════════════════════════
# Routes — Cart
# ════════════════════════════════════════════════════════════

@app.route("/cart/add", methods=["POST"])
def cart_add():
    item_id = str(request.form.get("item_id", ""))
    try:
        qty = max(1, int(request.form.get("qty", 1)))
    except ValueError:
        qty = 1
    cart = session.get("cart", {})
    cart[item_id] = cart.get(item_id, 0) + qty
    session["cart"] = cart
    flash("Added to cart!", "success")
    return redirect(request.referrer or url_for("menu_page"))


@app.route("/cart")
def cart_page():
    menu = load_menu()
    rows, subtotal, tax, total = compute_cart(menu)
    return render_template("cart.html", rows=rows, subtotal=subtotal, tax=tax, total=total)


@app.route("/cart/update", methods=["POST"])
def cart_update():
    item_id = str(request.form.get("item_id", ""))
    try:
        qty = int(request.form.get("qty", 1))
    except ValueError:
        qty = 1
    cart = session.get("cart", {})
    if qty <= 0:
        cart.pop(item_id, None)
    else:
        cart[item_id] = qty
    session["cart"] = cart
    return redirect(url_for("cart_page"))


@app.route("/cart/remove/<item_id>")
def cart_remove(item_id):
    cart = session.get("cart", {})
    cart.pop(str(item_id), None)
    session["cart"] = cart
    return redirect(url_for("cart_page"))


@app.route("/cart/clear")
def cart_clear():
    session["cart"] = {}
    return redirect(url_for("cart_page"))


# ════════════════════════════════════════════════════════════
# Routes — Order
# ════════════════════════════════════════════════════════════

@app.route("/order/place", methods=["POST"])
def place_order():
    cart = get_cart()
    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart_page"))

    menu      = load_menu()
    username  = session.get("username", "Guest")
    phone     = request.form.get("phone", "").strip()
    order_id  = "ORD" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))
    timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    rows, subtotal, tax, total = compute_cart(menu)

    # save bill to file
    ensure_dirs()
    bill_lines = [
        "=" * 52,
        "      Pahadi Kitchen  —  Order Receipt",
        "=" * 52,
        f"  Order ID  : {order_id}",
        f"  Customer  : {username}",
        f"  Date/Time : {timestamp}",
        "-" * 52,
    ]
    for r in rows:
        bill_lines.append(f"  {r['item'].name:<26} x{r['qty']:<4} Rs.{r['amount']:.2f}")
    bill_lines += [
        "-" * 52,
        f"  {'Subtotal':<40} Rs.{subtotal:.2f}",
        f"  {'GST (5%)':<40} Rs.{tax:.2f}",
        "=" * 52,
        f"  {'TOTAL':<40} Rs.{total:.2f}",
        "=" * 52,
    ]
    with open(os.path.join(ORDERS_DIR, f"{order_id}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(bill_lines))

    # save order status
    statuses = load_statuses()
    statuses[order_id] = {
        "status":        "pending",
        "customer":      username,
        "phone":         phone,
        "total":         f"{total:.2f}",
        "created_at":    datetime.datetime.now().isoformat(),
        "accepted_at":   None,
        "declined_at":   None,
        "ready_at":      None,
        "delivering_at": None,
        "delivered_at":  None,
        "eta_minutes":   random.randint(22, 35),
        "driver_name":   None,
        "driver_vehicle":None,
        "driver_rating": None,
        "driver_bike":   None,
    }
    save_statuses(statuses)

    if username != "Guest":
        save_order_to_history(username, order_id)

    # SMS — order placed
    send_sms(phone,
        f"Pahadi Kitchen: Hi {username}! Your order #{order_id} has been placed "
        f"(Rs.{total:.2f}). We'll confirm it shortly. Track at /track/{order_id}"
    )

    session["cart"] = {}
    return render_template(
        "bill.html",
        order_id=order_id, username=username, timestamp=timestamp,
        rows=rows, subtotal=subtotal, tax=tax, total=total,
    )


# ════════════════════════════════════════════════════════════
# Routes — Auth
# ════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        users = load_users()
        if username in users and users[username] == password:
            session["username"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("menu_page"))
        flash("Incorrect username or password.", "error")
    return render_template("auth.html", mode="login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm",  "").strip()
        users    = load_users()
        if not username or not password:
            flash("Username and password are required.", "error")
        elif username.lower() in ("admin", "guest"):
            flash("That username is reserved.", "error")
        elif username in users:
            flash("Username already taken. Try another.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            save_user(username, password)
            session["username"] = username
            flash(f"Welcome to Pahadi Kitchen, {username}! 🏔", "success")
            return redirect(url_for("menu_page"))
    return render_template("auth.html", mode="signup")


@app.route("/guest")
def guest_login():
    session["username"] = "Guest"
    flash("Browsing as Guest. Order history will not be saved.", "info")
    return redirect(url_for("menu_page"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════
# Routes — Order History
# ════════════════════════════════════════════════════════════

@app.route("/history")
def history():
    if not session.get("username") or session["username"] == "Guest":
        flash("Please log in to view your order history.", "info")
        return redirect(url_for("login"))
    username  = session["username"]
    order_ids = load_order_history(username)
    orders    = []
    for oid in reversed(order_ids):
        filepath = os.path.join(ORDERS_DIR, f"{oid}.txt")
        date_str = total_str = ""
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if "Date/Time" in line:
                        date_str = line.strip().split(":", 1)[1].strip()
                    if "TOTAL" in line:
                        total_str = line.strip().split("Rs.")[-1].strip()
        orders.append({"id": oid, "date": date_str, "total": total_str})
    return render_template("history.html", orders=orders)


@app.route("/history/<order_id>")
def view_order(order_id):
    if not session.get("username"):
        return redirect(url_for("login"))
    filepath = os.path.join(ORDERS_DIR, f"{order_id}.txt")
    if not os.path.exists(filepath):
        flash("Order not found.", "error")
        return redirect(url_for("history"))
    with open(filepath, "r", encoding="utf-8") as f:
        bill_text = f.read()
    return render_template("view_order.html", bill_text=bill_text, order_id=order_id)


# ════════════════════════════════════════════════════════════
# Routes — Admin
# ════════════════════════════════════════════════════════════

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASS:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin")
def admin_panel():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    menu      = load_menu()
    statuses  = load_statuses()
    orders    = []
    if os.path.exists(ORDERS_DIR):
        for fname in sorted(os.listdir(ORDERS_DIR), reverse=True):
            if not fname.endswith(".txt"):
                continue
            oid  = fname[:-4]
            info = {"id": oid, "customer": "", "date": "", "total": "",
                    "status": statuses.get(oid, {}).get("status", "unknown"),
                    "phone":  statuses.get(oid, {}).get("phone", "")}
            with open(os.path.join(ORDERS_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    if "Customer"  in line: info["customer"] = line.strip().split(":", 1)[1].strip()
                    if "Date/Time" in line: info["date"]     = line.strip().split(":", 1)[1].strip()
                    if "TOTAL"     in line: info["total"]    = line.strip().split("Rs.")[-1].strip()
            orders.append(info)
    categories = sorted({i.category for i in menu.values()})
    return render_template("admin.html", menu=menu, orders=orders, categories=categories,
                           cat_icons=CATEGORY_ICONS)


@app.route("/admin/add_item", methods=["POST"])
def admin_add_item():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    menu = load_menu()
    try:
        name     = request.form["name"].strip()
        category = request.form["category"].strip()
        price    = float(request.form["price"])
        desc     = request.form.get("desc", "").strip()
        if not name or not category or price <= 0:
            flash("All fields required; price must be positive.", "error")
        else:
            new_id = max(menu.keys(), default=0) + 1
            menu[new_id] = MenuItem(new_id, name, category, price, desc)
            save_menu(menu)
            flash(f"'{name}' added to menu.", "success")
    except (ValueError, KeyError):
        flash("Invalid input.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/remove_item/<int:item_id>")
def admin_remove_item(item_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    menu = load_menu()
    if item_id in menu:
        name = menu.pop(item_id).name
        save_menu(menu)
        flash(f"'{name}' removed from menu.", "success")
    else:
        flash("Item not found.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/update_price", methods=["POST"])
def admin_update_price():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    menu = load_menu()
    try:
        item_id   = int(request.form["item_id"])
        new_price = float(request.form["price"])
        if item_id in menu and new_price > 0:
            menu[item_id].price = new_price
            save_menu(menu)
            flash(f"Price updated for '{menu[item_id].name}'.", "success")
        else:
            flash("Invalid item or price.", "error")
    except (ValueError, KeyError):
        flash("Invalid input.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/edit_item", methods=["POST"])
def admin_edit_item():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    menu = load_menu()
    try:
        item_id  = int(request.form["item_id"])
        name     = request.form["name"].strip()
        category = request.form["category"].strip()
        price    = float(request.form["price"])
        desc     = request.form.get("desc", "").strip()
        if item_id not in menu:
            flash("Item not found.", "error")
        elif not name or not category or price <= 0:
            flash("Name, category and a positive price are required.", "error")
        else:
            menu[item_id] = MenuItem(item_id, name, category, price, desc)
            save_menu(menu)
            flash(f"'{name}' updated successfully.", "success")
    except (ValueError, KeyError):
        flash("Invalid input.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════
# Routes — Order Tracking
# ════════════════════════════════════════════════════════════

@app.route("/track/<order_id>")
def track_order(order_id):
    st = get_order_status(order_id)
    if not st:
        flash("Order not found.", "error")
        return redirect(url_for("index"))
    return render_template("track.html", order_id=order_id, status=st)


@app.route("/api/status/<order_id>")
def api_order_status(order_id):
    st = get_order_status(order_id)
    if not st:
        return jsonify({"error": "not found"}), 404
    return jsonify(st)


# ════════════════════════════════════════════════════════════
# Routes — Admin Order Management
# ════════════════════════════════════════════════════════════

@app.route("/admin/order/accept/<order_id>")
def admin_accept_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = get_order_status(order_id)
    if st and st["status"] == "pending":
        update_order_status(order_id, {
            "status":      "accepted",
            "accepted_at": datetime.datetime.now().isoformat(),
        })
        send_sms(st.get("phone"),
            f"Pahadi Kitchen: Great news! Your order #{order_id} has been accepted "
            f"and is now being prepared. Track live: /track/{order_id}"
        )
        flash(f"Order {order_id} accepted.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/decline/<order_id>")
def admin_decline_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = get_order_status(order_id)
    if st and st["status"] == "pending":
        update_order_status(order_id, {
            "status":      "declined",
            "declined_at": datetime.datetime.now().isoformat(),
        })
        send_sms(st.get("phone"),
            f"Pahadi Kitchen: Sorry, order #{order_id} could not be accepted at this time. "
            f"Please try ordering again."
        )
        flash(f"Order {order_id} declined.", "info")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/ready/<order_id>")
def admin_ready_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = get_order_status(order_id)
    if st and st["status"] == "accepted":
        driver = random.choice(FAKE_DRIVERS)
        now    = datetime.datetime.now().isoformat()
        update_order_status(order_id, {
            "status":         "out_for_delivery",
            "ready_at":       now,
            "delivering_at":  now,
            "driver_name":    driver["name"],
            "driver_vehicle": driver["vehicle"],
            "driver_rating":  driver["rating"],
            "driver_bike":    driver["bike"],
        })
        send_sms(st.get("phone"),
            f"Pahadi Kitchen: Your order #{order_id} is out for delivery! "
            f"{driver['name']} ({driver['bike']}, {driver['vehicle']}) is on the way. "
            f"ETA ~{st.get('eta_minutes', 25)} mins. Track: /track/{order_id}"
        )
        flash(f"Driver {driver['name']} assigned for order {order_id}.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/delivered/<order_id>")
def admin_delivered_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = get_order_status(order_id)
    if st and st["status"] == "out_for_delivery":
        update_order_status(order_id, {
            "status":       "delivered",
            "delivered_at": datetime.datetime.now().isoformat(),
        })
        send_sms(st.get("phone"),
            f"Pahadi Kitchen: Your order #{order_id} has been delivered! "
            f"Enjoy your Pahadi meal. Thank you for ordering with us!"
        )
        flash(f"Order {order_id} marked as delivered.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


# ════════════════════════════════════════════════════════════
# Boot
# ════════════════════════════════════════════════════════════

# Run on startup regardless of how the app is launched (gunicorn or direct)
ensure_dirs()
initialize_menu()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
