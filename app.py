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
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
import random
import json

app = Flask(__name__)
app.secret_key = "pahadi_kitchen_s3cr3t_2024"

# ── Database ─────────────────────────────────────────────────
# Uses PostgreSQL on Render (DATABASE_URL env var) or SQLite locally
_base_dir    = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(_base_dir, "data", "pahadi.db")
)
# Render gives postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"]        = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ── Constants ─────────────────────────────────────────────────
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
TAX_RATE   = 0.05

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
# Database Models
# ════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = "users"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),  unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class MenuItemModel(db.Model):
    __tablename__ = "menu_items"
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60),  nullable=False)
    price    = db.Column(db.Float,       nullable=False)
    desc     = db.Column(db.String(300), default="")

    @property
    def icon(self):
        return CATEGORY_ICONS.get(self.category, "🍽")


class Order(db.Model):
    __tablename__ = "orders"
    order_id   = db.Column(db.String(30), primary_key=True)
    username   = db.Column(db.String(80))
    phone      = db.Column(db.String(20), default="")
    timestamp  = db.Column(db.String(40))
    subtotal   = db.Column(db.Float)
    tax        = db.Column(db.Float)
    total      = db.Column(db.Float)
    bill_text  = db.Column(db.Text)
    items      = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.String(30), db.ForeignKey("orders.order_id"), nullable=False)
    item_name  = db.Column(db.String(120))
    qty        = db.Column(db.Integer)
    unit_price = db.Column(db.Float)


class OrderStatus(db.Model):
    __tablename__ = "order_statuses"
    order_id        = db.Column(db.String(30), primary_key=True)
    status          = db.Column(db.String(30), default="pending")
    customer        = db.Column(db.String(80))
    phone           = db.Column(db.String(20), default="")
    total           = db.Column(db.String(20))
    created_at      = db.Column(db.String(40))
    accepted_at     = db.Column(db.String(40))
    declined_at     = db.Column(db.String(40))
    ready_at        = db.Column(db.String(40))
    delivering_at   = db.Column(db.String(40))
    delivered_at    = db.Column(db.String(40))
    eta_minutes     = db.Column(db.Integer, default=25)
    driver_name     = db.Column(db.String(80))
    driver_vehicle  = db.Column(db.String(40))
    driver_rating   = db.Column(db.String(10))
    driver_bike     = db.Column(db.String(60))


# ════════════════════════════════════════════════════════════
# DB Init & Menu Seed
# ════════════════════════════════════════════════════════════

def initialize_db():
    os.makedirs("data", exist_ok=True)
    db.create_all()
    # Seed menu only if empty
    if MenuItemModel.query.count() == 0:
        default = [
            MenuItemModel(name="Aloo Ke Gutke",          category="Starters",    price=80,  desc="Spiced baby potatoes tempered with jakhiya seeds & dry red chillies"),
            MenuItemModel(name="Bhatt ke Dubke",          category="Starters",    price=90,  desc="Black soybean fritters in a tangy tomato-coriander dipping sauce"),
            MenuItemModel(name="Singal Fritters",         category="Starters",    price=70,  desc="Crispy wild fern fritters served with green mountain chutney"),
            MenuItemModel(name="Til Chutney Platter",     category="Starters",    price=60,  desc="Roasted sesame chutney served with warm mandua roti strips"),
            MenuItemModel(name="Kafuli",                  category="Main Course", price=150, desc="Slow-cooked spinach & fenugreek greens in a mustard-oil gravy"),
            MenuItemModel(name="Chainsoo",                category="Main Course", price=130, desc="Roasted black gram dal tempered with ghee & asafoetida"),
            MenuItemModel(name="Bhatt ki Churdkani",      category="Main Course", price=140, desc="Creamy black soybean curry in an aromatic ginger-garlic masala"),
            MenuItemModel(name="Gahat ki Dal",            category="Main Course", price=120, desc="Horse gram dal cooked with Pahadi spices — great for the hills"),
            MenuItemModel(name="Thechwani",               category="Main Course", price=110, desc="Slow-cooked radish & potato with jakhiya tempering"),
            MenuItemModel(name="Pahadi Ras (Chicken)",    category="Main Course", price=220, desc="Village-style slow-cooked chicken in an aromatic mountain curry"),
            MenuItemModel(name="Mandua ki Roti",          category="Breads",      price=40,  desc="Finger-millet flatbread — naturally gluten-free & earthy"),
            MenuItemModel(name="Jhangora Pulao",          category="Breads",      price=70,  desc="Barnyard millet pilaf tossed with seasonal mountain vegetables"),
            MenuItemModel(name="Bal Mithai",              category="Desserts",    price=100, desc="Fudgy brown milk sweet rolled in white sugar balls — Almora special"),
            MenuItemModel(name="Singori",                 category="Desserts",    price=80,  desc="Khoya sweet wrapped in a fresh maalu leaf — Kumaoni classic"),
            MenuItemModel(name="Jhangora ki Kheer",       category="Desserts",    price=90,  desc="Creamy millet pudding with cardamom, saffron & dry fruits"),
            MenuItemModel(name="Buransh Sharbat",         category="Drinks",      price=70,  desc="Refreshing rhododendron flower juice from the Himalayan orchards"),
            MenuItemModel(name="Chhachh",                 category="Drinks",      price=40,  desc="Chilled spiced mountain buttermilk with roasted cumin & mint"),
            MenuItemModel(name="Kafal Sharbat",           category="Drinks",      price=80,  desc="Tart & sweet Himalayan bayberry juice — a seasonal favourite"),
        ]
        db.session.add_all(default)
        db.session.commit()


