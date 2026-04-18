# 🏔 Pahadi Kitchen

> **A Python + Flask web app for ordering authentic Himalayan food**
> Semester 2 Group Project — Sanskriti Singh & Kanika Sharma

**Live Demo → [pahadi-kitchen.onrender.com](https://pahadi-kitchen.onrender.com)**

---

## 📖 About

Pahadi Kitchen is a full-stack food ordering web application themed around the authentic cuisine of the Kumaon and Garhwal hills of Uttarakhand. Built entirely using Python and Flask as part of a Semester 2 programming project, it simulates a real-world restaurant ordering system — from browsing the menu to live order tracking with a fake delivery driver.

---

## ✨ Features

- 🔐 **User Authentication** — Sign up, login, guest mode
- 🍛 **Pahadi Menu** — 18 authentic dishes across 5 categories (Starters, Main Course, Breads, Desserts, Drinks)
- 🔍 **Search & Filter** — By keyword, category, or max price
- 🛒 **Shopping Cart** — Add, remove, update quantities
- 🧾 **Order & Bill** — Itemised bill with 5% GST, unique Order ID
- 📍 **Live Order Tracking** — Real-time status updates with animated mountain SVG map and fake driver card
- 📱 **SMS Notifications** — Order updates via Twilio (optional)
- 📋 **Order History** — View all past orders and bills
- ⚙️ **Admin Panel** — Manage menu, accept/decline orders, assign drivers, mark delivered

---

## 🗺 Order Flow

```
Customer places order
        ↓
Admin: Accept or Decline
        ↓ (if accepted)
Admin: Mark as Ready for Pickup
        ↓
Driver auto-assigned → Customer sees live tracking map
        ↓
Admin: Mark as Delivered
        ↓
Customer sees "Order Delivered" 🎉
```

---

## 🍽 The Menu

| Category | Dishes |
|---|---|
| 🥗 Starters | Aloo Ke Gutke, Bhatt ke Dubke, Singal Fritters, Til Chutney Platter |
| 🍛 Main Course | Kafuli, Chainsoo, Bhatt ki Churdkani, Gahat ki Dal, Thechwani, Pahadi Ras |
| 🫓 Breads | Mandua ki Roti, Jhangora Pulao |
| 🍮 Desserts | Bal Mithai, Singori, Jhangora ki Kheer |
| 🥤 Drinks | Buransh Sharbat, Chhachh, Kafal Sharbat |

---

## 🛠 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3, Flask |
| Frontend | Jinja2 templates, vanilla CSS & JS |
| Storage | Flat files (`.txt`, `.json`) — no database |
| Deployment | Render (free tier) |
| SMS | Twilio (optional) |

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/sanskriti-singh03/pahadi-kitchen.git
cd pahadi-kitchen

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. (Optional) Add Twilio credentials for SMS
cp .env.example .env
# edit .env with your keys

# 4. Run
python3 app.py
```

Open **`http://127.0.0.1:5001`** in your browser.

**Admin login:** `admin` / `admin123`

---

## 📁 Project Structure

```
pahadi-kitchen/
├── app.py               # Flask backend — all routes & logic
├── requirements.txt
├── Procfile             # For Render deployment
├── static/
│   ├── style.css        # All styles
│   └── script.js        # Cart controls, tab nav, flash dismiss
├── templates/
│   ├── base.html        # Navbar, flash messages, footer
│   ├── index.html       # Homepage with hero & features
│   ├── menu.html        # Menu with search/filter
│   ├── cart.html        # Cart & order summary
│   ├── bill.html        # Order confirmation receipt
│   ├── track.html       # Live order tracking page
│   ├── auth.html        # Login & Sign up
│   ├── history.html     # Order history
│   ├── view_order.html  # View individual past order
│   ├── admin.html       # Admin panel
│   └── admin_login.html
└── data/                # Auto-created at runtime (gitignored)
    ├── menu.txt
    ├── users.txt
    ├── order_history.txt
    ├── statuses.json
    └── orders/
```

---

## 👥 Team

| Member | Responsibilities |
|---|---|
| **Sanskriti Singh** | Shopping cart, order/billing, order history, admin panel |
| **Kanika Sharma** | User authentication, menu display, search & filter, report writing |
| **Both** | Error handling, testing, debugging, final integration, UI/UX |

---

## 📌 Notes

- No external database — all data stored in plain `.txt` and `.json` files
- No third-party UI libraries — pure CSS with CSS variables
- SMS is optional — app works fully without Twilio credentials
- Free Render tier sleeps after inactivity — first load may take ~30 seconds
