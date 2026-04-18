"""
EasyOrder — A Python-Based Food Ordering Application
Semester 2 Group Project | Kanika Sharma & Sanskriti Singh
"""

import os
import datetime
import random

# ── File paths ──────────────────────────────────────────────
USERS_FILE   = "users.txt"
MENU_FILE    = "menu.txt"
ORDERS_DIR   = "orders"
HISTORY_FILE = "order_history.txt"

ADMIN_CREDENTIALS = ("admin", "admin123")
TAX_RATE = 0.05


# ════════════════════════════════════════════════════════════
# Model Classes
# ════════════════════════════════════════════════════════════

class MenuItem:
    def __init__(self, item_id, name, category, price):
        self.item_id  = item_id
        self.name     = name
        self.category = category
        self.price    = price

    def to_file_string(self):
        return f"{self.item_id}|{self.name}|{self.category}|{self.price:.2f}"

    @staticmethod
    def from_file_string(line):
        parts = line.strip().split("|")
        if len(parts) == 4:
            try:
                return MenuItem(int(parts[0]), parts[1], parts[2], float(parts[3]))
            except ValueError:
                return None
        return None

    def __str__(self):
        return f"{self.item_id:<4} {self.name:<25} {self.category:<15} Rs.{self.price:.2f}"


class Cart:
    def __init__(self):
        self.items = {}  # item_id -> (MenuItem, quantity)

    def add_item(self, item, quantity):
        if item.item_id in self.items:
            self.items[item.item_id] = (item, self.items[item.item_id][1] + quantity)
        else:
            self.items[item.item_id] = (item, quantity)

    def remove_item(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def update_quantity(self, item_id, quantity):
        if item_id in self.items:
            if quantity <= 0:
                del self.items[item_id]
            else:
                self.items[item_id] = (self.items[item_id][0], quantity)
            return True
        return False

    def clear(self):
        self.items = {}

    def is_empty(self):
        return len(self.items) == 0

    def get_subtotal(self):
        return sum(item.price * qty for item, qty in self.items.values())

    def display(self):
        if self.is_empty():
            print("  Your cart is empty.")
            return
        print(f"\n  {'ID':<4} {'Item':<25} {'Qty':<6} {'Unit Price':<14} {'Total'}")
        print("  " + "-" * 62)
        for item, qty in self.items.values():
            print(f"  {item.item_id:<4} {item.name:<25} {qty:<6} Rs.{item.price:<11.2f} Rs.{item.price * qty:.2f}")
        print("  " + "-" * 62)
        print(f"  {'Subtotal':<50} Rs.{self.get_subtotal():.2f}")


class Order:
    def __init__(self, username, cart_items, subtotal):
        self.order_id   = self._generate_id()
        self.username   = username
        self.cart_items = cart_items  # list of (name, qty, price)
        self.subtotal   = subtotal
        self.tax        = round(subtotal * TAX_RATE, 2)
        self.total      = round(subtotal + self.tax, 2)
        self.timestamp  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _generate_id(self):
        return "ORD" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))

    def generate_bill(self):
        lines = [
            "=" * 52,
            "          EasyOrder  -  Bill Receipt",
            "=" * 52,
            f"  Order ID  : {self.order_id}",
            f"  Customer  : {self.username}",
            f"  Date/Time : {self.timestamp}",
            "-" * 52,
            f"  {'Item':<25} {'Qty':<6} {'Amount'}",
            "-" * 52,
        ]
        for name, qty, price in self.cart_items:
            lines.append(f"  {name:<25} {qty:<6} Rs.{price * qty:.2f}")
        lines += [
            "-" * 52,
            f"  {'Subtotal':<40} Rs.{self.subtotal:.2f}",
            f"  {'GST (5%)':<40} Rs.{self.tax:.2f}",
            "=" * 52,
            f"  {'TOTAL':<40} Rs.{self.total:.2f}",
            "=" * 52,
        ]
        return "\n".join(lines)

    def save_to_file(self):
        os.makedirs(ORDERS_DIR, exist_ok=True)
        filepath = os.path.join(ORDERS_DIR, f"{self.order_id}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate_bill())
        return filepath


# ════════════════════════════════════════════════════════════
# File Handling
# ════════════════════════════════════════════════════════════

def load_users():
    users = {}
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                username, password = line.split(":", 1)
                users[username] = password
    return users


def save_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")


def load_menu():
    items = {}
    if not os.path.exists(MENU_FILE):
        return items
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        for line in f:
            item = MenuItem.from_file_string(line)
            if item:
                items[item.item_id] = item
    return items


def save_menu(menu):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        for item in menu.values():
            f.write(item.to_file_string() + "\n")


def initialize_menu():
    """Seed menu.txt with default items on first run."""
    if os.path.exists(MENU_FILE):
        return
    default_items = [
        MenuItem(1,  "Veg Spring Rolls",    "Starters",    60.00),
        MenuItem(2,  "Chicken Wings",        "Starters",   120.00),
        MenuItem(3,  "Paneer Tikka",         "Starters",   150.00),
        MenuItem(4,  "Garlic Bread",         "Starters",    80.00),
        MenuItem(5,  "Veg Fried Rice",       "Main Course", 130.00),
        MenuItem(6,  "Chicken Biryani",      "Main Course", 200.00),
        MenuItem(7,  "Paneer Butter Masala", "Main Course", 180.00),
        MenuItem(8,  "Dal Tadka",            "Main Course", 110.00),
        MenuItem(9,  "Butter Naan",          "Main Course",  40.00),
        MenuItem(10, "Gulab Jamun",          "Desserts",     70.00),
        MenuItem(11, "Ice Cream (2 scoops)", "Desserts",     90.00),
        MenuItem(12, "Ras Malai",            "Desserts",    100.00),
        MenuItem(13, "Cold Coffee",          "Drinks",       80.00),
        MenuItem(14, "Fresh Lime Soda",      "Drinks",       50.00),
        MenuItem(15, "Mango Lassi",          "Drinks",       70.00),
        MenuItem(16, "Masala Chai",          "Drinks",       30.00),
    ]
    save_menu({item.item_id: item for item in default_items})


def load_order_history(username):
    history = []
    if not os.path.exists(HISTORY_FILE):
        return history
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(username + ":"):
                history.append(line.split(":", 1)[1])
    return history


def save_order_to_history(username, order_id):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{username}:{order_id}\n")


# ════════════════════════════════════════════════════════════
# Display Helpers
# ════════════════════════════════════════════════════════════

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    print("\n" + "=" * 55)
    print(f"  EasyOrder  |  {title}")
    print("=" * 55)


def display_menu(menu, filter_category=None, max_price=None):
    categories = {}
    for item in menu.values():
        if filter_category and item.category.lower() != filter_category.lower():
            continue
        if max_price is not None and item.price > max_price:
            continue
        categories.setdefault(item.category, []).append(item)

    if not categories:
        print("  No items match your filter.")
        return

    for category, items in categories.items():
        print(f"\n  -- {category} --")
        print(f"  {'ID':<4} {'Name':<25} {'Price'}")
        print("  " + "-" * 40)
        for item in items:
            print(f"  {item.item_id:<4} {item.name:<25} Rs.{item.price:.2f}")


# ════════════════════════════════════════════════════════════
# Authentication
# ════════════════════════════════════════════════════════════

def sign_up():
    users = load_users()
    print("\n  -- Sign Up --")
    while True:
        username = input("  Username: ").strip()
        if not username:
            print("  Username cannot be empty.")
            continue
        if username.lower() in ("admin", "guest"):
            print("  That username is reserved. Choose another.")
            continue
        if username in users:
            print("  Username already taken. Try another.")
            continue
        break
    while True:
        password = input("  Password: ").strip()
        if not password:
            print("  Password cannot be empty.")
            continue
        confirm = input("  Confirm password: ").strip()
        if password != confirm:
            print("  Passwords do not match. Try again.")
            continue
        break
    save_user(username, password)
    print(f"\n  Account created! Welcome, {username}!")
    return username


def login():
    users = load_users()
    print("\n  -- Login --")
    for attempt in range(3):
        username = input("  Username: ").strip()
        password = input("  Password: ").strip()
        if username in users and users[username] == password:
            print(f"\n  Welcome back, {username}!")
            return username
        remaining = 2 - attempt
        if remaining > 0:
            print(f"  Incorrect credentials. {remaining} attempt(s) left.")
        else:
            print("  Too many failed attempts.")
    return None


# ════════════════════════════════════════════════════════════
# Customer Menu
# ════════════════════════════════════════════════════════════

def customer_menu(username):
    menu = load_menu()
    cart = Cart()
    is_guest = (username == "Guest")

    while True:
        print_header(f"Customer  |  {username}")
        print("  1.  View Full Menu")
        print("  2.  Search Menu by Keyword")
        print("  3.  Filter by Category")
        print("  4.  Filter by Max Price")
        print("  5.  Add Item to Cart")
        print("  6.  View Cart")
        print("  7.  Remove Item from Cart")
        print("  8.  Update Item Quantity")
        print("  9.  Clear Cart")
        print("  10. Place Order")
        if not is_guest:
            print("  11. View Order History")
        print("  0.  Logout")
        print()

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            print_header("Menu")
            display_menu(menu)

        elif choice == "2":
            keyword = input("\n  Search keyword: ").strip().lower()
            if not keyword:
                print("  Enter a keyword.")
            else:
                results = {k: v for k, v in menu.items() if keyword in v.name.lower()}
                if results:
                    print_header(f'Search: "{keyword}"')
                    display_menu(results)
                else:
                    print(f'  No items found for "{keyword}".')

        elif choice == "3":
            print("\n  Categories: Starters, Main Course, Desserts, Drinks")
            cat = input("  Enter category: ").strip()
            print_header(f"Category: {cat}")
            display_menu(menu, filter_category=cat)

        elif choice == "4":
            try:
                max_price = float(input("\n  Max price (Rs.): ").strip())
                print_header(f"Items under Rs.{max_price:.0f}")
                display_menu(menu, max_price=max_price)
            except ValueError:
                print("  Invalid price. Enter a number.")

        elif choice == "5":
            display_menu(menu)
            try:
                item_id = int(input("\n  Enter item ID to add: ").strip())
                if item_id not in menu:
                    print("  Item not found.")
                else:
                    qty = int(input("  Quantity: ").strip())
                    if qty <= 0:
                        print("  Quantity must be at least 1.")
                    else:
                        cart.add_item(menu[item_id], qty)
                        print(f"  Added {qty}x {menu[item_id].name} to cart.")
            except ValueError:
                print("  Invalid input. Enter numbers only.")

        elif choice == "6":
            print_header("Your Cart")
            cart.display()

        elif choice == "7":
            print_header("Your Cart")
            cart.display()
            if cart.is_empty():
                pass
            else:
                try:
                    item_id = int(input("\n  Enter item ID to remove: ").strip())
                    if cart.remove_item(item_id):
                        print("  Item removed from cart.")
                    else:
                        print("  That item is not in your cart.")
                except ValueError:
                    print("  Invalid input.")

        elif choice == "8":
            print_header("Your Cart")
            cart.display()
            if not cart.is_empty():
                try:
                    item_id = int(input("\n  Enter item ID to update: ").strip())
                    qty = int(input("  New quantity (0 to remove): ").strip())
                    if cart.update_quantity(item_id, qty):
                        print("  Cart updated.")
                    else:
                        print("  That item is not in your cart.")
                except ValueError:
                    print("  Invalid input.")

        elif choice == "9":
            if cart.is_empty():
                print("\n  Cart is already empty.")
            else:
                confirm = input("\n  Clear entire cart? (y/n): ").strip().lower()
                if confirm == "y":
                    cart.clear()
                    print("  Cart cleared.")

        elif choice == "10":
            if cart.is_empty():
                print("\n  Your cart is empty. Add items before ordering.")
            else:
                print_header("Order Confirmation")
                cart.display()
                confirm = input("\n  Confirm and place order? (y/n): ").strip().lower()
                if confirm == "y":
                    snapshot = [(item.name, qty, item.price) for item, qty in cart.items.values()]
                    order    = Order(username, snapshot, cart.get_subtotal())
                    filepath = order.save_to_file()
                    if not is_guest:
                        save_order_to_history(username, order.order_id)
                    cart.clear()
                    print("\n" + order.generate_bill())
                    print(f"\n  Bill saved to: {filepath}")
                else:
                    print("  Order cancelled.")

        elif choice == "11" and not is_guest:
            history = load_order_history(username)
            if not history:
                print("\n  No past orders found.")
            else:
                print_header("Order History")
                valid = []
                for order_id in history:
                    filepath = os.path.join(ORDERS_DIR, f"{order_id}.txt")
                    if os.path.exists(filepath):
                        valid.append(order_id)
                        with open(filepath, "r", encoding="utf-8") as f:
                            for line in f:
                                if "Date/Time" in line or "TOTAL" in line:
                                    print(f"  [{len(valid)}] {order_id}  |  {line.strip()}")
                                    if "TOTAL" in line:
                                        break
                    else:
                        print(f"  {order_id}  (bill file missing)")

                if valid:
                    sub = input("\n  Enter number to view full bill (or 0 to go back): ").strip()
                    try:
                        idx = int(sub)
                        if 1 <= idx <= len(valid):
                            filepath = os.path.join(ORDERS_DIR, f"{valid[idx-1]}.txt")
                            with open(filepath, "r", encoding="utf-8") as f:
                                print("\n" + f.read())
                    except ValueError:
                        pass

        elif choice == "0":
            print(f"\n  Goodbye, {username}!")
            break

        else:
            print("  Invalid choice. Please try again.")

        input("\n  Press Enter to continue...")
        clear_screen()


# ════════════════════════════════════════════════════════════
# Admin Menu
# ════════════════════════════════════════════════════════════

def admin_menu():
    while True:
        menu = load_menu()
        print_header("Admin Panel")
        print("  1. View All Menu Items")
        print("  2. Add Menu Item")
        print("  3. Remove Menu Item")
        print("  4. Update Item Price")
        print("  5. View All Orders")
        print("  0. Logout")
        print()

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            print_header("All Menu Items")
            print(f"  {'ID':<4} {'Name':<25} {'Category':<15} {'Price'}")
            print("  " + "-" * 55)
            for item in menu.values():
                print(f"  {item}")

        elif choice == "2":
            print("\n  -- Add New Item --")
            try:
                name = input("  Item name: ").strip()
                if not name:
                    print("  Name cannot be empty.")
                    input("\n  Press Enter to continue...")
                    clear_screen()
                    continue
                print("  Categories: Starters, Main Course, Desserts, Drinks")
                category = input("  Category: ").strip()
                if not category:
                    print("  Category cannot be empty.")
                    input("\n  Press Enter to continue...")
                    clear_screen()
                    continue
                price = float(input("  Price (Rs.): ").strip())
                if price <= 0:
                    print("  Price must be a positive number.")
                    input("\n  Press Enter to continue...")
                    clear_screen()
                    continue
                new_id   = max(menu.keys(), default=0) + 1
                new_item = MenuItem(new_id, name, category, price)
                menu[new_id] = new_item
                save_menu(menu)
                print(f"  Item added: {new_item}")
            except ValueError:
                print("  Invalid input. Price must be a number.")

        elif choice == "3":
            print_header("All Menu Items")
            for item in menu.values():
                print(f"  {item}")
            try:
                item_id = int(input("\n  Enter item ID to remove: ").strip())
                if item_id in menu:
                    removed = menu.pop(item_id)
                    save_menu(menu)
                    print(f"  Removed: {removed.name}")
                else:
                    print("  Item not found.")
            except ValueError:
                print("  Invalid input.")

        elif choice == "4":
            print_header("All Menu Items")
            for item in menu.values():
                print(f"  {item}")
            try:
                item_id = int(input("\n  Enter item ID: ").strip())
                if item_id not in menu:
                    print("  Item not found.")
                else:
                    new_price = float(input(f"  New price for '{menu[item_id].name}' (Rs.): ").strip())
                    if new_price <= 0:
                        print("  Price must be positive.")
                    else:
                        menu[item_id].price = new_price
                        save_menu(menu)
                        print(f"  Updated price to Rs.{new_price:.2f}")
            except ValueError:
                print("  Invalid input.")

        elif choice == "5":
            print_header("All Orders")
            if not os.path.exists(ORDERS_DIR) or not any(
                f.endswith(".txt") for f in os.listdir(ORDERS_DIR)
            ):
                print("  No orders placed yet.")
            else:
                count = 0
                for filename in sorted(os.listdir(ORDERS_DIR)):
                    if not filename.endswith(".txt"):
                        continue
                    count += 1
                    filepath = os.path.join(ORDERS_DIR, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            if any(k in line for k in ("Order ID", "Customer", "Date/Time", "TOTAL")):
                                print(f"  {line.rstrip()}")
                        print()
                print(f"  Total orders: {count}")

        elif choice == "0":
            print("\n  Admin logged out.")
            break

        else:
            print("  Invalid choice.")

        input("\n  Press Enter to continue...")
        clear_screen()


# ════════════════════════════════════════════════════════════
# Entry Point
# ════════════════════════════════════════════════════════════

def main():
    initialize_menu()

    while True:
        clear_screen()
        print("\n" + "=" * 55)
        print("        Welcome to EasyOrder")
        print("   A Python-Based Food Ordering Application")
        print("=" * 55)
        print("  1. Login")
        print("  2. Sign Up")
        print("  3. Continue as Guest")
        print("  4. Admin Login")
        print("  0. Exit")
        print()

        choice = input("  Enter choice: ").strip()

        if choice == "1":
            username = login()
            if username:
                clear_screen()
                customer_menu(username)

        elif choice == "2":
            username = sign_up()
            if username:
                clear_screen()
                customer_menu(username)

        elif choice == "3":
            print("\n  Continuing as Guest. Order history will not be saved.")
            input("  Press Enter to continue...")
            clear_screen()
            customer_menu("Guest")

        elif choice == "4":
            print("\n  -- Admin Login --")
            admin_user = input("  Username: ").strip()
            admin_pass = input("  Password: ").strip()
            if (admin_user, admin_pass) == ADMIN_CREDENTIALS:
                clear_screen()
                admin_menu()
            else:
                print("  Invalid admin credentials.")
                input("  Press Enter to continue...")

        elif choice == "0":
            print("\n  Thank you for using EasyOrder. Goodbye!\n")
            break

        else:
            print("  Invalid choice.")
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()