# ════════════════════════════════════════════════════════════
# SMS
# ════════════════════════════════════════════════════════════

def send_sms(to_number, message):
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


def compute_cart(menu_map):
    rows     = []
    subtotal = 0.0
    for item_id, qty in session.get("cart", {}).items():
        item = menu_map.get(int(item_id))
        if item:
            amount    = item.price * qty
            subtotal += amount
            rows.append({"item": item, "qty": qty, "amount": amount})
    tax   = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)
    return rows, subtotal, tax, total


# ════════════════════════════════════════════════════════════
# Context Processor
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
    category  = request.args.get("category", "").strip()
    search    = request.args.get("search",   "").strip().lower()
    max_price = request.args.get("max_price", "").strip()

    q = MenuItemModel.query
    if category:
        q = q.filter_by(category=category)
    if search:
        q = q.filter(
            db.or_(
                MenuItemModel.name.ilike(f"%{search}%"),
                MenuItemModel.desc.ilike(f"%{search}%")
            )
        )
    if max_price:
        try:
            q = q.filter(MenuItemModel.price <= float(max_price))
        except ValueError:
            pass

    items      = q.order_by(MenuItemModel.id).all()
    categories = sorted(set(i.category for i in MenuItemModel.query.all()))
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
    menu_map = {i.id: i for i in MenuItemModel.query.all()}
    rows, subtotal, tax, total = compute_cart(menu_map)
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

    menu_map  = {i.id: i for i in MenuItemModel.query.all()}
    username  = session.get("username", "Guest")
    phone     = request.form.get("phone", "").strip()
    order_id  = "ORD" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))
    timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    rows, subtotal, tax, total = compute_cart(menu_map)

    # Build bill text
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
    bill_text = "\n".join(bill_lines)

    # Save order to DB
    order = Order(
        order_id=order_id, username=username, phone=phone,
        timestamp=timestamp, subtotal=subtotal, tax=tax,
        total=total, bill_text=bill_text
    )
    db.session.add(order)
    for r in rows:
        db.session.add(OrderItem(
            order_id=order_id, item_name=r["item"].name,
            qty=r["qty"], unit_price=r["item"].price
        ))

    # Save status to DB
    status = OrderStatus(
        order_id=order_id, status="pending",
        customer=username, phone=phone,
        total=f"{total:.2f}",
        created_at=datetime.datetime.now().isoformat(),
        eta_minutes=random.randint(22, 35),
    )
    db.session.add(status)
    db.session.commit()

    send_sms(phone,
        f"Pahadi Kitchen: Hi {username}! Your order #{order_id} has been placed "
        f"(Rs.{total:.2f}). We'll confirm shortly. Track: /track/{order_id}"
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
        user = User.query.filter_by(username=username, password=password).first()
        if user:
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
        if not username or not password:
            flash("Username and password are required.", "error")
        elif username.lower() in ("admin", "guest"):
            flash("That username is reserved.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Username already taken. Try another.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            db.session.add(User(username=username, password=password))
            db.session.commit()
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
    orders = Order.query.filter_by(username=session["username"])\
                        .order_by(Order.order_id.desc()).all()
    return render_template("history.html", orders=orders)


@app.route("/history/<order_id>")
def view_order(order_id):
    if not session.get("username"):
        return redirect(url_for("login"))
    order = Order.query.get(order_id)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("history"))
    return render_template("view_order.html", bill_text=order.bill_text, order_id=order_id)


# ════════════════════════════════════════════════════════════
# Routes — Tracking
# ════════════════════════════════════════════════════════════

@app.route("/track/<order_id>")
def track_order(order_id):
    st = OrderStatus.query.get(order_id)
    if not st:
        flash("Order not found.", "error")
        return redirect(url_for("index"))
    return render_template("track.html", order_id=order_id, status=st_to_dict(st))


@app.route("/api/status/<order_id>")
def api_order_status(order_id):
    st = OrderStatus.query.get(order_id)
    if not st:
        return jsonify({"error": "not found"}), 404
    return jsonify(st_to_dict(st))


def st_to_dict(st):
    return {
        "status":         st.status,
        "customer":       st.customer,
        "phone":          st.phone,
        "total":          st.total,
        "created_at":     st.created_at,
        "accepted_at":    st.accepted_at,
        "declined_at":    st.declined_at,
        "ready_at":       st.ready_at,
        "delivering_at":  st.delivering_at,
        "delivered_at":   st.delivered_at,
        "eta_minutes":    st.eta_minutes,
        "driver_name":    st.driver_name,
        "driver_vehicle": st.driver_vehicle,
        "driver_rating":  st.driver_rating,
        "driver_bike":    st.driver_bike,
    }


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
    menu    = MenuItemModel.query.order_by(MenuItemModel.id).all()
    orders  = db.session.query(Order, OrderStatus)\
                .outerjoin(OrderStatus, Order.order_id == OrderStatus.order_id)\
                .order_by(Order.order_id.desc()).all()
    categories = sorted(set(i.category for i in menu))
    order_rows = []
    for o, st in orders:
        order_rows.append({
            "id":       o.order_id,
            "customer": o.username,
            "phone":    o.phone,
            "date":     o.timestamp,
            "total":    f"{o.total:.2f}",
            "status":   st.status if st else "unknown",
        })
    return render_template("admin.html", menu=menu, orders=order_rows,
                           categories=categories, cat_icons=CATEGORY_ICONS)


@app.route("/admin/add_item", methods=["POST"])
def admin_add_item():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    try:
        name     = request.form["name"].strip()
        category = request.form["category"].strip()
        price    = float(request.form["price"])
        desc     = request.form.get("desc", "").strip()
        if not name or not category or price <= 0:
            flash("All fields required; price must be positive.", "error")
        else:
            db.session.add(MenuItemModel(name=name, category=category, price=price, desc=desc))
            db.session.commit()
            flash(f"'{name}' added to menu.", "success")
    except (ValueError, KeyError):
        flash("Invalid input.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/remove_item/<int:item_id>")
def admin_remove_item(item_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    item = MenuItemModel.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f"'{item.name}' removed.", "success")
    else:
        flash("Item not found.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/edit_item", methods=["POST"])
def admin_edit_item():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    try:
        item = MenuItemModel.query.get(int(request.form["item_id"]))
        if not item:
            flash("Item not found.", "error")
        else:
            item.name     = request.form["name"].strip()
            item.category = request.form["category"].strip()
            item.price    = float(request.form["price"])
            item.desc     = request.form.get("desc", "").strip()
            db.session.commit()
            flash(f"'{item.name}' updated.", "success")
    except (ValueError, KeyError):
        flash("Invalid input.", "error")
    return redirect(url_for("admin_panel") + "#menu-tab")


@app.route("/admin/order/accept/<order_id>")
def admin_accept_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = OrderStatus.query.get(order_id)
    if st and st.status == "pending":
        st.status      = "accepted"
        st.accepted_at = datetime.datetime.now().isoformat()
        db.session.commit()
        send_sms(st.phone,
            f"Pahadi Kitchen: Your order #{order_id} is accepted & being prepared! "
            f"Track: /track/{order_id}"
        )
        flash(f"Order {order_id} accepted.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/decline/<order_id>")
def admin_decline_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = OrderStatus.query.get(order_id)
    if st and st.status == "pending":
        st.status      = "declined"
        st.declined_at = datetime.datetime.now().isoformat()
        db.session.commit()
        send_sms(st.phone,
            f"Pahadi Kitchen: Sorry, order #{order_id} could not be accepted. Please try again."
        )
        flash(f"Order {order_id} declined.", "info")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/ready/<order_id>")
def admin_ready_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = OrderStatus.query.get(order_id)
    if st and st.status == "accepted":
        driver = random.choice(FAKE_DRIVERS)
        now    = datetime.datetime.now().isoformat()
        st.status         = "out_for_delivery"
        st.ready_at       = now
        st.delivering_at  = now
        st.driver_name    = driver["name"]
        st.driver_vehicle = driver["vehicle"]
        st.driver_rating  = driver["rating"]
        st.driver_bike    = driver["bike"]
        db.session.commit()
        send_sms(st.phone,
            f"Pahadi Kitchen: Your order #{order_id} is out for delivery! "
            f"{driver['name']} ({driver['bike']}) is on the way. ETA ~{st.eta_minutes} mins."
        )
        flash(f"Driver {driver['name']} assigned for order {order_id}.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/order/delivered/<order_id>")
def admin_delivered_order(order_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    st = OrderStatus.query.get(order_id)
    if st and st.status == "out_for_delivery":
        st.status       = "delivered"
        st.delivered_at = datetime.datetime.now().isoformat()
        db.session.commit()
        send_sms(st.phone,
            f"Pahadi Kitchen: Your order #{order_id} has been delivered! Enjoy your Pahadi meal 🏔"
        )
        flash(f"Order {order_id} marked as delivered.", "success")
    return redirect(url_for("admin_panel") + "#orders-tab")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


# ════════════════════════════════════════════════════════════
# Boot
# ════════════════════════════════════════════════════════════

with app.app_context():
    initialize_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
